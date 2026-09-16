"""Draft validation refuses precisely, completely, and without repairing anything."""

import copy

from django.test import SimpleTestCase

from services.drafts.draft_validation_service import DraftValidationService
from services.shared.schema_registry import SchemaRegistry


def _bdd_draft():
    return {
        "schemaVersion": "graphpilot.draft.v1",
        "kind": "diagramDraft",
        "diagramName": "sample",
        "diagramType": "bdd_diagram",
        "authority": "as_implemented",
        "requests": ["Diagram this service."],
        "evidence": [
            {
                "id": "ev-service",
                "kind": "code",
                "locator": {"path": "src/service.py", "lineRange": {"start": 1, "end": 20}},
                "summary": "The service is defined here.",
            }
        ],
        "elements": [
            {
                "id": "service",
                "semanticType": "block",
                "label": "Service",
                "assurance": "grounded",
                "evidenceRefs": ["ev-service"],
            },
            {
                "id": "repository",
                "semanticType": "block",
                "label": "Repository",
                "assurance": "grounded",
                "evidenceRefs": ["ev-service"],
            },
        ],
        "relationships": [
            {
                "id": "service-uses-repository",
                "semanticType": "dependency",
                "source": "service",
                "target": "repository",
                "assurance": "grounded",
                "evidenceRefs": ["ev-service"],
            }
        ],
    }


def _activity_draft():
    return {
        "schemaVersion": "graphpilot.draft.v1",
        "kind": "diagramDraft",
        "diagramName": "flow",
        "diagramType": "activity_diagram",
        "authority": "conceptual",
        "requests": ["Diagram the flow."],
        "elements": [
            {"id": "start", "semanticType": "initialNode", "label": "Start", "assurance": "conceptual"},
            {"id": "choose", "semanticType": "decisionNode", "label": "Valid?", "assurance": "conceptual"},
            {"id": "accept", "semanticType": "opaqueAction", "label": "Accept", "assurance": "conceptual"},
            {"id": "reject", "semanticType": "opaqueAction", "label": "Reject", "assurance": "conceptual"},
        ],
        "relationships": [
            {"id": "start-to-choose", "semanticType": "controlFlow", "source": "start", "target": "choose", "assurance": "conceptual"},
            {"id": "choose-to-accept", "semanticType": "controlFlow", "source": "choose", "target": "accept", "guard": "valid", "assurance": "conceptual"},
            {"id": "choose-to-reject", "semanticType": "controlFlow", "source": "choose", "target": "reject", "guard": "invalid", "assurance": "conceptual"},
        ],
    }


class DraftValidationServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = DraftValidationService()

    def _codes(self, draft):
        return {finding.code for finding in self.service.validate(draft).findings}

    def _findings_at(self, draft, path):
        return [f for f in self.service.validate(draft).findings if f.path == path]

    # ---- a refusal states the rule it is enforcing --------------------------------

    def test_a_too_long_value_states_the_limit_and_the_actual_length(self):
        """A host binary-searched `diagram_check_draft` to discover the limit is 256.

        `jsonschema` says *"'…' is too long"* and echoes the whole offending value, which
        is the one thing the author already has. `pattern` errors quote their regex and
        were never a problem; these now match.
        """
        draft = _bdd_draft()
        draft["elements"][0]["label"] = "x" * 258

        finding, = self._findings_at(draft, "$.elements[0].label")

        self.assertEqual(finding.code, "schema_maxLength")
        self.assertIn("258 characters", finding.message)
        self.assertIn("limit is 256", finding.message)
        self.assertNotIn("x" * 100, finding.message)

    def test_a_wrong_type_names_the_keys_the_right_one_needs(self):
        """`features.constraints` cost one host six probe drafts.

        The old message said what the value was not — *"is not of type 'object'"* — and
        never what it should be, so the shape `{"expression": ...}` had to be guessed at.
        The subschema knows its required keys, so the refusal can simply say them.
        """
        draft = _bdd_draft()
        draft["elements"][0]["features"] = {"constraints": ["unique (user_id, workspace)"]}

        finding, = self._findings_at(draft, "$.elements[0].features.constraints[0]")

        self.assertEqual(finding.code, "schema_type")
        self.assertIn("an object is required", finding.message)
        self.assertIn("`expression`", finding.message)

    # ---- acceptance -------------------------------------------------------------

    def test_bundled_example_is_valid(self):
        example = SchemaRegistry().get_schema("diagram_draft")["examples"][0]
        self.assertTrue(self.service.validate(example).valid)

    def test_minimal_grounded_and_conceptual_drafts_are_valid(self):
        self.assertTrue(self.service.validate(_bdd_draft()).valid)
        self.assertTrue(self.service.validate(_activity_draft()).valid)

    def test_composition_may_carry_a_source_role_and_multiplicity(self):
        draft = _bdd_draft()
        draft["relationships"][0] = {
            "id": "part-of",
            "semanticType": "composition",
            "source": "repository",
            "target": "service",
            "sourceRole": "repository",
            "sourceMultiplicity": {"lower": 1, "upper": 1},
            "assurance": "grounded",
            "evidenceRefs": ["ev-service"],
        }
        self.assertTrue(self.service.validate(draft).valid)

    def test_a_non_object_draft_is_refused_without_crashing(self):
        for value in (None, [], "draft", 7):
            with self.subTest(value=value):
                result = self.service.validate(value)
                self.assertFalse(result.valid)
                self.assertEqual(result.findings[0].code, "draft_invalid")

    # ---- schema layer -----------------------------------------------------------

    def test_unknown_field_is_refused_rather_than_ignored(self):
        draft = _bdd_draft()
        draft["elements"][0]["colour"] = "blue"
        self.assertIn("schema_additionalProperties", self._codes(draft))

    def test_malformed_id_is_refused(self):
        """An id has to be usable as an id: no whitespace, no path separators, and not
        starting with punctuation."""
        for value in ("Service One", "service/one", "-service", "", "a" * 129):
            with self.subTest(value=value):
                draft = _bdd_draft()
                draft["elements"][0]["id"] = value
                self.assertTrue(
                    {"schema_pattern", "schema_minLength", "schema_maxLength"}
                    & self._codes(draft)
                )

    def test_an_id_the_editor_minted_is_accepted(self):
        """This used to be refused, and it made an edited diagram permanently unreadable.

        The editor names a hand-drawn relationship `edge_<source>_<target>_<uuid>`, the
        canonical schema pins no pattern at all and stores it happily, and the draft
        insisted on a lowercase hyphenated slug. So `diagram_read` projected a document
        that failed its own schema, and a host could never edit a diagram again once
        somebody had drawn a single edge on it — the exact diagrams the edit path exists
        to serve.

        The id is the key the merge preserves geometry on, so the projection cannot tidy
        it. The pattern has to accept what is already on disk. Hosts are still told to
        author a slug; this is about reading back what the editor wrote.
        """
        draft = _bdd_draft()
        draft["relationships"][0]["id"] = (
            "edge_auto_done_1dcdbfcb-8260-4584-aabd-86899b43c23d"
        )
        draft["elements"][0]["id"] = "node_Order_2"
        for item in draft["relationships"]:
            if item["source"] == "service":
                item["source"] = "node_Order_2"

        self.assertNotIn("schema_pattern", self._codes(draft))

    def test_schema_findings_suppress_downstream_layers(self):
        """A missing required field cannot also produce twenty reference errors."""
        draft = _bdd_draft()
        del draft["diagramType"]
        codes = self._codes(draft)
        self.assertEqual(codes, {"schema_required"})

    # ---- identity ---------------------------------------------------------------

    def test_duplicate_element_id_is_reported_against_the_later_one(self):
        draft = _bdd_draft()
        draft["elements"][1]["id"] = "service"
        findings = self._findings_at(draft, "$.elements[1].id")
        self.assertEqual([f.code for f in findings], ["duplicate_id"])

    def test_element_and_relationship_ids_share_one_space(self):
        draft = _bdd_draft()
        draft["relationships"][0]["id"] = "service"
        self.assertIn("duplicate_id", self._codes(draft))

    # ---- references -------------------------------------------------------------

    def test_unresolved_endpoint_evidence_and_assumption_refs(self):
        draft = _bdd_draft()
        draft["relationships"][0]["target"] = "missing"
        draft["elements"][0]["evidenceRefs"] = ["ev-nope"]
        draft["elements"][1]["assurance"] = "assumed"
        draft["elements"][1]["assumptionRef"] = "asm-nope"
        del draft["elements"][1]["evidenceRefs"]
        codes = self._codes(draft)
        self.assertIn("unresolved_reference", codes)
        paths = {f.path for f in self.service.validate(draft).findings}
        self.assertIn("$.relationships[0].target", paths)
        self.assertIn("$.elements[0].evidenceRefs[0]", paths)
        self.assertIn("$.elements[1].assumptionRef", paths)

    def test_self_parent_and_containment_cycle_are_reported(self):
        draft = _bdd_draft()
        draft["elements"][0]["parentId"] = "service"
        self.assertIn("cyclic_parent", self._codes(draft))

        looped = _bdd_draft()
        looped["elements"][0]["parentId"] = "repository"
        looped["elements"][1]["parentId"] = "service"
        self.assertIn("cyclic_parent", self._codes(looped))

    # ---- `user` is the editor's to claim, never a host's --------------------------

    def test_a_host_may_not_author_user_assurance(self):
        """It is a claim about who drew something, not about how well grounded it is.

        Only the editor can make it true. A host writing one would be stating a fact about
        the world it is not in a position to know — and the value exists precisely so a
        reader can tell a person's addition from a cited one.
        """
        draft = _bdd_draft()
        draft["elements"][0]["assurance"] = "user"
        draft["elements"][0].pop("evidenceRefs", None)

        findings = self._findings_at(draft, "$.elements[0].assurance")

        self.assertEqual([f.code for f in findings], ["assurance_unsupported"])
        self.assertIn("a person drew this", findings[0].message)

    def test_the_user_refusal_does_not_also_demand_evidence(self):
        """One cause, one finding. A `user` element has no evidenceRefs by definition, so
        reporting `grounded requires evidenceRefs` beside it would send a host to add a
        citation to something it should not have authored at all."""
        draft = _bdd_draft()
        draft["elements"][0]["assurance"] = "user"
        draft["elements"][0].pop("evidenceRefs", None)

        self.assertEqual(len(self._findings_at(draft, "$.elements[0].assurance")), 1)

    def test_user_is_in_the_schema_so_the_refusal_is_the_meaning_stage_one(self):
        """If the enum rejected it, the host would get `schema_enum` instead — and a
        shape-stage refusal cannot explain why the value exists but is not for it."""
        draft = _bdd_draft()
        draft["elements"][0]["assurance"] = "user"

        self.assertNotIn("schema_enum", self._codes(draft))

    # ---- the request log ----------------------------------------------------------

    def test_a_create_carrying_more_than_one_ask_is_refused(self):
        """Appending is what editing does. A create that arrives with a list has either
        copied one from somewhere or invented history, and both are worth refusing while
        nothing has been written."""
        draft = _bdd_draft()
        draft["requests"] = ["Draw the service layer.", "Now add the cache."]
        self.assertIn("requests_invalid", self._codes(draft))

    def test_one_ask_is_what_a_create_takes(self):
        draft = _bdd_draft()
        draft["requests"] = ["Draw the service layer."]
        self.assertNotIn("requests_invalid", self._codes(draft))

    def test_an_empty_request_log_is_refused_by_the_schema(self):
        draft = _bdd_draft()
        draft["requests"] = []
        self.assertIn("schema_minItems", self._codes(draft))

    # ---- authority and assurance ------------------------------------------------

    def test_as_implemented_requires_evidence(self):
        draft = _bdd_draft()
        draft["evidence"] = []
        for element in draft["elements"]:
            element["assurance"] = "assumed"
            element["assumptionRef"] = "asm-x"
            del element["evidenceRefs"]
        draft["relationships"][0]["assurance"] = "assumed"
        draft["relationships"][0]["assumptionRef"] = "asm-x"
        del draft["relationships"][0]["evidenceRefs"]
        draft["assumptions"] = [
            {"id": "asm-x", "statement": "Assume it.", "reason": "Not established.", "acceptedBy": "host"}
        ]
        self.assertIn("evidence_required", self._codes(draft))

    def test_conceptual_authority_forbids_evidence(self):
        draft = _activity_draft()
        draft["evidence"] = [
            {
                "id": "ev-x",
                "kind": "code",
                "locator": {"path": "a.py", "lineRange": {"start": 1, "end": 2}},
                "summary": "Something.",
            }
        ]
        self.assertIn("evidence_unexpected", self._codes(draft))

    def test_grounded_without_evidence_and_assumed_without_assumption(self):
        draft = _bdd_draft()
        del draft["elements"][0]["evidenceRefs"]
        draft["elements"][1]["assurance"] = "assumed"
        del draft["elements"][1]["evidenceRefs"]
        findings = self.service.validate(draft).findings
        self.assertEqual(
            [f.path for f in findings if f.code == "assurance_unsupported"],
            ["$.elements[0].assurance", "$.elements[1].assurance"],
        )

    def test_assurance_and_authority_must_agree_in_both_directions(self):
        conceptual_in_grounded = _bdd_draft()
        conceptual_in_grounded["elements"][0]["assurance"] = "conceptual"
        self.assertIn("assurance_unsupported", self._codes(conceptual_in_grounded))

        grounded_in_conceptual = _activity_draft()
        grounded_in_conceptual["elements"][0]["assurance"] = "grounded"
        self.assertIn("assurance_unsupported", self._codes(grounded_in_conceptual))

    # ---- vocabulary -------------------------------------------------------------

    def test_off_vocabulary_types_name_the_permitted_set(self):
        draft = _bdd_draft()
        draft["elements"][0]["semanticType"] = "opaqueAction"
        draft["relationships"][0]["semanticType"] = "controlFlow"
        findings = [f for f in self.service.validate(draft).findings if f.code == "semantic_type_unsupported"]
        self.assertEqual(len(findings), 2)
        element_finding = next(f for f in findings if f.path.startswith("$.elements"))
        self.assertIn("block", element_finding.message)
        self.assertEqual(element_finding.details["permitted"], ["block", "note"])

    def test_stereotype_is_bdd_only(self):
        draft = _activity_draft()
        draft["elements"][0]["stereotype"] = "«control»"
        self.assertIn("stereotype_unsupported", self._codes(draft))

    def test_a_block_only_field_is_refused_on_a_note_in_a_bdd_diagram(self):
        """Gating on the diagram type alone left the hole one level down.

        Only a `classifier-box` draws a compartment, so `features` on a `note` validated,
        persisted, and then rendered nothing — the exact failure the gate exists to stop.
        The published refusal already read "Only a BDD **block** takes a `stereotype`", so
        the prose was right and the check was not.
        """
        draft = _bdd_draft()
        draft["elements"].append({
            "id": "remark",
            "semanticType": "note",
            "label": "A remark.",
            "features": {"literals": ["NOPE"]},
            "stereotype": "«aside»",
            "assurance": "grounded",
            "evidenceRefs": ["ev-service"],
        })
        index = len(draft["elements"]) - 1
        findings = {f.path: f for f in self.service.validate(draft).findings}
        self.assertIn(f"$.elements[{index}].features", findings)
        self.assertIn(f"$.elements[{index}].stereotype", findings)
        self.assertIn("a note is not a block", findings[f"$.elements[{index}].features"].message)

    def test_an_extend_only_field_is_refused_on_another_relationship(self):
        """`condition` and `extensionLocations` were copied through only for an `extend`.

        Anywhere else they validated and were then dropped without a word — the same
        silent-discard class as compartments on a non-block.
        """
        for field, value in (("condition", "if stock is low"), ("extensionLocations", ["after save"])):
            draft = _bdd_draft()
            draft["relationships"][0][field] = value
            with self.subTest(field=field):
                findings = {f.path: f for f in self.service.validate(draft).findings}
                self.assertIn(f"$.relationships[0].{field}", findings)
                self.assertEqual(findings[f"$.relationships[0].{field}"].code, "notation_invalid")

    def test_a_block_field_on_a_block_is_still_accepted(self):
        """The narrowing must not refuse the case it exists to serve."""
        draft = _bdd_draft()
        draft["elements"][0]["features"] = {"literals": ["OPEN", "DONE"]}
        draft["elements"][0]["stereotype"] = "«system»"
        self.assertTrue(self.service.validate(draft).valid, msg=self._codes(draft))

    # ---- notation ---------------------------------------------------------------

    def test_forbidden_relationship_ends_are_refused_not_dropped(self):
        draft = _bdd_draft()
        draft["relationships"][0]["sourceRole"] = "client"
        self.assertIn("notation_invalid", self._codes(draft))

        generalization = _bdd_draft()
        generalization["relationships"][0] = {
            "id": "child-of",
            "semanticType": "generalization",
            "source": "service",
            "target": "repository",
            "targetMultiplicity": {"lower": 1, "upper": 1},
            "assurance": "grounded",
            "evidenceRefs": ["ev-service"],
        }
        findings = [f for f in self.service.validate(generalization).findings if f.code == "notation_invalid"]
        self.assertEqual([f.path for f in findings], ["$.relationships[0].targetMultiplicity"])

    def test_guard_belongs_only_to_control_flow(self):
        draft = _bdd_draft()
        draft["relationships"][0]["guard"] = "always"
        self.assertIn("notation_invalid", self._codes(draft))

    def test_a_decision_with_two_branches_needs_guards(self):
        draft = _activity_draft()
        del draft["relationships"][1]["guard"]
        findings = [f for f in self.service.validate(draft).findings if f.code == "guard_required"]
        self.assertEqual([f.path for f in findings], ["$.relationships[1].guard"])

    def test_a_single_outgoing_branch_needs_no_guard(self):
        draft = _activity_draft()
        draft["relationships"] = draft["relationships"][:2]
        del draft["relationships"][1]["guard"]
        draft["elements"] = [e for e in draft["elements"] if e["id"] != "reject"]
        self.assertNotIn("guard_required", self._codes(draft))

    def test_comment_link_requires_a_note_endpoint(self):
        draft = _bdd_draft()
        draft["relationships"][0]["semanticType"] = "commentLink"
        self.assertIn("notation_invalid", self._codes(draft))

        annotated = _bdd_draft()
        annotated["elements"].append(
            {"id": "remark", "semanticType": "note", "label": "Wired in main.", "assurance": "grounded", "evidenceRefs": ["ev-service"]}
        )
        annotated["relationships"][0] = {
            "id": "remark-on-service",
            "semanticType": "commentLink",
            "source": "remark",
            "target": "service",
            "assurance": "grounded",
            "evidenceRefs": ["ev-service"],
        }
        self.assertTrue(self.service.validate(annotated).valid)

    def test_bdd_structural_relationships_require_block_endpoints(self):
        draft = _bdd_draft()
        draft["elements"][1] = {
            "id": "repository",
            "semanticType": "note",
            "label": "A remark",
            "assurance": "grounded",
            "evidenceRefs": ["ev-service"],
        }
        findings = [f for f in self.service.validate(draft).findings if f.code == "notation_invalid"]
        self.assertEqual([f.path for f in findings], ["$.relationships[0].target"])

    # ---- reporting --------------------------------------------------------------

    def test_every_reason_is_returned_at_once_and_sorted(self):
        draft = _bdd_draft()
        draft["relationships"][0]["target"] = "missing"
        draft["relationships"][0]["sourceRole"] = "client"
        del draft["elements"][0]["evidenceRefs"]
        draft["elements"][1]["semanticType"] = "opaqueAction"

        findings = self.service.validate(draft).findings
        self.assertGreaterEqual(len(findings), 4)
        self.assertEqual(
            list(findings),
            sorted(findings, key=lambda item: (item.path, item.code, item.message)),
        )
        self.assertEqual(
            {f.code for f in findings},
            {"assurance_unsupported", "notation_invalid", "semantic_type_unsupported", "unresolved_reference"},
        )

    def test_validation_never_mutates_the_submitted_draft(self):
        draft = _bdd_draft()
        draft["elements"][0]["semanticType"] = "opaqueAction"
        before = copy.deepcopy(draft)
        self.service.validate(draft)
        self.assertEqual(draft, before)
