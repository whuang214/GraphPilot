"""The worked example is the only place the draft envelope is written down.

`diagram_get_authoring_contract` returned `example: null` for two of the three types, so a
host asked for an activity or use case diagram could not author a valid draft at all —
the single worst finding of the corpus run, reported independently by two cold hosts.

Promoting a curated answer key was tried first and abandoned: an answer key is
`conceptual`, so it cites nothing and carries no uncertainty, assumption or decision. It
would have taught the vocabulary and none of the honesty apparatus, which is precisely
where hosts went wrong — three of one host's four refusals came from `assumptions` alone.

So these examples are purpose-written, and these assertions keep them worth reading.
"""

import json
from pathlib import Path

from django.test import SimpleTestCase

from services.diagrams.catalog.diagram_types import SUPPORTED_DIAGRAM_TYPES
from services.diagrams.layout.diagram_layout_service import DiagramLayoutService
from services.diagrams.rendering.diagram_render_service import DiagramRenderService
from services.diagrams.validation.diagram_validation_service import DiagramValidationService
from services.drafts.authoring_contract_service import AuthoringContractService
from services.drafts.draft_validation_service import DraftValidationService
from services.materialization.canonical_assembly import assemble_canonical
from services.drafts.evidence_service import EvidenceService
from services.materialization.materializer import to_logical
from services.shared.workspace_storage_service import WorkspaceStorageService

#: The repository the worked examples cite. Skipped when the corpus is not checked out,
#: since it lives beside GraphPilot rather than inside it.
FIXTURE = Path(__file__).resolve().parents[3].parent / "GraphPilot-Test-Repos" / "todo-api-fixture"


def _examples():
    service = AuthoringContractService()
    return {t: service.build(t).get("example") for t in SUPPORTED_DIAGRAM_TYPES}


class WorkedExampleTests(SimpleTestCase):
    def test_every_diagram_type_has_one(self):
        missing = [t for t, example in _examples().items() if not example]
        self.assertEqual(missing, [])

    def test_each_is_a_draft_a_host_could_submit(self):
        service = DraftValidationService()
        for diagram_type, example in _examples().items():
            with self.subTest(diagram_type=diagram_type):
                findings = service.validate(example).findings
                self.assertEqual(
                    [f"{f.code} {f.path}" for f in findings], [],
                    "the shape we hand a host must be one we would accept from it",
                )

    def test_each_is_for_the_type_that_serves_it(self):
        for diagram_type, example in _examples().items():
            with self.subTest(diagram_type=diagram_type):
                self.assertEqual(example["diagramType"], diagram_type)

    def test_each_teaches_the_whole_envelope(self):
        """A field nobody demonstrates is a field hosts guess at.

        `evidence` carries the honesty rules, `requests` is required and length-checked,
        and `assurance: assumed` is meaningless without the `assumptions` entry it points
        at. Every one of these was a refusal or a reported gap in the corpus run.
        """
        for diagram_type, example in _examples().items():
            with self.subTest(diagram_type=diagram_type):
                self.assertEqual(example["authority"], "as_implemented",
                                 "a conceptual example cites nothing and teaches nothing")
                for section in ("evidence", "requests"):
                    self.assertTrue(example.get(section),
                                    f"{diagram_type} demonstrates no {section}")
                self.assertEqual(len(example["requests"]), 1,
                                 "an example is a create, and a create is asked for once")
                cited = {entry["id"] for entry in example["evidence"]}
                for item in example["elements"] + example["relationships"]:
                    for ref in item.get("evidenceRefs") or ():
                        self.assertIn(ref, cited)

    def test_an_assumed_item_always_points_at_its_assumption(self):
        for diagram_type, example in _examples().items():
            declared = {a["id"] for a in example.get("assumptions") or ()}
            for item in example["elements"] + example["relationships"]:
                if item["assurance"] != "assumed":
                    continue
                with self.subTest(diagram_type=diagram_type, item=item["id"]):
                    self.assertIn(item.get("assumptionRef"), declared)

    def test_every_top_level_field_appears_in_some_example(self):
        """The successor to a `decisions`-kind check, and a broader one.

        Hosts guess at whatever no example shows, so the bar is the envelope itself: every
        field the schema declares has to be demonstrated somewhere across the three.
        """
        from services.shared.schema_registry import SchemaRegistry

        declared = set(SchemaRegistry().get_schema("diagram_draft")["properties"])
        shown = {key for example in _examples().values() for key in example}

        # `basis` is written by `diagram_read` and refused from a host, and these examples
        # teach authoring a create — which is based on nothing. Showing it would model the
        # one field a host must never write.
        self.assertEqual(declared - shown - {"basis"}, set(),
                         "a top-level field no example shows is one hosts guess at")

    def test_each_materializes_into_a_diagram_that_validates_and_draws(self):
        """An example that cannot become a picture is advice we have never followed."""
        layout, validator = DiagramLayoutService(), DiagramValidationService()
        renderer = DiagramRenderService()
        for diagram_type, example in _examples().items():
            with self.subTest(diagram_type=diagram_type):
                diagram, _engine = assemble_canonical(
                    to_logical(example), diagram_type, example["diagramName"], "test", layout
                )
                result = validator.validate(diagram)
                self.assertTrue(
                    result.valid,
                    [i.message for i in result.issues if i.severity == "error"][:3],
                )
                self.assertIn("<svg", renderer.to_svg(diagram))

    def test_every_citation_points_at_a_real_repository(self):
        """The examples teach evidential honesty, so their own evidence has to be honest.

        They were first written against an invented service and cited
        `repositories/protocols.py`, `api/routes.py`, `permissions.can_edit` and
        `reminder_service.cancel_for` — none of which exist anywhere — with every line
        number made up. Nothing caught it, because `diagram_get_authoring_contract` never
        resolves a locator; only `diagram_create` does.

        They now cite `todo-api-fixture`, and this runs the same resolution a real create
        performs. A renamed symbol or a shifted line range fails here.
        """
        if not FIXTURE.is_dir():
            self.skipTest(f"corpus fixture not present at {FIXTURE}")
        evidence = EvidenceService(WorkspaceStorageService(str(FIXTURE)))
        for diagram_type, example in _examples().items():
            with self.subTest(diagram_type=diagram_type):
                resolution = evidence.resolve(example["evidence"])
                self.assertTrue(
                    resolution.valid,
                    [f"{f.code}: {f.message}" for f in resolution.findings][:3],
                )

    #: A worked example is judged on readability; the answers cover the vocabulary. The
    #: ceiling is per type because the notations are not comparable: a structure diagram
    #: says a lot with few edges, while a flow has to show its branches *and* rejoin them,
    #: so an activity with two decision points cannot be as small as a BDD and still be
    #: honest about what happens when a check fails.
    READABLE_SIZE = {"bdd_diagram": 16, "use_case_diagram": 20, "activity_diagram": 30}

    def test_each_is_short_enough_to_read(self):
        for diagram_type, example in _examples().items():
            with self.subTest(diagram_type=diagram_type):
                size = len(example["elements"]) + len(example["relationships"])
                self.assertLessEqual(
                    size, self.READABLE_SIZE[diagram_type], "too long to read in one go"
                )
                self.assertLessEqual(
                    len(json.dumps(example)), 12_000,
                    "the contract is read in full by a host before it authors anything",
                )
