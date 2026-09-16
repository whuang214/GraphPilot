"""The projection is only worth anything if it round-trips.

Read a saved diagram, project it back to a draft, materialize that draft, and the semantics
must survive. Every committed example is run through it, because a projection that works on
a hand-written fixture and loses something on a real 27-node activity diagram is a
projection that will lose someone's work.

What is *not* asserted is byte-equality with the original file. Class 2 and class 3 fields
— positions, styles, digests, timestamps — are deliberately absent from the projection and
come back by rule on the next write. Asserting they survive a bare materialize would be
asserting the design is something other than it is.
"""

import json
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from services.diagrams.layout.diagram_layout_service import DiagramLayoutService
from services.drafts.draft_projection_service import project
from services.drafts.draft_validation_service import DraftValidationService
from services.materialization.materializer import materialize

BLUEPRINTS = Path(settings.BASE_DIR) / "assets" / "blueprints"


def _committed():
    for path in sorted(BLUEPRINTS.glob("*/examples/*/*/output.gp.json")):
        yield path.parent.name, json.loads(path.read_text(encoding="utf-8"))


def _semantics(diagram):
    """Everything a draft is allowed to express, in a comparable shape."""
    return {
        "nodes": {
            node["id"]: {
                "semanticType": (node.get("data") or {}).get("semanticType"),
                "label": (node.get("data") or {}).get("label"),
                "stereotype": (node.get("data") or {}).get("stereotype"),
                "features": (node.get("data") or {}).get("features"),
                "parentId": node.get("parentId"),
                "assurance": (node.get("origin") or {}).get("assurance"),
                "evidenceRefs": (node.get("origin") or {}).get("evidenceRefs") or [],
            }
            for node in diagram["nodes"]
        },
        "edges": {
            edge["id"]: {
                "semanticType": (edge.get("data") or {}).get("semanticType"),
                "source": edge["source"],
                "target": edge["target"],
                "label": edge.get("label"),
                "guard": (edge.get("data") or {}).get("guard"),
                "condition": (edge.get("data") or {}).get("condition"),
                "extensionLocations": (edge.get("data") or {}).get("extensionLocations"),
                # Ends are the field the first version of this test did not compare, and
                # the projection was reading them from the wrong level — so every role,
                # multiplicity and navigability on every edge was silently dropped and
                # nothing failed. A round trip that does not compare a field does not
                # protect it.
                "sourceEnd": (edge.get("data") or {}).get("sourceEnd"),
                "targetEnd": (edge.get("data") or {}).get("targetEnd"),
                "assurance": (edge.get("origin") or {}).get("assurance"),
            }
            for edge in diagram["edges"]
        },
        "authority": diagram["metadata"].get("authority"),
        "requests": [r["text"] for r in diagram["metadata"].get("requests") or ()],
    }


#: The only difference allowed between an authored draft and the projection of the diagram
#: it produced. An empty optional array is written out by some hand-authored drafts and
#: omitted by the projection, because the contract tells hosts to leave out what does not
#: apply — and `evidence: []` on a conceptual diagram would be a claim rather than a blank.
_EMPTY_OPTIONALS = ("evidence", "assumptions")


def _comparable(draft):
    out = {key: value for key, value in draft.items() if key != "basis"}
    for key in _EMPTY_OPTIONALS:
        if out.get(key) == []:
            del out[key]
    return out


class ProjectingGivesBackTheAuthoredDraftTests(SimpleTestCase):
    """`project(materialize(draft))` must equal `draft`.

    The strongest statement available about the projection, and the reason it is worth
    having beside the semantic comparison below: **there is no allowlist to forget.**

    The test underneath this one compares a hand-written list of fields, and that is
    precisely how the projection shipped reading relationship ends from the wrong level —
    every role, multiplicity and navigability was dropped, and the comparison could not see
    it because nobody had listed those fields. A whole-document equality has nothing to
    leave out.

    A difference here is one of two things, and both are worth failing over: a field the
    projection loses, or a normalisation the materializer performs that nobody wrote down.
    """

    def test_every_committed_draft_survives_the_round_trip(self):
        for name, diagram in _committed():
            draft_path = BLUEPRINTS.glob(f"*/examples/*/{name}/draft.json")
            source = next(draft_path, None)
            if source is None:
                continue
            with self.subTest(example=name):
                authored = json.loads(source.read_text(encoding="utf-8"))
                self.assertEqual(_comparable(authored), _comparable(project(diagram)))

    def test_the_only_tolerated_difference_is_an_empty_optional(self):
        """Named so the exemption cannot quietly grow. If a third key needs adding here,
        that is a finding about the projection, not a fixture detail."""
        self.assertEqual(_EMPTY_OPTIONALS, ("evidence", "assumptions"))


