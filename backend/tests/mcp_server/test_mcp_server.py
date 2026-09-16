import json
import asyncio
import tempfile
from pathlib import Path

from django.test import SimpleTestCase
from mcp.types import CallToolResult

from mcp_server import server
from services.diagrams.catalog.constants import LONG_LABEL_LENGTH


def _run(coro):
    return asyncio.run(coro)


def _draft_with_label(label: str) -> dict:
    """The smallest valid draft that carries one label of the caller's choosing.

    Conceptual, so it cites nothing and needs no repository on disk — the label budget
    is a property of the draft, and proving that is half the point.
    """
    return {
        "schemaVersion": "graphpilot.draft.v1",
        "kind": "diagramDraft",
        "diagramName": "label-budget",
        "diagramType": "bdd_diagram",
        "authority": "conceptual",
        "requests": ["Draw one block."],
        "elements": [
            {"id": "only", "semanticType": "block", "label": label, "assurance": "conceptual"}
        ],
        "relationships": [],
    }


def _payload(result):
    return result.structuredContent or {} if isinstance(result, CallToolResult) else result


def _valid_diagram():
    return {
        "schemaVersion": "graphpilot.diagram.v1",
        "kind": "diagram",
        "diagramType": "activity_diagram",
        "id": "diagram_order_review",
        "name": "Order Review",
        "metadata": {"source": "mcp"},
        "viewport": {"x": 0, "y": 0, "zoom": 1},
        "nodes": [
            {
                "id": "start",
                "type": "gpNode",
                "position": {"x": 0, "y": 0},
                "width": 90,
                "height": 60,
                "data": {"label": "Start", "semanticType": "initialNode"},
            },
            {
                "id": "end",
                "type": "gpNode",
                "position": {"x": 0, "y": 120},
                "width": 90,
                "height": 60,
                "data": {"label": "End", "semanticType": "activityFinalNode"},
            },
        ],
        "edges": [
            {
                "id": "flow",
                "type": "default",
                "source": "start",
                "target": "end",
                "data": {"semanticType": "controlFlow"},
            }
        ],
    }


