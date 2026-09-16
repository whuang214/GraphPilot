"""Tests for the browser-facing API routes."""

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from services.shared.workspace_storage_service import WorkspaceStorageService

LOAD_URL = "/api/diagrams/load"
SAVE_URL = "/api/diagrams/save"
LIST_URL = "/api/diagrams/list"
VALIDATE_URL = "/api/diagrams/validate"
RENDER_URL = "/api/diagrams/render"

VALID_DIAGRAM = {
    "schemaVersion": "graphpilot.diagram.v1",
    "kind": "diagram",
    "diagramType": "activity_diagram",
    "id": "diagram_test",
    "name": "Test Diagram",
    "metadata": {},
    "viewport": {"x": 0, "y": 0, "zoom": 1},
    "nodes": [
        {
            "id": "node_start",
            "type": "gpNode",
            "position": {"x": 100, "y": 100},
            "data": {"label": "Start", "semanticType": "initialNode"},
        }
    ],
    "edges": [],
}

# A diagram that passes all validation layers (sizes present, supported type),
# suitable for asserting a successful save round-trip.
SAVE_VALID_DIAGRAM = {
    "schemaVersion": "graphpilot.diagram.v1",
    "kind": "diagram",
    "diagramType": "activity_diagram",
    "id": "diagram_save_test",
    "name": "Save Test Diagram",
    "metadata": {"source": "ui", "blueprintKey": "activity_diagram.default"},
    "viewport": {"x": 0, "y": 0, "zoom": 1},
    "nodes": [
        {
            "id": "node_start",
            "type": "gpNode",
            "position": {"x": 80, "y": 80},
            "width": 140,
            "height": 60,
            "data": {"label": "Start", "semanticType": "initialNode"},
        },
        {
            "id": "node_review",
            "type": "gpNode",
            "position": {"x": 280, "y": 80},
            "width": 180,
            "height": 60,
            "data": {"label": "Review Order", "semanticType": "opaqueAction"},
        },
    ],
    "edges": [
        {
            "id": "edge_start_to_review",
            "type": "default",
            "source": "node_start",
            "target": "node_review",
            "label": "Next",
            "data": {"semanticType": "controlFlow"},
        }
    ],
}


class DiagramLoadRouteTests(SimpleTestCase):
    def setUp(self):
        # A temp dir acts as the user project workspace; the diagram is a named
        # file under <workspace>/.graphpilot/diagrams/order-approval.gp.json,
        # mirroring the real model.
        self._workspace = tempfile.mkdtemp()
        self._diagram_dir = Path(self._workspace) / ".graphpilot" / "diagrams"
        self._diagram_dir.mkdir(parents=True)
        self._diagram_path = self._diagram_dir / "order-approval.gp.json"

    def tearDown(self):
        shutil.rmtree(self._workspace, ignore_errors=True)

    def _write(self, content):
        self._diagram_path.write_text(content, encoding="utf-8")

    def test_load_success(self):
        self._write(json.dumps(VALID_DIAGRAM))
        response = self.client.get(LOAD_URL, {"path": str(self._diagram_path)})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["diagramPath"], str(self._diagram_path.resolve()))
        self.assertEqual(body["diagram"], VALID_DIAGRAM)
        self.assertEqual(len(body["revision"]), 64)

    def test_missing_path_returns_400(self):
        response = self.client.get(LOAD_URL)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "missing_path")

    def test_blank_path_returns_400(self):
        response = self.client.get(LOAD_URL, {"path": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "missing_path")

    def test_a_diagram_outside_any_storage_folder_opens(self):
        """Requiring a `.graphpilot` ancestor refused every diagram the product ships:
        the training and answer examples under `assets/blueprints/*/examples/` are
        ordinary `.gp.json` files in ordinary folders, and an editUrl pointing at one came
        back `invalid_path`. Where a file sits does not make it unsafe."""
        stray = Path(self._workspace) / "loose-diagram.gp.json"
        stray.write_text(json.dumps(VALID_DIAGRAM), encoding="utf-8")
        response = self.client.get(LOAD_URL, {"path": str(stray)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["diagram"], VALID_DIAGRAM)

    def test_a_loose_diagram_grants_only_its_own_directory(self):
        """The containment that matters is still applied. Opening a loose file makes its
        own folder the root, so a traversal out of it is refused exactly as it would be
        from inside a workspace."""
        stray = Path(self._workspace) / "loose-diagram.gp.json"
        stray.write_text(json.dumps(VALID_DIAGRAM), encoding="utf-8")
        escape = str(stray.parent / ".." / "escaped.gp.json")
        response = self.client.get(LOAD_URL, {"path": escape})
        self.assertNotEqual(response.status_code, 200)

    def test_file_not_found_returns_404(self):
        response = self.client.get(LOAD_URL, {"path": str(self._diagram_path)})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")

    def test_directory_path_returns_404(self):
        # A directory under .graphpilot must map to a clean not_found, not a 500.
        nested_dir = self._diagram_dir / "nested"
        nested_dir.mkdir()
        response = self.client.get(LOAD_URL, {"path": str(nested_dir)})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")

    def test_invalid_json_returns_422(self):
        self._write("not valid json {{{")
        response = self.client.get(LOAD_URL, {"path": str(self._diagram_path)})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "invalid_json")

    def test_non_object_json_returns_422(self):
        self._write(json.dumps([1, 2, 3]))
        response = self.client.get(LOAD_URL, {"path": str(self._diagram_path)})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "invalid_json")


