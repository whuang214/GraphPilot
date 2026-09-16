import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource

from services.shared import schema_registry as schema_registry_module
from services.shared.schema_identities import SCHEMA_IDENTITIES
from services.diagrams.catalog.diagram_types import SUPPORTED_DIAGRAM_TYPES
from services.shared.schema_registry import SchemaArtifact, SchemaRegistry


_VALID_ARTIFACT = (
    '{"$schema":"https://json-schema.org/draft/2020-12/schema",'
    '"$id":"graphpilot.one.v1","type":"object",'
    '"required":["schemaVersion","kind"],"additionalProperties":false,'
    '"properties":{"schemaVersion":{"const":"graphpilot.one.v1"},'
    '"kind":{"const":"one"}}}'
)
_BROKEN_ARTIFACT = (
    '{"$schema":"https://json-schema.org/draft/2020-12/schema",'
    '"$id":"graphpilot.one.v1","type":"not-a-json-schema-type"}'
)
_ONE = (SchemaArtifact("one", "one.json", "graphpilot.one.v1", "one"),)


SCHEMA_ROOT = Path(__file__).resolve().parent.parent.parent / "assets" / "schemas"


class SchemaRegistryTests(SimpleTestCase):
    def setUp(self):
        self.registry = SchemaRegistry(schema_root=SCHEMA_ROOT)

    def test_loads_all_registered_schemas_and_validates_meta_schema(self):
        schemas = tuple(
            self.registry.get_schema(artifact.key)
            for artifact in self.registry.list_schema_artifacts()
        )

        self.assertEqual(
            [schema["$id"] for schema in schemas],
            [artifact.schema_id for artifact in self.registry.list_schema_artifacts()],
        )
        self.assertIn("graphpilot.diagram.v1", [schema["$id"] for schema in schemas])
        for schema in schemas:
            Draft202012Validator.check_schema(schema)

    def test_pre_namespace_context_schema_keys_and_files_are_absent(self):
        for key in ("evidence_manifest", "diagram_request"):
            with self.subTest(key=key), self.assertRaises(KeyError):
                self.registry.get_schema(key)
        self.assertFalse((SCHEMA_ROOT / "evidence-manifest.json").exists())
        self.assertFalse((SCHEMA_ROOT / "diagram-request.json").exists())

    def test_loaded_schemas_are_copy_isolated_from_the_cache(self):
        first = self.registry.get_diagram_schema()
        second = self.registry.get_diagram_schema()

        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        first["required"].append("injected")
        self.assertNotIn("injected", self.registry.get_diagram_schema()["required"])

    def test_process_wide_cache_does_not_leak_mutations_between_instances(self):
        first = SchemaRegistry(schema_root=SCHEMA_ROOT).get_diagram_schema()
        first["required"].append("injected")

        second = SchemaRegistry(schema_root=SCHEMA_ROOT).get_diagram_schema()
        self.assertNotIn("injected", second["required"])

    def test_reference_registry_is_reused_across_instances(self):
        first = SchemaRegistry(schema_root=SCHEMA_ROOT).reference_registry()
        second = SchemaRegistry(schema_root=SCHEMA_ROOT).reference_registry()

        self.assertIs(first, second)

    def test_reference_registry_resolves_every_registered_schema_id(self):
        references = self.registry.reference_registry()

        for artifact in self.registry.list_schema_artifacts():
            with self.subTest(schema_id=artifact.schema_id):
                self.assertEqual(
                    references[artifact.schema_id].contents["$id"], artifact.schema_id
                )

    def test_every_bundled_example_validates_against_its_own_schema(self):
        """A bundled ``examples`` entry is an annotation, not a validated artifact.

        Nothing in JSON Schema checks it, yet the authoring contract returns these
        examples to hosts as the shape to copy. A stale example would teach a wrong
        shape with full confidence, which is worse than returning nothing. The
        reference registry is required because bundled schemas cross-``$ref`` by
        ``$id``; a bare validator raises ``Unresolvable`` here.
        """
        references = self.registry.reference_registry()
        checked = 0

        for artifact in self.registry.list_schema_artifacts():
            schema = self.registry.get_schema(artifact.key)
            for index, example in enumerate(schema.get("examples", ())):
                checked += 1
                with self.subTest(schema=artifact.filename, example=index):
                    validator = Draft202012Validator(schema, registry=references)
                    errors = [
                        f"{list(error.absolute_path)}: {error.validator}: {error.message}"
                        for error in validator.iter_errors(example)
                    ]
                    self.assertEqual(errors, [])

        self.assertGreaterEqual(checked, 1)

    def test_reference_registry_is_keyed_by_schema_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "one.json").write_text(
                '{"$schema":"https://json-schema.org/draft/2020-12/schema",'
                '"$id":"graphpilot.one.v1","type":"object",'
                '"required":["schemaVersion","kind"],"additionalProperties":false,'
                '"properties":{"schemaVersion":{"const":"graphpilot.one.v1"},'
                '"kind":{"const":"one"}}}',
                encoding="utf-8",
            )
            scoped = SchemaRegistry(
                schema_root=root,
                artifacts=(
                    SchemaArtifact("one", "one.json", "graphpilot.one.v1", "one"),
                ),
            )

            self.assertIsNot(scoped.reference_registry(), self.registry.reference_registry())
            self.assertEqual(
                scoped.reference_registry()["graphpilot.one.v1"].contents["$id"],
                "graphpilot.one.v1",
            )

    def test_generation_contract_inventory_is_registered_and_meta_valid(self):
        artifacts = {artifact.key: artifact for artifact in self.registry.list_schema_artifacts()}
        self.assertTrue(set(SCHEMA_IDENTITIES).issubset(artifacts))
        report = self.registry.validate_inventory()
        reference_registry = Registry().with_resources(
            (
                artifact.schema_id,
                Resource.from_contents(self.registry.get_schema(artifact.key)),
            )
            for artifact in artifacts.values()
        )

        self.assertEqual(report["schemaCount"], len(artifacts))
        self.assertEqual(report["schemaIds"], sorted(report["schemaIds"]))
        for key, identity in SCHEMA_IDENTITIES.items():
            artifact = artifacts[key]
            self.assertEqual(artifact.schema_id, identity.schema_id)
            self.assertEqual(artifact.kind, identity.kind)
            self.assertEqual(artifact.filename, identity.filename)
            schema = self.registry.get_schema(key)
            Draft202012Validator.check_schema(schema)
            examples = schema.get("examples")
            self.assertIsInstance(examples, list, msg=key)
            self.assertTrue(examples, msg=key)
            # The draft schema carries the worked example the authoring contract serves,
            # and there is one per diagram type: the example is the only place the draft
            # envelope is written down, so a type without one leaves a host unable to
            # author at all. Every other schema still carries exactly one.
            if key == "diagram_draft":
                served = [e["diagramType"] for e in examples]
                self.assertEqual(sorted(served), sorted(SUPPORTED_DIAGRAM_TYPES), msg=key)
                self.assertEqual(len(served), len(set(served)), msg="one example per type")
            else:
                self.assertEqual(len(examples), 1, msg=key)
            validator = Draft202012Validator(schema, registry=reference_registry)
            for index, example in enumerate(examples):
                errors = list(validator.iter_errors(example))
                self.assertEqual(errors, [], msg=f"{key}[{index}]: {errors}")

    def test_inventory_rejects_duplicate_ids_paths_and_unapproved_kinds(self):
        duplicate_id = (
            SchemaArtifact("one", "one.json", "graphpilot.one.v1", "one"),
            SchemaArtifact("two", "two.json", "graphpilot.one.v1", "two"),
        )
        duplicate_path = (
            SchemaArtifact("one", "same.json", "graphpilot.one.v1", "one"),
            SchemaArtifact("two", "same.json", "graphpilot.two.v1", "two"),
        )
        duplicate_kind = (
            SchemaArtifact("one", "one.json", "graphpilot.one.v1", "same"),
            SchemaArtifact("two", "two.json", "graphpilot.two.v1", "same"),
        )

        for artifacts in (duplicate_id, duplicate_path, duplicate_kind):
            with self.subTest(artifacts=artifacts):
                with self.assertRaises(ValueError):
                    SchemaRegistry(schema_root=SCHEMA_ROOT, artifacts=artifacts)

    def test_inventory_rejects_schema_identity_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "one.json").write_text(
                '{"$schema":"https://json-schema.org/draft/2020-12/schema",'
                '"$id":"graphpilot.wrong.v1","type":"object",'
                '"required":["schemaVersion","kind"],"additionalProperties":false,'
                '"properties":{"schemaVersion":{"const":"graphpilot.wrong.v1"},'
                '"kind":{"const":"one"}}}',
                encoding="utf-8",
            )
            registry = SchemaRegistry(
                schema_root=root,
                artifacts=(
                    SchemaArtifact("one", "one.json", "graphpilot.one.v1", "one"),
                ),
            )
            with self.assertRaisesRegex(ValueError, "\\$id mismatch"):
                registry.validate_inventory()

    def test_diagram_summary_preserves_existing_contract(self):
        summary = self.registry.get_diagram_schema_summary("activity_diagram")

        self.assertEqual(summary["schemaId"], "graphpilot.diagram.v1")
        self.assertEqual(
            summary["supportedDiagramTypes"],
            ["activity_diagram", "use_case_diagram", "bdd_diagram"],
        )
        self.assertIn("id", summary["nodeRequiredFields"])
        self.assertIn("source", summary["edgeRequiredFields"])

    def test_invalid_diagram_type_is_rejected(self):
        with self.assertRaises(ValueError):
            self.registry.get_diagram_schema("sequence_diagram")
        with self.assertRaises(ValueError):
            self.registry.get_diagram_schema_summary("sequence_diagram")

    def test_missing_schema_is_reported_with_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = SchemaRegistry(schema_root=Path(tmp))

            with self.assertRaisesRegex(FileNotFoundError, "diagram.json"):
                registry.get_diagram_schema()

    def test_invalid_schema_json_is_reported_with_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "diagram.json").write_text("not json {{{", encoding="utf-8")
            registry = SchemaRegistry(schema_root=root)

            with self.assertRaisesRegex(ValueError, "diagram.json"):
                registry.get_diagram_schema()