class DiagramLookupToolTests(SimpleTestCase):
    def test_list_types(self):
        payload = _payload(_run(server.diagram_list_types()))
        entries = payload["diagramTypes"]

        self.assertEqual(
            [item["diagramType"] for item in entries],
            ["activity_diagram", "use_case_diagram", "bdd_diagram"],
        )
        # An identifier alone is not discovery: a host read `bdd` as behaviour-driven
        # development, gathered behavioural evidence, and lost the whole run.
        for item in entries:
            with self.subTest(diagram_type=item["diagramType"]):
                self.assertTrue(item["meaning"].strip())
                self.assertTrue(item["chooseWhen"].strip())
        bdd = next(i for i in entries if i["diagramType"] == "bdd_diagram")
        self.assertIn("Block Definition Diagram", bdd["meaning"])

    def test_there_is_no_name_only_view_to_skim(self):
        """The old shape was a list of identifiers beside a separate map of meanings.

        A host could read `diagramTypes` — three bare strings — and never open
        `diagramTypeMeanings`, which is how `bdd` got read as behaviour-driven
        development. Every identifier now arrives welded to its explanation, so the
        skimmable view does not exist, and `howToChoose` says what to do with them.
        """
        payload = _payload(_run(server.diagram_list_types()))
        self.assertNotIn("diagramTypeMeanings", payload)
        self.assertIn("howToChoose", payload)
        for item in payload["diagramTypes"]:
            self.assertIsInstance(item, dict)
            self.assertEqual(
                sorted(item), ["chooseWhen", "diagramType", "meaning"]
            )
        # `chooseWhen` maps a request onto a type; a definition alone never did that.
        bdd = next(i for i in payload["diagramTypes"] if i["diagramType"] == "bdd_diagram")
        self.assertIn("not behaviour-driven development", bdd["chooseWhen"].lower())

    def test_a_check_reports_the_long_labels_a_create_would_warn_about(self):
        """Three cold hosts in one run authored inside the stated 256-character limit,
        were warned at 141, 139 and 134, and could not fix any of it — the diagram was
        already saved and nothing overwrites it. The warning is a character count, so
        nothing ever required a write to produce it."""
        draft = _draft_with_label("x" * (LONG_LABEL_LENGTH + 20))
        with tempfile.TemporaryDirectory() as workspace:
            checked = _run(server.diagram_check_draft(draft=draft, workspaceDir=workspace))
            created = _run(server.diagram_create(workspaceDir=workspace, draft=draft))

        preview = {w["code"] for w in checked.structuredContent["warnings"]}
        actual = {w["code"] for w in created.structuredContent["operationWarnings"]}
        self.assertIn("long_label", preview)
        # The draft is still valid — this is advice, not a refusal.
        self.assertTrue(checked.structuredContent["valid"])
        self.assertIn("long_label", checked.content[0].text)
        # And the preview must not disagree with the create it previews.
        self.assertTrue(preview <= actual, f"preview={preview} create={actual}")

    def test_the_check_does_not_claim_to_measure_relationship_labels(self):
        """`checked` said "whether each fits its element", and a clipped *edge* label —
        `«extend» [an uncancelled hold exists for th…` — got through and appeared at
        create. The fit check reads nodes. An overstated `checked` list is worse than a
        short honest one, because it is the one place the tool says what it knows."""
        with tempfile.TemporaryDirectory() as workspace:
            result = _run(
                server.diagram_check_draft(draft=_draft_with_label("Fine"), workspaceDir=workspace)
            )
        structured = result.structuredContent
        self.assertNotIn(
            "label lengths and whether each fits its element", structured["checked"],
            "the overstated wording is back",
        )
        self.assertTrue(any("element label" in c for c in structured["checked"]))
        self.assertTrue(any("relationship's label" in n for n in structured["notChecked"]))

    def test_a_taken_name_is_refused_and_nothing_offers_to_remove_it(self):
        """No tool on this surface destroys a saved diagram.

        One briefly did. `diagram_delete` was added to close the `hard_to_read` loop —
        `a5.f6` — and the next corpus run showed what that loop costs: a host cleared its
        collisions by flattening every guard to `yes`/`no` and demoting a decision to a
        note, spending three of six creates to make the diagram say less. The warning is
        GraphPilot's layout and never the host's to chase, so the loop should not exist
        and neither should the tool that served it.

        Removing a diagram is the user's decision, in their own repository, on a file that
        may carry editor work no draft knows about.
        """
        draft = _draft_with_label("First attempt")
        with tempfile.TemporaryDirectory() as workspace:
            created = _run(server.diagram_create(workspaceDir=workspace, draft=draft))
            self.assertFalse(created.isError)

            blocked = _run(server.diagram_create(workspaceDir=workspace, draft=draft))

        self.assertTrue(blocked.isError)
        self.assertEqual(blocked.structuredContent["error"]["code"], "diagram_exists")
        # The refusal must offer another name, not a way to destroy the first.
        self.assertIn("another `diagramName`", blocked.content[0].text)
        self.assertNotIn("delete", blocked.content[0].text.lower())

    def test_nothing_on_the_surface_removes_a_saved_diagram(self):
        tools = {tool.name for tool in _run(server.mcp.list_tools())}

        self.assertNotIn("diagram_delete", tools)
        for name in tools:
            with self.subTest(tool=name):
                self.assertNotIn("delete", name)

    def test_the_workflow_never_sends_a_host_to_chase_legibility(self):
        """Four voices used to brief this loop: the warning, the workflow, the
        `diagram_exists` refusal and the tool's own docstring. Fixing one would have left
        the incoherence that has bitten this contract before."""
        self.assertIn("hard to read", server._WORKFLOW)
        self.assertIn("not yours", server._WORKFLOW)
        self.assertNotIn("diagram_delete", server._WORKFLOW)

    def test_a_check_does_not_claim_to_know_what_only_the_picture_shows(self):
        """`hard_to_read` measures the drawn SVG — which label collided with which — so
        it cannot be known before there is a picture. Saying so is the point: a clean
        check is not a promise of a legible diagram, and a host that assumes otherwise
        learns the difference on a file it cannot replace."""
        with tempfile.TemporaryDirectory() as workspace:
            result = _run(
                server.diagram_check_draft(draft=_draft_with_label("Fine"), workspaceDir=workspace)
            )
        structured = result.structuredContent
        self.assertTrue(any("fits its element" in c for c in structured["checked"]))
        self.assertTrue(any("overlap" in n for n in structured["notChecked"]))
        self.assertNotIn("hard_to_read", {w["code"] for w in structured["warnings"]})

    def test_nothing_claims_a_refused_create_spends_the_name(self):
        """It never did — every refusal path returns before the first write.

        Three places said otherwise, and an A/B measured the cost: the host denied
        `diagram_check_draft` spent an estimated 40% of its effort re-verifying citations
        against a penalty that does not exist, and *"nearly dropped `stereotype` entirely
        … purely because a refusal felt expensive rather than because I doubted the
        semantics"*. A false claim about cost does not make a host careful, it makes a
        host hedge.
        """
        text = server._WORKFLOW + (server.diagram_check_draft.__doc__ or "")
        self.assertNotIn("the name is spent", text)
        self.assertNotIn("a name was spent", text)
        self.assertIn("does not consume the diagram name", text)

    def test_a_refused_create_lists_its_findings_in_the_prose_channel(self):
        """It reported a count and no findings: they existed only at
        `structuredContent.error.details.findings`, so a host reading the text channel
        learned that eight things were wrong and not one of them."""
        with tempfile.TemporaryDirectory() as workspace:
            result = _run(server.diagram_create(workspaceDir=workspace, draft={"no": 1}))
        prose = result.content[0].text
        findings = result.structuredContent["error"]["details"]["findings"]
        self.assertTrue(result.isError)
        self.assertGreater(len(findings), 1)
        for finding in findings[:40]:
            self.assertIn(finding["code"], prose)
            self.assertIn(finding["path"], prose)
        self.assertIn("the name is still free", prose)

    def test_the_workflow_ships_its_prose_once(self):
        """It was annotated `-> str`, so FastMCP wrapped the return into
        `{"result": ...}` — and the whole 5,400-character document shipped twice, once as
        `content` and once as the same string in a box. Nobody chose that; it fell out of
        the annotation. `structuredContent` is optional, and omitting it says something
        true: there is no structure here, only an argument to read."""
        result = _run(server.diagram_workflow())
        self.assertIsNone(result.structuredContent)
        self.assertIn("## The five steps", result.content[0].text)
        self.assertEqual(len(result.content), 1)

    def test_both_channels_carry_the_types(self):
        """Every other tool in the discovery path populates `structuredContent`; this one
        returned a bare dict, so the channel was `null` on the one call the workflow now
        makes mandatory."""
        result = _run(server.diagram_list_types())
        self.assertIsNotNone(result.structuredContent)
        text = result.content[0].text
        self.assertIn("bdd_diagram", text)
        self.assertIn("Block Definition Diagram", text)

    def test_diagram_list_types_is_the_only_place_the_meanings_live(self):
        """They used to be inlined into every `diagramType` argument description.

        That fixed a real failure — two runs lost to reading `bdd` as behaviour-driven
        development — and then outlived its reason. It does not scale: one sentence per
        type, repeated in `tools/list`, which every client loads at connect. And the
        failure stopped being terminal when the provider pipeline's append-only history
        went, because a host that fetches the wrong contract now reads `meaning` and pays
        one cheap call to fetch the right one.

        The enum stays — a client should still get the valid values for free.
        """
        tools = {tool.name: tool for tool in _run(server.mcp.list_tools())}
        spec = tools["diagram_get_authoring_contract"].inputSchema["properties"]["diagramType"]
        self.assertEqual(spec["enum"], ["activity_diagram", "use_case_diagram", "bdd_diagram"])
        self.assertIn("diagram_list_types", spec["description"])

        entries = _payload(_run(server.diagram_list_types()))["diagramTypes"]
        meanings = {i["diagramType"]: i["meaning"] for i in entries}
        for name, meaning in meanings.items():
            with self.subTest(diagram_type=name):
                self.assertNotIn(meaning, spec["description"], "the meanings are inlined again")
        # Nor is the bdd disambiguation restated here. Adding a diagram type must not mean
        # editing an argument description on every tool that accepts one.
        self.assertNotIn("behaviour-driven", spec["description"].lower())

        # It belongs in the returned data, not in any description of it. A tool
        # description says what the tool does; the payload says what each type means, so
        # a new type is one entry in DIAGRAM_TYPE_MEANINGS and no prose edit anywhere.
        self.assertNotIn("behaviour-driven", tools["diagram_list_types"].description.lower())
        self.assertIn("behaviour-driven development", meanings["bdd_diagram"].lower())
        self.assertIn("activity_diagram", meanings["bdd_diagram"])

    def test_an_unsupported_type_is_refused_but_is_not_the_real_net(self):
        """`unsupported_diagram_type` catches an identifier that does not exist. The
        mistake worth catching is a *valid* identifier chosen for the wrong reason, and
        only the contract's own `meaning` catches that — so it must say so plainly."""
        refused = _run(server.diagram_get_authoring_contract("behaviour_driven_development"))
        self.assertTrue(refused.isError)
        self.assertEqual(_payload(refused)["error"]["code"], "unsupported_diagram_type")

        wrong_but_valid = _run(server.diagram_get_authoring_contract("bdd_diagram"))
        meaning = _payload(wrong_but_valid)["meaning"].lower()
        self.assertIn("not behaviour-driven development", meaning)
        self.assertIn("activity_diagram", meaning)

    def test_the_canonical_schema_is_not_offered_to_an_author(self):
        """`g3`. `diagram_get_schema` told a host to do what the workflow forbids.

        Its description said *"Call before building or validating a diagram to learn its
        required structure"*, and it returned the **canonical** schema —
        `nodeRequiredFields: [id, type, position, data]`. That is the saved document, and
        the workflow says in bold *"Never author positions, styles, or relationship-end
        objects."* Five hosts across two corpus runs reported it as a trap; two wasted
        calls on it before working out it was the wrong document.

        `diagram_get_authoring_contract` answers the question it pretended to.
        """
        self.assertFalse(hasattr(server, "diagram_get_schema"))

    def test_validate_uses_shared_service(self):
        diagram = _valid_diagram()
        result = _payload(_run(server.diagram_validate(diagram)))

        self.assertEqual(
            {k: v for k, v in result.items() if k != "checkedCitations"},
            server._validation_service.validate(diagram).to_dict(),
        )
        # And it says which question it answered. Without a workspace it checked the
        # document, not whether the document is still true.
        self.assertFalse(result["checkedCitations"])

    def test_validate_can_say_whether_a_diagram_is_still_true(self):
        """`a5.f9`. `EvidenceService.recheck` re-hashes cited regions and reports the ones
        that moved — 46 lines that no surface reached, while `03-design/03-validation.md`
        listed evidence freshness as something GraphPilot checks. The capability was
        built, the promise was false, and the code read as dead to the audit.

        Exposed through the argument hosts already know: `workspaceDir` turns on citation
        checking here exactly as it does on `diagram_check_draft`.
        """
        with tempfile.TemporaryDirectory() as workspace:
            source = Path(workspace) / "app.py"
            source.write_text("class Thing:\n    pass\n", encoding="utf-8")
            draft = _draft_with_label("Thing")
            draft["authority"] = "as_implemented"
            draft["evidence"] = [{
                "id": "ev-one", "kind": "code",
                "locator": {"path": "app.py", "symbol": "Thing",
                            "lineRange": {"start": 1, "end": 2}},
                "summary": "The Thing class.",
            }]
            draft["elements"][0].update(assurance="grounded", evidenceRefs=["ev-one"])
            created = _run(server.diagram_create(workspaceDir=workspace, draft=draft))
            self.assertFalse(created.isError, created.content[0].text)
            diagram = json.loads(
                Path(created.structuredContent["diagramPath"]).read_text(encoding="utf-8")
            )

            # Through `_payload`, because that is what the transport does. Reading the
            # raw return instead is why nothing noticed `diagram_validate` was answering
            # in `content` while the contract published `structuredContent`.
            fresh = _payload(_run(server.diagram_validate(diagram, workspaceDir=workspace)))
            self.assertTrue(fresh["checkedCitations"])
            self.assertEqual(fresh["citationsChecked"], 1)
            self.assertEqual(fresh["staleCitations"], [])

            # The code moves underneath it, which is the whole point.
            source.write_text("class Something:\n    pass\n", encoding="utf-8")
            stale = _payload(_run(server.diagram_validate(diagram, workspaceDir=workspace)))

        self.assertTrue(stale["staleCitations"], "drift went unreported")
        self.assertTrue(stale["valid"], "drift is a warning, not a malformed document")