class DiagramSaveRouteTests(SimpleTestCase):
    def setUp(self):
        self._workspace = tempfile.mkdtemp()
        self._diagram_dir = Path(self._workspace) / ".graphpilot" / "diagrams"
        self._diagram_dir.mkdir(parents=True)
        self._diagram_path = self._diagram_dir / "order-approval.gp.json"

    def tearDown(self):
        shutil.rmtree(self._workspace, ignore_errors=True)

    def _post(self, body):
        return self.client.post(
            SAVE_URL, data=json.dumps(body), content_type="application/json"
        )

    def _seed_existing(self):
        self._diagram_path.write_text(json.dumps({"stale": True}), encoding="utf-8")

    def test_save_success_writes_file(self):
        self._seed_existing()
        response = self._post(
            {"diagramPath": str(self._diagram_path), "diagram": SAVE_VALID_DIAGRAM}
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["saved"])
        self.assertEqual(body["diagramPath"], str(self._diagram_path.resolve()))
        self.assertEqual(body["diagram"]["metadata"].get("authoring"), "custom")
        on_disk = json.loads(self._diagram_path.read_text(encoding="utf-8"))
        # The UI save route stamps metadata.authoring = "custom" as provenance;
        # diagramType remains the strict/freeform switch.
        self.assertEqual(on_disk["metadata"].get("authoring"), "custom")
        expected = {**SAVE_VALID_DIAGRAM, "metadata": {**SAVE_VALID_DIAGRAM["metadata"], "authoring": "custom"}}
        self.assertEqual(on_disk, expected)

    def test_save_rejects_a_stale_expected_revision(self):
        self._seed_existing()
        response = self._post({
            "diagramPath": str(self._diagram_path),
            "diagram": SAVE_VALID_DIAGRAM,
            "expectedRevision": "0" * 64,
        })
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"]["code"], "source_changed")
        self.assertEqual(json.loads(self._diagram_path.read_text(encoding="utf-8")), {"stale": True})

    def test_save_accepts_the_current_expected_revision(self):
        self._seed_existing()
        revision = WorkspaceStorageService.for_diagram_path(self._diagram_path).diagram_revision(self._diagram_path)
        response = self._post({
            "diagramPath": str(self._diagram_path),
            "diagram": SAVE_VALID_DIAGRAM,
            "expectedRevision": revision,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["revision"]), 64)

    def test_save_renders_sibling_svg(self):
        # Render-on-save: a successful save writes <name>.svg beside the JSON and
        # returns its path.
        self._seed_existing()
        response = self._post(
            {"diagramPath": str(self._diagram_path), "diagram": SAVE_VALID_DIAGRAM}
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        svg_path = Path(body["svgPath"])
        self.assertEqual(svg_path.name, "order-approval.svg")
        self.assertEqual(svg_path.parent, self._diagram_dir.resolve())
        self.assertTrue(svg_path.is_file())
        self.assertTrue(svg_path.read_text(encoding="utf-8").lstrip().startswith("<?xml"))

    @patch("api.views._render_service.render", side_effect=OSError("render unavailable"))
    def test_save_render_failure_returns_nonfatal_problem_warning(self, _render):
        self._seed_existing()
        response = self._post(
            {"diagramPath": str(self._diagram_path), "diagram": SAVE_VALID_DIAGRAM}
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["saved"])
        self.assertNotIn("svgPath", body)
        self.assertEqual(
            body["warning"],
            {
                "code": "render_failed",
                "message": "The diagram was saved, but SVG rendering failed.",
                "retryable": True,
                "details": {
                    "diagramPath": str(self._diagram_path.resolve()),
                    "intendedSvgPath": str(
                        self._diagram_path.with_name("order-approval.svg").resolve()
                    ),
                },
            },
        )

    def test_save_overwrites_existing(self):
        self._diagram_path.write_text(json.dumps({"stale": True}), encoding="utf-8")
        response = self._post(
            {"diagramPath": str(self._diagram_path), "diagram": SAVE_VALID_DIAGRAM}
        )
        self.assertEqual(response.status_code, 200)
        on_disk = json.loads(self._diagram_path.read_text(encoding="utf-8"))
        expected = {**SAVE_VALID_DIAGRAM, "metadata": {**SAVE_VALID_DIAGRAM["metadata"], "authoring": "custom"}}
        self.assertEqual(on_disk, expected)

    def test_save_flips_off_type_diagram_to_custom(self):
        # A UI save whose board uses an element outside its declared type's vocabulary is
        # reconciled to the universal `custom` type (diagramType is the strict/freeform switch).
        self._seed_existing()
        block = {
            "id": "node_block",
            "type": "gpNode",
            "position": {"x": 480, "y": 80},
            "width": 180,
            "height": 80,
            "data": {"label": "Engine", "semanticType": "block"},
        }
        diagram = {**SAVE_VALID_DIAGRAM, "nodes": SAVE_VALID_DIAGRAM["nodes"] + [block]}
        response = self._post({"diagramPath": str(self._diagram_path), "diagram": diagram})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["diagram"]["diagramType"], "custom")
        on_disk = json.loads(self._diagram_path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk["diagramType"], "custom")

    def test_save_keeps_conformant_diagram_type(self):
        # A UI save that stays within its declared type's vocabulary keeps its diagramType.
        self._seed_existing()
        response = self._post(
            {"diagramPath": str(self._diagram_path), "diagram": SAVE_VALID_DIAGRAM}
        )
        self.assertEqual(response.status_code, 200)
        on_disk = json.loads(self._diagram_path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk["diagramType"], "activity_diagram")

    def test_missing_path_returns_400(self):
        response = self._post({"diagram": SAVE_VALID_DIAGRAM})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "missing_path")

    def test_missing_diagram_returns_400(self):
        response = self._post({"diagramPath": str(self._diagram_path)})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "invalid_diagram")

    def test_non_object_diagram_returns_400(self):
        response = self._post(
            {"diagramPath": str(self._diagram_path), "diagram": [1, 2, 3]}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "invalid_diagram")

    def test_schema_invalid_nested_data_returns_validation_failed_not_500(self):
        invalid = json.loads(json.dumps(SAVE_VALID_DIAGRAM))
        invalid["nodes"][0]["data"] = "not an object"
        response = self._post(
            {"diagramPath": str(self._diagram_path), "diagram": invalid}
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "validation_failed")

    def test_a_diagram_outside_any_storage_folder_saves_back(self):
        """Editing an example in the browser has to be able to write it back where it
        lives. A missing file is still a 404 — the change is about *where*, not whether."""
        stray = Path(self._workspace) / "loose-diagram.gp.json"
        stray.write_text(json.dumps({"stale": True}), encoding="utf-8")
        response = self._post(
            {"diagramPath": str(stray), "diagram": SAVE_VALID_DIAGRAM}
        )
        self.assertEqual(response.status_code, 200, response.json())
        written = json.loads(stray.read_text(encoding="utf-8"))
        self.assertEqual(written["nodes"], SAVE_VALID_DIAGRAM["nodes"])
        self.assertNotIn("stale", written)

    def test_valid_save_to_missing_file_returns_not_found(self):
        response = self._post(
            {"diagramPath": str(self._diagram_path), "diagram": SAVE_VALID_DIAGRAM}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")
        self.assertFalse(self._diagram_path.exists())

    def test_invalid_diagram_returns_validation_failed_and_does_not_write(self):
        invalid = {**SAVE_VALID_DIAGRAM, "nodes": []}  # blocking "no_nodes" error
        response = self._post(
            {"diagramPath": str(self._diagram_path), "diagram": invalid}
        )
        self.assertEqual(response.status_code, 422)
        body = response.json()["error"]
        self.assertEqual(body["code"], "validation_failed")
        self.assertTrue(body["retryable"])
        self.assertTrue(body["details"]["issues"])
        for issue in body["details"]["issues"]:
            self.assertEqual(set(issue), {"code", "message", "path"})
            self.assertIsInstance(issue["code"], str)
            self.assertIsInstance(issue["message"], str)
            self.assertTrue(issue["path"] is None or isinstance(issue["path"], str))
        self.assertFalse(self._diagram_path.exists())

    def test_invalid_save_leaves_existing_file_untouched(self):
        original = json.dumps(SAVE_VALID_DIAGRAM)
        self._diagram_path.write_text(original, encoding="utf-8")
        invalid = {**SAVE_VALID_DIAGRAM, "nodes": []}
        response = self._post(
            {"diagramPath": str(self._diagram_path), "diagram": invalid}
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(self._diagram_path.read_text(encoding="utf-8"), original)

    def test_blueprint_drift_warning_still_saves(self):
        self._seed_existing()
        drifted = {
            **SAVE_VALID_DIAGRAM,
            "metadata": {"source": "ui", "blueprintKey": "bdd_diagram.default"},
        }
        response = self._post(
            {"diagramPath": str(self._diagram_path), "diagram": drifted}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["saved"])

    def test_save_missing_metadata_is_rejected(self):
        # The UI save route stamps metadata.authoring only when metadata is a dict; a
        # save missing the required `metadata` is rejected by validation, not masked.
        no_metadata = {k: v for k, v in SAVE_VALID_DIAGRAM.items() if k != "metadata"}
        response = self._post(
            {"diagramPath": str(self._diagram_path), "diagram": no_metadata}
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "validation_failed")
        self.assertFalse(self._diagram_path.exists())


class DiagramListRouteTests(SimpleTestCase):
    """Read-only workspace diagram listing."""

    def setUp(self):
        self._workspace = tempfile.mkdtemp()
        self._diagram_dir = Path(self._workspace) / ".graphpilot" / "diagrams"
        self._diagram_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self._workspace, ignore_errors=True)

    def _write(self, name):
        p = self._diagram_dir / f"{name}.gp.json"
        p.write_text(json.dumps(VALID_DIAGRAM), encoding="utf-8")
        return p

    def test_list_returns_sorted_names_and_paths(self):
        self._write("beta")
        first = self._write("alpha")
        response = self.client.get(LIST_URL, {"path": str(first)})
        self.assertEqual(response.status_code, 200)
        diagrams = response.json()["diagrams"]
        self.assertEqual([d["name"] for d in diagrams], ["alpha", "beta"])
        self.assertIn(
            str((self._diagram_dir / "alpha.gp.json").resolve()),
            [d["path"] for d in diagrams],
        )

    def test_list_empty_workspace_returns_empty(self):
        # Pass a (not-yet-created) diagram path inside the workspace.
        probe = self._diagram_dir / "anything.gp.json"
        response = self.client.get(LIST_URL, {"path": str(probe)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["diagrams"], [])

    def test_list_missing_path_returns_400(self):
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "missing_path")

    def test_list_outside_a_storage_folder_is_empty_rather_than_an_error(self):
        """A loose file's folder is its own root, and a folder with no `.graphpilot` in it
        holds no named diagrams. Empty is the honest answer; it used to be a 400."""
        stray = Path(self._workspace) / "loose.gp.json"
        stray.write_text("{}", encoding="utf-8")
        response = self.client.get(LIST_URL, {"path": str(stray)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["diagrams"], [])


class DiagramValidateRouteTests(SimpleTestCase):
    """Path-free, write-free validation for the open-any-file flow."""

    def _post(self, body):
        return self.client.post(VALIDATE_URL, data=json.dumps(body), content_type="application/json")

    def test_valid_diagram_returns_valid_and_normalized(self):
        response = self._post({"diagram": SAVE_VALID_DIAGRAM})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["valid"])
        self.assertEqual(body["validationErrors"], [])
        # Returns the normalized diagram with the custom authoring marker stamped.
        self.assertEqual(body["diagram"]["metadata"].get("authoring"), "custom")

    def test_invalid_diagram_returns_errors_and_not_valid(self):
        invalid = {**SAVE_VALID_DIAGRAM, "nodes": []}  # blocking "no_nodes" error
        response = self._post({"diagram": invalid})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["valid"])
        self.assertTrue(body["validationErrors"])

    def test_schema_invalid_nested_data_returns_errors_not_500(self):
        invalid = json.loads(json.dumps(SAVE_VALID_DIAGRAM))
        invalid["nodes"][0]["data"] = "not an object"
        response = self._post({"diagram": invalid})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["valid"])
        self.assertTrue(response.json()["validationErrors"])

    def test_missing_diagram_returns_400(self):
        response = self._post({})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "invalid_diagram")

    def test_non_object_diagram_returns_400(self):
        response = self._post({"diagram": [1, 2, 3]})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "invalid_diagram")


class DiagramRenderRouteTests(SimpleTestCase):
    """Path-free, write-free render for the editor preview/export flow."""

    def _post(self, body):
        return self.client.post(RENDER_URL, data=json.dumps(body), content_type="application/json")

    def test_valid_diagram_returns_svg(self):
        response = self._post({"diagram": SAVE_VALID_DIAGRAM})
        self.assertEqual(response.status_code, 200)
        svg = response.json()["svg"]
        self.assertTrue(svg.lstrip().startswith("<?xml"))
        self.assertIn("</svg>", svg)

    def test_missing_diagram_returns_400(self):
        response = self._post({})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "invalid_diagram")

    def test_non_object_diagram_returns_400(self):
        response = self._post({"diagram": "nope"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "invalid_diagram")

    def test_malformed_diagram_returns_render_failed(self):
        # Missing the required 'nodes' list -> the render service rejects it.
        response = self._post({"diagram": {"edges": []}})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "render_failed")

    def test_non_dict_node_entries_return_render_failed_not_500(self):
        # `nodes` is a list but its entries aren't dicts: this used to raise an
        # uncaught AttributeError (500); it must now be a clean render_failed.
        response = self._post({"diagram": {"nodes": [1, 2], "edges": []}})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "render_failed")