class SchemaMetaValidationCacheTests(SimpleTestCase):
    """`checked_schema` is `check_schema` plus memoization — never a bypass.

    Bundled artifacts are immutable, so the metaschema walk is a pure function of the
    file. These tests pin the two properties that make caching it safe: a malformed
    artifact is still rejected, and one root never vouches for another.
    """

    def setUp(self):
        SchemaRegistry.clear_caches()
        self.addCleanup(SchemaRegistry.clear_caches)

    @staticmethod
    def _spy():
        return mock.patch.object(
            schema_registry_module.Draft202012Validator,
            "check_schema",
            wraps=Draft202012Validator.check_schema,
        )

    @staticmethod
    def _scoped(root: Path, body: str) -> SchemaRegistry:
        (root / "one.json").write_text(body, encoding="utf-8")
        return SchemaRegistry(schema_root=root, artifacts=_ONE)

    def test_meta_validation_runs_once_per_root_across_instances(self):
        registry = SchemaRegistry(schema_root=SCHEMA_ROOT)

        with self._spy() as checked:
            registry.checked_schema("diagram")
            registry.checked_schema("diagram")
            SchemaRegistry(schema_root=SCHEMA_ROOT).checked_schema("diagram")

        self.assertEqual(checked.call_count, 1)

    def test_a_malformed_artifact_is_rejected_on_every_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = self._scoped(Path(tmp), _BROKEN_ARTIFACT)

            for attempt in range(2):
                with self.subTest(attempt=attempt), self.assertRaises(SchemaError):
                    registry.checked_schema("one")

    def test_one_root_does_not_vouch_for_another(self):
        with tempfile.TemporaryDirectory() as good, tempfile.TemporaryDirectory() as bad:
            self._scoped(Path(good), _VALID_ARTIFACT).checked_schema("one")

            with self.assertRaises(SchemaError):
                self._scoped(Path(bad), _BROKEN_ARTIFACT).checked_schema("one")

    def test_clear_caches_drops_the_meta_validation_cache(self):
        registry = SchemaRegistry(schema_root=SCHEMA_ROOT)
        registry.checked_schema("diagram")
        SchemaRegistry.clear_caches()

        with self._spy() as checked:
            registry.checked_schema("diagram")

        self.assertEqual(checked.call_count, 1)

    def test_checked_schema_is_copy_isolated_and_rejects_unknown_keys(self):
        registry = SchemaRegistry(schema_root=SCHEMA_ROOT)

        first = registry.checked_schema("diagram")
        first["required"].append("injected")

        self.assertEqual(first["$id"], "graphpilot.diagram.v1")
        self.assertNotIn("injected", registry.checked_schema("diagram")["required"])
        with self.assertRaises(KeyError):
            registry.checked_schema("not_a_registered_key")