class ToolSurfaceTests(SimpleTestCase):
    """The published surface is exact; nothing reappears implicitly."""

    def test_registered_tools_are_exactly_the_published_surface(self):
        names = sorted(tool.name for tool in _run(server.mcp.list_tools()))
        self.assertEqual(
            names,
            [
                "diagram_check_draft",
                "diagram_create",
                "diagram_get_authoring_contract",
                "diagram_list_types",
                # The edit round trip. Two tools rather than one that infers the intent:
                # a write submits the *whole* desired state, so a host that did not know
                # a diagram already existed would omit everything already in it, and
                # omission deletes. Creating refuses when the name is taken and updating
                # refuses when it is free, so guessing wrong costs one refused call
                # instead of somebody's work.
                "diagram_read",
                "diagram_render",
                "diagram_update",
                "diagram_validate",
                "diagram_workflow",
                "echo",
                "health",
            ],
        )

    def test_removed_provider_backed_tools_are_absent(self):
        names = {tool.name for tool in _run(server.mcp.list_tools())}
        for removed in (
            "context_evidence_status",
            "context_evidence_save",
            "context_readiness_assess",
            "diagram_request_save",
            "diagram_generate_direct",
            "diagram_generate_from_context",
            "diagram_generation_get_contract",
            "diagram_generation_workflow",
        ):
            self.assertNotIn(removed, names)