class EveryCommittedDiagramRoundTripsTests(SimpleTestCase):
    def setUp(self):
        self.layout = DiagramLayoutService()

    def test_the_projection_of_every_committed_diagram_is_a_valid_draft(self):
        """Minus the one row the host must append — so it is valid except for `requests`,
        which the write supplies. Everything else has to stand on its own.

        Projected **with a basis**, because that is the only way a projection ever exists:
        `diagram_read` stamps one on every call. Without it the validator reads the
        document as a create and refuses a `user` element — correctly, since a host may
        not author one — and the first version of this test therefore failed the moment a
        committed example contained something a person had drawn.
        """
        service = DraftValidationService()
        stamp = {"diagram": "sha256:" + "0" * 64, "readAt": "2026-01-01T00:00:00Z"}
        for name, diagram in _committed():
            with self.subTest(example=name):
                draft = project(diagram, basis=stamp)
                # The projection deliberately appends nothing; a create needs exactly one
                # ask, so give it the one it was made with to check the rest of the shape.
                draft["requests"] = draft["requests"][:1] or ["Draw it."]
                result = service.validate(draft)
                self.assertTrue(
                    result.valid,
                    [f"{f.code} {f.path} {f.message}" for f in result.findings][:4],
                )

    def test_materializing_the_projection_preserves_every_semantic_field(self):
        for name, diagram in _committed():
            with self.subTest(example=name):
                draft = project(diagram)
                draft["requests"] = draft["requests"] or ["Draw it."]
                digests = {
                    record["id"]: record["contentDigest"]
                    for record in diagram["metadata"].get("evidence") or ()
                }
                rebuilt, _ = materialize(
                    draft, evidence_digests=digests, layout_service=self.layout
                )
                self.assertEqual(_semantics(rebuilt), _semantics(diagram))

    def test_no_geometry_reaches_the_draft(self):
        """The host must not be able to author a position, so it must not be shown one.

        This is the whole reason a person's arrangement survives an edit: the field never
        makes the round trip, so there is nothing for a host to overwrite.

        Checked as keys at each level rather than as substrings — a property's `type`
        (`"str"`, `"datetime"`) is a legitimate part of `features`, and a blanket search
        for the word cannot tell it from a node's renderer `type`.
        """
        banned = {
            "position", "width", "height", "style", "route", "viewport",
            "sourceHandle", "targetHandle", "type", "rationale", "schemaRules",
            "contentDigest", "createdAt", "updatedAt", "origin", "metadata", "data",
        }
        for name, diagram in _committed():
            draft = project(diagram)
            with self.subTest(example=name):
                self.assertEqual(banned & set(draft), set())
                for section in ("elements", "relationships"):
                    for item in draft[section]:
                        self.assertEqual(banned & set(item), set(), item.get("id"))
                for record in draft.get("evidence") or ():
                    self.assertEqual(banned & set(record), set(), record["id"])
                    self.assertNotIn("contentDigest", record)


class WhatTheProjectionCarriesTests(SimpleTestCase):
    def _diagram(self, **metadata):
        return {
            "schemaVersion": "graphpilot.diagram.v1",
            "kind": "diagram",
            "diagramType": "bdd_diagram",
            "id": "diagram_x",
            "name": "x",
            "metadata": {"authority": "conceptual", **metadata},
            "viewport": {"x": 0, "y": 0, "zoom": 1},
            "nodes": [{
                "id": "a", "type": "gpNode",
                "position": {"x": 10, "y": 20}, "width": 200, "height": 90,
                "style": {"background": "#fff"},
                "data": {"label": "A", "semanticType": "block", "description": "typed by a person"},
                "origin": {"assurance": "conceptual", "evidenceRefs": [],
                           "assumptionRefs": [], "schemaRules": [], "rationale": "r"},
            }],
            "edges": [],
        }

    def test_the_request_log_is_flattened_to_text(self):
        diagram = self._diagram(requests=[
            {"at": "2026-08-01T00:00:00Z", "text": "First ask."},
            {"at": "2026-08-02T00:00:00Z", "text": "Second ask."},
        ])

        self.assertEqual(project(diagram)["requests"], ["First ask.", "Second ask."])

    def test_nothing_is_appended_to_the_request_log(self):
        """The document is a valid draft minus exactly one row, and that row is the thing
        the host is about to do. It cannot write without saying why."""
        diagram = self._diagram(requests=[{"at": "2026-08-01T00:00:00Z", "text": "Only."}])

        self.assertEqual(len(project(diagram)["requests"]), 1)

    def test_a_typed_description_is_not_emitted_and_therefore_cannot_be_lost(self):
        """`data.description` is class 2: the host did not write it, so it is copied back
        by id rather than shown. Emitting it would let a host drop it by omission."""
        self.assertNotIn("description", json.dumps(project(self._diagram())))

    def test_basis_rides_in_the_file_rather_than_being_asked_for(self):
        stamp = {"diagram": "sha256:abc", "readAt": "2026-08-05T12:00:00Z"}

        self.assertEqual(project(self._diagram(), basis=stamp)["basis"], stamp)

    def test_a_diagram_with_no_origins_projects_as_conceptual(self):
        """Diagrams written before origins existed still have to be editable."""
        diagram = self._diagram()
        del diagram["nodes"][0]["origin"]

        self.assertEqual(project(diagram)["elements"][0]["assurance"], "conceptual")

    def test_an_empty_optional_is_omitted_rather_than_sent_back_blank(self):
        """`"stereotype": ""` is a value nobody authored, and the contract tells hosts to
        omit what the source does not establish."""
        self.assertNotIn("stereotype", project(self._diagram())["elements"][0])
