"""The contract is derived, so it cannot tell a host one thing and refuse it for another."""

import json
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from services.diagrams.catalog.diagram_types import SUPPORTED_DIAGRAM_TYPES, get_type_profile
from services.drafts.authoring_contract_service import (
    _DIRECTION,
    _ENVELOPE,
    _scoped_relationship_fields,
    REFUSAL_GUIDE,
    AuthoringContractService,
)
from services.drafts.draft_contract import END_POLICY, scoped_element_fields
from services.drafts.draft_validation_service import DraftValidationService
from services.diagrams.validation.validation_contract import ValidationCode
from services.shared.schema_registry import SchemaRegistry


def _scoped_fields(diagram_type: str, section: str) -> frozenset:
    """Fields this type may not author in *section* — the contract's own filter."""
    if section == "element":
        return scoped_element_fields(diagram_type)
    if section == "relationship":
        return _scoped_relationship_fields(get_type_profile(diagram_type))
    return frozenset()


def _payload(service, diagram_type: str) -> str:
    """Everything that reaches a host for *diagram_type*.

    `content` is now a short orientation summary and the contract itself travels as
    `structuredContent`, so a test that asserts a fact reaches the host must look at
    both. Searching the serialized contract keeps every finding these tests encode
    pinned to the channel that now carries it.
    """
    contract = service.build(diagram_type)
    return service.render_summary(contract) + json.dumps(contract, ensure_ascii=False)


class AuthoringContractServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = AuthoringContractService()

    def test_every_supported_type_has_a_contract(self):
        self.assertEqual(set(self.service.supported_types()), set(SUPPORTED_DIAGRAM_TYPES))
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            with self.subTest(diagram_type=diagram_type):
                self.assertEqual(self.service.build(diagram_type)["contractFor"], diagram_type)

    def test_an_unsupported_type_is_refused(self):
        with self.assertRaises(ValueError):
            self.service.build("sequence_diagram")

    # ---- derivation, not duplication ---------------------------------------------

    def test_the_vocabulary_is_exactly_the_type_profile(self):
        """A hand-written list would drift from what the validator accepts."""
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            with self.subTest(diagram_type=diagram_type):
                contract = self.service.build(diagram_type)
                profile = get_type_profile(diagram_type)
                self.assertEqual(
                    {item["semanticType"] for item in contract["vocabulary"]["elements"]},
                    set(profile.allowed_node_semantic_types),
                )
                self.assertEqual(
                    {item["semanticType"] for item in contract["vocabulary"]["relationships"]},
                    set(profile.allowed_edge_semantic_types),
                )

    def test_top_level_fields_come_from_the_draft_schema(self):
        rows = self.service.build("bdd_diagram")["topLevelFields"]
        self.assertEqual(
            sorted(f for f, r in rows.items() if r["required"] == "yes"),
            ["authority", "diagramName", "diagramType", "elements", "kind",
             "relationships", "requests", "schemaVersion"],
        )
        self.assertEqual(
            sorted(f for f, r in rows.items() if r["required"] == "no"),
            ["assumptions", "basis"],
        )
        self.assertEqual(rows["evidence"]["required"], "if `as_implemented`")
        self.assertEqual(rows["elements"]["array"], "yes")
        self.assertEqual(rows["requests"]["array"], "yes")
        self.assertEqual(rows["diagramType"]["array"], "no")

    def test_guidance_is_sectioned_and_loses_nothing(self):
        """It shipped as one 1,759-character string holding a whole Markdown document.

        A cold host reading the JSON channel had its reader truncate that value and could
        not recover it by line, because the document was one line — and what it lost
        included "prefer the weaker true relationship", the rule that decided five of its
        seven edges. Sections truncate gracefully.

        The second assertion is the one that matters: sectioning must not drop anything.
        The first attempt kept a section's table and silently discarded the paragraph
        beside it, which is the exact defect class this program keeps finding.
        """
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            source = (
                Path(settings.BASE_DIR) / "assets" / "blueprints" / diagram_type / "authoring.md"
            ).read_text(encoding="utf-8")
            sections = self.service.build(diagram_type)["guidance"]
            blob = json.dumps(sections, ensure_ascii=False)
            with self.subTest(diagram_type=diagram_type):
                self.assertIsInstance(sections, list)
                self.assertTrue(all("heading" in s for s in sections))
                self.assertNotIn("| ---", blob, "a pipe table survived as raw Markdown")
                for line in source.splitlines():
                    line = line.strip()
                    if not line or line.startswith(("#", "|")):
                        continue
                    fragment = line.lstrip("- ").strip()
                    # Wrapped lines are rejoined, so match on the first clause.
                    head = fragment.split(",")[0].split(".")[0].strip()
                    if len(head) > 12:
                        self.assertIn(head, blob, f"guidance lost: {head!r}")

    def test_relationship_end_fields_name_the_relationships_that_allow_them(self):
        """The rule lived only in `vocabulary.relationships[].ends`, a prose string on a
        nested array item hundreds of lines from `sourceRole`. A cold host skipped those
        items as "the vocabulary blurb" and said it avoided an illegal end on a dependency
        only because the file it was diagramming stated the same rule — "that is luck"."""
        contract = self.service.build("bdd_diagram")
        rows = {r["field"]: r for r in contract["envelope"]["relationship"]["fields"]}
        # A BDD dependency forbids a source end and allows a target one.
        self.assertIn("`composition`", rows["sourceRole"]["note"])
        self.assertNotIn("`dependency`", rows["sourceRole"]["note"])
        self.assertIn("`dependency`", rows["targetRole"]["note"])
        self.assertIn("notation_invalid", rows["sourceMultiplicity"]["note"])

    def test_semantic_type_offers_only_what_this_type_allows(self):
        """The field a host reads while authoring listed all twelve semantic types across
        all three diagram types, and deferred to the validator for the real set — a tool
        call for something sitting a few keys away. A cold host named it as the wrong list
        closest to the work: the shape advertised values that earn
        `semantic_type_unsupported`."""
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            contract = self.service.build(diagram_type)
            for section, key in (("element", "elements"), ("relationship", "relationships")):
                allowed = {i["semanticType"] for i in contract["vocabulary"][key]}
                row = next(
                    r for r in contract["envelope"][section]["fields"]
                    if r["field"] == "semanticType"
                )
                with self.subTest(diagram_type=diagram_type, section=section):
                    offered = set(re.findall(r"`([A-Za-z]+)`", row["shape"]))
                    self.assertEqual(offered, allowed)

    def test_containers_are_named_per_type(self):
        self.assertEqual(self.service.build("use_case_diagram")["vocabulary"]["containers"], ["subject"])
        self.assertEqual(self.service.build("bdd_diagram")["vocabulary"]["containers"], [])

    # ---- the rules a host most often gets wrong -----------------------------------

    def test_composition_asks_for_the_part_role_and_never_mentions_aggregation(self):
        """The diamond comes from the type; asking for aggregation would double it."""
        relationships = {
            item["semanticType"]: item
            for item in self.service.build("bdd_diagram")["vocabulary"]["relationships"]
        }
        self.assertEqual(relationships["composition"]["direction"], "part → whole")
        self.assertIn("part's role", relationships["composition"]["ends"])
        self.assertEqual(relationships["generalization"]["ends"], "none")
        self.assertNotIn("source", relationships["dependency"]["ends"])

        prose = _payload(self.service, "bdd_diagram")
        self.assertNotIn("aggregation", prose)

    def test_include_and_extend_directions_are_stated_and_opposite(self):
        relationships = {
            item["semanticType"]: item
            for item in self.service.build("use_case_diagram")["vocabulary"]["relationships"]
        }
        self.assertEqual(relationships["include"]["direction"], "base → included")
        self.assertEqual(relationships["extend"]["direction"], "extension → base")

    def test_control_flow_advertises_its_guard(self):
        relationships = {
            item["semanticType"]: item
            for item in self.service.build("activity_diagram")["vocabulary"]["relationships"]
        }
        self.assertIn("guard", relationships["controlFlow"]["ends"])

    # ---- the worked example must actually work ------------------------------------

    def test_the_envelope_answers_every_gap_the_cold_hosts_hit(self):
        """One row per finding from the `E2` run.

        The contract used to point at a "draft contract" document that does not exist, so
        the worked example was the only place the envelope was written down. Three fresh
        hosts guessed; one spent three of its four refusals on `assumptions` alone. Each
        assertion below is a place a competent agent had to guess, and the fix is the same
        for all of them: derive the field tables from the schema instead of describing it.
        """
        service = AuthoringContractService()
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            prose = _payload(service, diagram_type)
            with self.subTest(diagram_type=diagram_type):
                # f6 — the enums were unobtainable; all three hosts guessed. The second
                # enum this checked belonged to `request.detailLevel`, which no longer
                # exists; `evidence.kind` below covers the same ground.
                self.assertIn("`as_implemented`", prose)
                # f7 — every required field of an assumption, and the pairing rule.
                for field in ("acceptedBy", "statement", "reason"):
                    self.assertIn(field, prose)
                self.assertIn("`host` or `user`", prose)
                # f8 — one unknown key produced 12 of 13 findings in a single refusal.
                for key in ("parentId", "evidenceRefs"):
                    self.assertIn(key, prose)
                # f13 — enums shown by example only.
                self.assertIn("`configuration`", prose)
                # f14 — relationships carry evidence exactly as elements do.
                self.assertIn("Relationships carry evidence", prose)
                # f16 — a mis-rooted path silently mis-digests.
                self.assertIn("Workspace-relative", prose)

    def test_a_type_scoped_field_is_documented_only_where_it_is_authorable(self):
        """The other half of f8, now per type.

        `stereotype`, `features` and `extensionPoints` belong to one diagram type each. An
        activity contract used to carry all three — plus a whole `features` section whose
        own purpose line read "BDD only" — so the surface taught vocabulary the validator
        refuses. `f9`/`f11` moved with them: "unbounded" and "unlike `properties`" describe
        multiplicity and compartments, which only their owning types can author.

        Asserted against the element field table rather than the whole prose: the refusal
        guide still names `stereotype`, and rightly — an activity draft carrying one is
        refused, so that rule is reachable and belongs in the contract. What must not
        appear is the field offered as something to author.
        """
        service = AuthoringContractService()
        owner = {
            "stereotype": "bdd_diagram",
            "features": "bdd_diagram",
            "extensionPoints": "use_case_diagram",
        }
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            offered = {
                row["field"]
                for row in service.build(diagram_type)["envelope"]["element"]["fields"]
            }
            for field, owning_type in owner.items():
                with self.subTest(diagram_type=diagram_type, field=field):
                    if diagram_type == owning_type:
                        self.assertIn(field, offered)
                    else:
                        self.assertNotIn(field, offered)
        # f9 and f11 stay proven, on the types that can reach them.
        self.assertIn("unbounded", _payload(service, "bdd_diagram"))
        self.assertIn("unlike `properties`", _payload(service, "bdd_diagram"))

    def test_an_activity_contract_drops_the_sections_it_cannot_author(self):
        """18% of an activity envelope described BDD block compartments."""
        service = AuthoringContractService()
        activity = set(service.build("activity_diagram")["envelope"])
        self.assertEqual(activity & {"features", "property", "operation", "constraint"}, set())
        # No activity relationship carries an end and it has no properties, so nothing in
        # one can hold a multiplicity.
        self.assertNotIn("multiplicity", activity)
        # A use case association does carry ends, so it keeps it.
        self.assertIn("multiplicity", service.build("use_case_diagram")["envelope"])

    def test_every_relationship_states_its_direction(self):
        """`direction` cannot be derived: END_POLICY records whether an end may carry a
        role, not which end is the part. It is the highest-consequence field in the
        contract — a composition authored backwards validates cleanly and asserts the
        opposite ownership — so it is pinned here instead."""
        self.assertEqual(sorted(END_POLICY), sorted(_DIRECTION))

    def test_nothing_the_contract_points_at_is_missing_from_it(self):
        """A cold host given one channel had to guess two values on the critical path.

        It invented `kind`, whose literal value appeared nowhere, and the shape of
        `lineRange`, which `locator` cross-referenced and nothing defined. Both fail
        closed as `draft_invalid`, which suppresses every other finding, so the single
        refusal could not say which guess was wrong.

        The generic guard is the valuable half: an `object — see X` shape must resolve to
        a section the same response carries.
        """
        service = AuthoringContractService()
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            contract = service.build(diagram_type)
            payload = _payload(service, diagram_type)
            with self.subTest(diagram_type=diagram_type):
                self.assertIn("Always `graphpilot.draft.v1`", payload)
                self.assertIn("Always `diagramDraft`", payload)
                for section in contract["envelope"].values():
                    for row in section["fields"]:
                        referenced = re.findall(r"object — see `([A-Za-z]+)`", row["shape"])
                        for name in referenced:
                            self.assertIn(
                                name, contract["envelope"],
                                f"`{name}` is cross-referenced and never defined",
                            )

    def test_a_host_that_cannot_see_the_contract_is_told_to_stop(self):
        """`content` is orientation; `structuredContent` is the contract.

        That split is what the MCP specification pictures — its own example pairs a
        one-line `content` with a full record set — and `content` cannot simply be
        dropped instead, because the spec marks it required and `structuredContent`
        optional.

        The cost is a real failure mode: a client that does not surface
        `structuredContent` leaves a host holding orientation and nothing to author from.
        Left alone that fails silently, because orientation reads like guidance. So the
        summary names the field it depends on and tells a host to report rather than
        guess — the same reasoning as `content_lost`, where a defect the host cannot
        author around is reported instead of absorbed.
        """
        service = AuthoringContractService()
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            contract = service.build(diagram_type)
            summary = service.render_summary(contract)
            with self.subTest(diagram_type=diagram_type):
                self.assertIn("structuredContent", summary)
                self.assertIn("stop and say so", summary)
                # Orientation only — the summary must not try to become the contract.
                self.assertLess(len(summary), 1200)
                # And the contract it points at really does carry the example.
                self.assertIsNotNone(contract["example"])
                self.assertEqual(
                    contract["example"]["diagramType"], diagram_type
                )

    def test_no_top_level_field_points_at_a_table_that_does_not_exist(self):
        """A row with no description of its own fell through to *"see the field table for
        `basis`"* — and only the repeated structures have a field table, so a host chased a
        section that was never going to be there. It reported the dead end.

        The cause was `$ref`: the property carries no description, the definition does, and
        nothing resolved one to the other.
        """
        contract = self.service.build("bdd_diagram")
        described = {"element", "relationship", "evidence", "assumption"}
        for field, row in contract["topLevelFields"].items():
            with self.subTest(field=field):
                if "field table" in row["note"]:
                    self.assertIn(
                        field.rstrip("s"), described,
                        f"`{field}` points at a field table nothing publishes",
                    )

    def test_the_basis_row_explains_the_field_rather_than_deferring(self):
        row = self.service.build("bdd_diagram")["topLevelFields"]["basis"]

        self.assertIn("never authored", row["note"])
        self.assertEqual(row["required"], "no", "a create is based on nothing")

    def test_the_request_rule_covers_editing_as_well_as_creating(self):
        """The refusal table was written as if `diagram_create` were the only caller, so it
        said a draft carries exactly one ask — which an update contradicts, and a host
        stopped to re-read before trusting the table."""
        rule = dict(REFUSAL_GUIDE)["requests_invalid"]

        self.assertIn("create", rule)
        self.assertIn("edit", rule)

    def test_the_edit_refusals_are_explained_like_every_other(self):
        """`basis_stale` fired on a host that had been told the behaviour three times in
        prose and could still not find the code in the table it greps."""
        codes = dict(REFUSAL_GUIDE)

        self.assertIn("basis_stale", codes)
        self.assertIn("diagram_crossed", codes)

    def test_a_conditionally_required_field_does_not_report_itself_optional(self):
        """`evidence` is absent from the schema's `required`, and `evidence_required`
        refuses an `as_implemented` draft that cites nothing. A flat "no" is a lie a host
        can act on."""
        rows = self.service.build("bdd_diagram")["topLevelFields"]
        self.assertEqual(rows["evidence"]["required"], "if `as_implemented`")
        self.assertEqual(rows["assumptions"]["required"], "no")

    def test_a_guard_says_who_draws_the_brackets(self):
        """f17. The renderer wraps a guard in `[...]`, so an author who brackets it ships
        `[[stock ok]]` and nothing tells them until they look at the picture."""
        service = AuthoringContractService()
        prose = _payload(service, "activity_diagram")
        self.assertIn("GraphPilot draws the surrounding brackets", prose)

    def test_the_contract_points_at_no_document_that_does_not_exist(self):
        """f6 was a dangling pointer: *"See the `request` section of the draft contract"*.
        No tool returns such a document, and the phrase read like it was fetchable."""
        service = AuthoringContractService()
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            contract = service.build(diagram_type)
            blob = json.dumps(contract) + service.render_summary(contract)
            with self.subTest(diagram_type=diagram_type):
                self.assertNotIn("section of the draft contract", blob)

    def test_every_envelope_field_is_derived_from_the_schema(self):
        """Prose beside a schema drifts from it. `A4` audits for exactly this, so the
        contract must not gain a hand-written field table."""
        schema = SchemaRegistry().get_schema("diagram_draft")
        service = AuthoringContractService()
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            contract = service.build(diagram_type)
            for name, section in contract["envelope"].items():
                scoped_out = _scoped_fields(diagram_type, name)
                described = {row["field"] for row in section["fields"]}
                actual = set(schema["$defs"][name].get("properties") or {}) - scoped_out
                with self.subTest(diagram_type=diagram_type, section=name):
                    self.assertEqual(described, actual)
                    required = {r["field"] for r in section["fields"] if r["required"] == "yes"}
                    self.assertEqual(
                        required, set(schema["$defs"][name].get("required") or ()) - scoped_out
                    )

    def test_the_trim_is_lossless_in_both_directions(self):
        """The whole safety argument for a per-type contract, in one place.

        Nothing the validator **accepts** for a type may be missing from that type's
        contract, and nothing the contract documents may be something the validator
        **refuses**. A trim that fails either direction has stopped being a trim.
        """
        schema = SchemaRegistry().get_schema("diagram_draft")
        service = AuthoringContractService()
        every_section = {name for name, _purpose in _ENVELOPE}
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            contract = service.build(diagram_type)
            documented = {
                (name, row["field"])
                for name, section in contract["envelope"].items()
                for row in section["fields"]
            }
            authorable = {
                (name, field)
                for name in every_section
                for field in (schema["$defs"][name].get("properties") or {})
                if field not in _scoped_fields(diagram_type, name)
            }
            # Sections dropped whole are only legitimate when nothing reaches them.
            unreachable = {
                (name, field)
                for name, field in authorable
                if name not in contract["envelope"]
            }
            with self.subTest(diagram_type=diagram_type):
                self.assertEqual(
                    documented - authorable, set(),
                    "the contract documents a field this type may not author",
                )
                self.assertEqual(
                    authorable - documented - unreachable, set(),
                    "this type may author a field the contract never mentions",
                )
                # Every top-level draft field is named — optional ones and the two
                # constants included, since the section declares itself exhaustive.
                self.assertEqual(set(contract["topLevelFields"]), set(schema["properties"]))

    def test_the_top_level_arrays_are_named_outside_the_example(self):
        """`assumptions` used to appear only inside the worked example — the one part of
        the contract the Markdown channel never carried. `orphan_assumption` refuses a
        draft that does not reference an assumption, so a host had to learn the array's
        name from a place its client might not render.

        `requests` joins it for the same reason and a sharper one: it is required, its
        length is checked, and a host that never sees it named cannot supply it at all."""
        service = AuthoringContractService()
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            prose = _payload(service, diagram_type)
            with self.subTest(diagram_type=diagram_type):
                for field in ("assumptions", "evidence", "requests"):
                    self.assertIn(f"`{field}`", prose)

    def test_every_refusal_code_is_explained_before_a_host_trips_it(self):
        """`A4`. A rule a host can only learn by failing is a rule we have not stated.

        `orphan_evidence` was a hard refusal explained nowhere, and all three cold hosts
        discovered it the same way — by being refused. Auditing for the pattern found
        **14 of 19** refusal codes in that state.

        This reads the codes out of the services rather than from a list beside them, so
        adding a refusal without explaining it fails here instead of in front of a host.
        """
        codes = set()
        for module in (
            "services/drafts/draft_validation_service.py",
            "services/drafts/evidence_service.py",
            "services/materialization/diagram_creation_service.py",
            "mcp_server/server.py",
        ):
            text = (Path(settings.BASE_DIR) / module).read_text(encoding="utf-8")
            codes |= set(re.findall(r'DraftFinding\(\s*\n?\s*"([a-z_]+)"', text))
            codes |= set(re.findall(r'DraftRefused\(\s*"([a-z_]+)"', text))
            codes |= set(re.findall(r'"code":\s*"([a-z_]+)"', text))
            codes |= set(re.findall(r'_error\(\s*\n?\s*"([a-z_]+)"', text))

        # `schema_*` is generated per jsonschema keyword and carries its rule in its own
        # message. The rest below are **transport** failures: a malformed call, a path
        # outside the workspace, a bug on our side. They are not things a well-formed
        # draft can be refused for, so a host cannot avoid them by authoring differently
        # and the contract has nothing useful to say in advance.
        transport = {
            "unsafe_path", "unsupported_diagram_type", "schema_unavailable",
            "invalid_diagram", "render_failed", "unexpected_error", "workspace_missing",
            "diagram_not_found", "invalid_request", "internal_error", "invalid_arguments",
            "invalid_diagram_json", "workspace_resolution_error", "unreadable_diagram",
            "unwritable_diagram", "invalid_workspace", "validation_unavailable",
        }
        codes = {c for c in codes if not c.startswith("schema_") and c not in transport}

        # Canonical validation's warnings reach a host too — through `diagram_create`'s
        # `operationWarnings` and now through `diagram_check_draft`. They are emitted as
        # `ValidationCode` members rather than `DraftFinding`, so the greps above never
        # saw them, and `structural_constraint` sat undocumented until a host met it and
        # reported "a third warning code in no table I was given". The hole was in this
        # test, not in the guide.
        codes |= {
            ValidationCode.STRUCTURAL_CONSTRAINT.value,
            ValidationCode.LONG_LABEL.value,
            ValidationCode.LABEL_TRUNCATED.value,
        }

        explained = {code for code, _rule in REFUSAL_GUIDE}
        self.assertEqual(
            sorted(codes - explained), [],
            "these can refuse a draft and no contract explains them",
        )

    def test_every_bounded_field_states_its_bound(self):
        """A cold host wrote a 271-character label and was refused `schema_maxLength`.

        The field said `shape: "short text"`. "Short" is not a number, the limit lived
        only in the schema, and `schema_*` is deliberately absent from the refusal table —
        so the one rule that refused it was stated in neither of the two places a host
        reads. Bounds are derived from the schema here, so this cannot drift.
        """
        schema = SchemaRegistry().checked_schema("diagram_draft")
        defs = schema.get("$defs") or {}
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            contract = self.service.build(diagram_type)
            for section in ("element", "relationship"):
                for row in contract["envelope"][section]["fields"]:
                    spec = ((defs.get(section) or {}).get("properties") or {}).get(
                        row["field"]
                    ) or {}
                    ref = str(spec.get("$ref") or "").rsplit("/", 1)[-1]
                    target = defs.get(ref) or spec
                    cap = target.get("maxLength") or spec.get("maxItems")
                    if not cap or target.get("enum"):
                        continue
                    with self.subTest(type=diagram_type, field=row["field"]):
                        self.assertIn(
                            str(cap), row["shape"],
                            f"{row['field']} is capped at {cap} and does not say so",
                        )

    def test_the_extend_fields_are_published_as_conditionally_required(self):
        """Both said `required: no` while the structural critic refused an `extend` that
        named no location. A host omitted them obeying "prefer omission to a guess", was
        refused, and complied by inventing a point name its source never used — "the rule
        pushed me across the exact line the honesty rules drew"."""
        contract = self.service.build("use_case_diagram")
        rel = {r["field"]: r for r in contract["envelope"]["relationship"]["fields"]}
        el = {r["field"]: r for r in contract["envelope"]["element"]["fields"]}
        self.assertNotEqual(rel["extensionLocations"]["required"], "no")
        self.assertNotEqual(el["extensionPoints"]["required"], "no")
        # And it must tell a host what to do when the source names no point, or it has
        # merely moved the fabrication one step earlier.
        self.assertIn("do not invent", rel["extensionLocations"]["note"])
        self.assertIn("reply to the user", rel["extensionLocations"]["note"])

        # The escape hatch must not name a field that does not exist. This note used to
        # end "record what you could not establish in `uncertainties`" — and all three
        # hosts in corpus run 5 reported it independently, because the backticks make it
        # read as a schema field. A host that needed it would have authored an unknown
        # key and been refused for following the contract.
        declared = set(self.service.build("use_case_diagram")["topLevelFields"])
        for row in rel.values():
            for word in re.findall(r"`(\w+)`", row.get("note") or ""):
                if word.endswith("s") and word not in declared and word.islower():
                    self.assertNotIn(
                        word, {"uncertainties", "decisions"},
                        f"`{word}` is not a draft field and the note names it as one",
                    )

    def test_the_end_fields_say_they_are_drawn_as_one_label(self):
        """A host authored `sourceRole` and `sourceMultiplicity` inside their documented
        limits and watched `payments_received 0..*` collide with two node labels. The
        renderer joins them with a space; the contract described them separately and never
        said so, so the length that had to fit was one no field stated."""
        rows = {
            r["field"]: r
            for r in self.service.build("bdd_diagram")["envelope"]["relationship"]["fields"]
        }
        for field in ("sourceRole", "sourceMultiplicity", "targetRole", "targetMultiplicity"):
            with self.subTest(field=field):
                self.assertIn("one label", rows[field]["note"])
        # Navigability is not part of that label, so it must not claim to be.
        self.assertNotIn("one label", rows["targetNavigable"]["note"])

    def test_no_end_field_contradicts_itself_about_its_scope(self):
        """`sourceNavigable` read "**Association only.** … Only on `association`,
        `composition`" — two different rules in one sentence, and `targetNavigable` named
        a third scope. A host played safe, used navigability on associations only, and
        said the contradiction cost it a decision it should not have had to make."""
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            rows = self.service.build(diagram_type)["envelope"]["relationship"]["fields"]
            for row in rows:
                if not row["field"].endswith(("Role", "Multiplicity", "Navigable")):
                    continue
                with self.subTest(type=diagram_type, field=row["field"]):
                    # The scope is derived from END_POLICY; no hand-written scope may
                    # sit beside it saying something narrower.
                    self.assertNotIn("Association only", row["note"])

    def test_the_summary_lets_a_host_detect_a_truncated_contract(self):
        """"Can you see `structuredContent`?" is a yes that a host reading 60% of it
        answers honestly and wrongly. Two hosts had this payload truncated by their
        terminal. A key count and a key list are checkable; a yes/no is not."""
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            contract = self.service.build(diagram_type)
            prose = _payload(self.service, diagram_type)
            with self.subTest(diagram_type=diagram_type):
                self.assertIn(f"{len(contract)} top-level keys", prose)
                self.assertIn(f"{len(contract['envelope'])} sections", prose)

    def test_stereotype_says_it_is_free_text_and_who_adds_the_guillemets(self):
        """Four hosts across two runs reported having no idea what values are legal. One
        avoided the field entirely — "a feature the contract talked me out of using" —
        and another guessed `«control»`, which renders as `««control»»` because the
        renderer adds the guillemets itself."""
        rows = {
            r["field"]: r
            for r in self.service.build("bdd_diagram")["envelope"]["element"]["fields"]
        }
        note = rows["stereotype"]["note"]
        self.assertIn("Free text", note)
        self.assertIn("guillemets", note)
        self.assertIn("«service»", note)

    def test_the_top_level_rows_state_their_limits_too(self):
        """`diagramName` is the one value a host cannot change afterwards, and its shape —
        a slug of at most 64 characters — appeared nowhere. The array caps were equally
        invisible: 256 elements, 512 relationships."""
        contract = self.service.build("bdd_diagram")["topLevelFields"]
        self.assertIn("64 characters", contract["diagramName"]["limit"])
        self.assertIn("a-z0-9", contract["diagramName"]["limit"])
        self.assertIn("256 entries", contract["elements"]["limit"])
        self.assertIn("512 entries", contract["relationships"]["limit"])
        self.assertEqual(contract["kind"]["limit"], "none")

    def test_the_contract_does_not_claim_its_refusal_table_is_complete(self):
        """It said "all N rules that can refuse a draft". It never was: `schema_*` is one
        code per jsonschema keyword, generated, and excluded from the table by design. A
        host that trusted the claim was refused by a rule the claim said did not exist."""
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            prose = _payload(self.service, diagram_type)
            with self.subTest(diagram_type=diagram_type):
                self.assertNotIn("all 20 rules", prose)
                self.assertIn("meaning-stage", prose)
                self.assertIn("schema_<keyword>", prose)

    def test_the_refusal_guide_reaches_the_host(self):
        service = AuthoringContractService()
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            payload = _payload(service, diagram_type)
            shipped = {r["code"] for r in service.build(diagram_type)["refusals"]}
            with self.subTest(diagram_type=diagram_type):
                self.assertEqual(shipped, {code for code, _rule in REFUSAL_GUIDE})
                for code, _rule in REFUSAL_GUIDE:
                    self.assertIn(code, payload)

    def test_the_bdd_example_is_a_draft_the_validator_accepts(self):
        """An example that would be refused is worse than no example."""
        example = self.service.build("bdd_diagram")["example"]
        self.assertIsNotNone(example)
        result = DraftValidationService().validate(example)
        self.assertTrue(result.valid, msg=[f.message for f in result.findings])

    # ---- what reaches the host ------------------------------------------------------

    def test_the_payload_names_the_type_its_vocabulary_and_its_guidance(self):
        payload = _payload(self.service, "bdd_diagram")

        self.assertIn("Authoring a `bdd_diagram` draft", payload)
        self.assertIn("Block Definition Diagram", payload)
        self.assertIn("composition", payload)
        # The containment rule now sits on `parentId`, where a host is reading, rather
        # than as a sentence 126 lines below the field it governs.
        self.assertIn("has no container element", payload)
        # The per-type guidance file is included, not summarized away.
        self.assertIn("Prefer the weaker true relationship", payload)

    def test_the_prose_warns_against_the_behaviour_driven_reading(self):
        """Two complete runs were lost to reading bdd as behaviour-driven development."""
        prose = _payload(self.service, "bdd_diagram")
        self.assertIn("Not behaviour-driven development", prose)

    def test_every_type_renders_prose_without_placeholders(self):
        for diagram_type in SUPPORTED_DIAGRAM_TYPES:
            with self.subTest(diagram_type=diagram_type):
                prose = _payload(self.service, diagram_type)
                self.assertNotIn("None", prose)
                self.assertGreater(len(prose), 800)