class DiagramCreateToolTests(SimpleTestCase):
    """The MCP layer stays thin: it maps a refusal, it does not decide one."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name)
        source = self.workspace / "src" / "service.py"
        source.parent.mkdir(parents=True)
        source.write_text("\n".join(f"line {n}" for n in range(1, 31)), encoding="utf-8")

    def _draft(self, **overrides):
        draft = {
            "schemaVersion": "graphpilot.draft.v1",
            "kind": "diagramDraft",
            "diagramName": "service-structure",
            "diagramType": "bdd_diagram",
            "authority": "as_implemented",
            "requests": ["Diagram the service."],
            "evidence": [
                {
                    "id": "ev-service",
                    "kind": "code",
                    "locator": {"path": "src/service.py", "lineRange": {"start": 1, "end": 10}},
                    "summary": "The service is defined here.",
                }
            ],
            "elements": [
                {"id": "service", "semanticType": "block", "label": "Service", "assurance": "grounded", "evidenceRefs": ["ev-service"]},
                {"id": "repository", "semanticType": "block", "label": "Repository", "assurance": "grounded", "evidenceRefs": ["ev-service"]},
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
        draft.update(overrides)
        return draft

    def _create(self, draft=None, workspace=None):
        return _run(
            server.diagram_create(
                workspaceDir=workspace if workspace is not None else str(self.workspace),
                draft=draft or self._draft(),
            )
        )

    def test_a_created_diagram_returns_paths_counts_and_a_clickable_editor_link(self):
        result = self._create()
        payload = _payload(result)

        self.assertFalse(result.isError)
        self.assertEqual(payload["outcome"], "created")
        self.assertEqual(payload["diagramName"], "service-structure")
        self.assertEqual(payload["diagramType"], "bdd_diagram")
        self.assertEqual((payload["nodeCount"], payload["edgeCount"]), (2, 1))
        self.assertTrue(payload["diagramPath"].endswith("service-structure.gp.json"))
        self.assertTrue(payload["svgPath"].endswith("service-structure.svg"))
        self.assertIn("/editor?diagramPath=", payload["editUrl"])
        self.assertEqual(payload["assurance"]["authority"], "as_implemented")
        self.assertEqual(payload["operationWarnings"], [])

        markdown = result.content[0].text
        self.assertIn("Open in the GraphPilot editor", markdown)
        self.assertIn("(2 nodes, 1 edges)", markdown)

    def test_a_refused_draft_returns_every_finding_and_is_not_retryable(self):
        draft = self._draft()
        draft["elements"][0]["semanticType"] = "opaqueAction"

        result = self._create(draft)
        error = _payload(result)["error"]

        self.assertTrue(result.isError)
        self.assertEqual(error["code"], "semantic_type_unsupported")
        self.assertFalse(error["retryable"])
        paths = {finding["path"] for finding in error["details"]["findings"]}
        self.assertIn("$.elements[0].semanticType", paths)

    def test_creating_the_same_diagram_twice_is_refused(self):
        self._create()
        result = self._create()
        error = _payload(result)["error"]

        self.assertTrue(result.isError)
        self.assertEqual(error["code"], "diagram_exists")
        self.assertFalse(error["retryable"])

    def test_an_unusable_workspace_is_reported_before_anything_else(self):
        result = self._create(workspace=str(self.workspace / "nope"))
        self.assertTrue(result.isError)
        self.assertEqual(_payload(result)["error"]["code"], "invalid_workspace")
