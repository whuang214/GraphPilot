"""Cached, copy-isolated access to GraphPilot's versioned JSON Schemas."""

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from django.conf import settings
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from services.diagrams.catalog.diagram_types import SUPPORTED_DIAGRAM_TYPES, TYPE_PROFILES, is_supported_diagram_type
from services.shared.schema_identities import SCHEMA_IDENTITIES


@dataclass(frozen=True)
class SchemaArtifact:
    key: str
    filename: str
    schema_id: str
    kind: str


_EXISTING_SCHEMA_ARTIFACTS = (
    SchemaArtifact("diagram", "diagram.json", "graphpilot.diagram.v1", "diagram"),
)

_GENERATION_SCHEMA_ARTIFACTS = tuple(
    SchemaArtifact(key, identity.filename, identity.schema_id, identity.kind)
    for key, identity in SCHEMA_IDENTITIES.items()
)

_SCHEMA_ARTIFACTS = _EXISTING_SCHEMA_ARTIFACTS + _GENERATION_SCHEMA_ARTIFACTS

# Parsed schema bodies and built reference registries are pure functions of the
# schema files on disk, so they are shared process-wide rather than rebuilt for
# every service instance. Both caches are keyed by the resolved schema root so a
# registry pointed at a temporary root never reads another root's artifacts.
_SCHEMA_FILE_CACHE: Dict[Tuple[str, str], Dict[str, Any]] = {}
_REFERENCE_REGISTRY_CACHE: Dict[Tuple[str, Tuple[str, ...]], Registry] = {}
# Meta-validation is a pure function of the schema file, so the answer cannot change
# while the process lives. Callers that build a validator per request would otherwise
# re-prove that an immutable bundled artifact is a well-formed schema on every request.
_CHECKED_SCHEMA_CACHE: set[Tuple[str, str]] = set()
# Per-type contracts that legitimately share one ``kind``. Empty until a
# multi-type contract is registered again.
_ALLOWED_DUPLICATE_KINDS: Dict[str, frozenset] = {}


class SchemaRegistry:
    """Load, validate, cache, and isolate registered schema artifacts."""

    def __init__(
        self,
        schema_root: Optional[Path] = None,
        *,
        artifacts: Optional[Iterable[SchemaArtifact]] = None,
    ) -> None:
        self._schema_root = (
            Path(schema_root)
            if schema_root is not None
            else Path(settings.BASE_DIR) / "assets" / "schemas"
        )
        self._artifacts: Tuple[SchemaArtifact, ...] = tuple(
            _SCHEMA_ARTIFACTS if artifacts is None else artifacts
        )
        self._validate_artifact_descriptors(self._artifacts)
        self._artifacts_by_key = {artifact.key: artifact for artifact in self._artifacts}
        self._schemas: Dict[str, Dict[str, Any]] = {}

    def get_schema(self, schema_name: str) -> Dict[str, Any]:
        """Return an isolated copy of one registered schema by registry key."""
        return copy.deepcopy(self._load_cached(schema_name))

    def checked_schema(self, schema_name: str) -> Dict[str, Any]:
        """Return an isolated copy of one schema, meta-validated once per process.

        Equivalent to ``check_schema(get_schema(key))`` but pays the metaschema walk
        at most once per schema root, so a malformed artifact still raises
        ``SchemaError`` on its first use rather than being silently accepted.
        """
        artifact = self._artifacts_by_key.get(schema_name)
        if artifact is None:
            raise KeyError(f"Unknown schema registry key: {schema_name}")
        cache_key = (str(self._schema_root), artifact.filename)
        if cache_key not in _CHECKED_SCHEMA_CACHE:
            Draft202012Validator.check_schema(self._load_cached(schema_name))
            _CHECKED_SCHEMA_CACHE.add(cache_key)
        return self.get_schema(schema_name)

    def list_schema_artifacts(self) -> Tuple[SchemaArtifact, ...]:
        return self._artifacts

    def reference_registry(self) -> Registry:
        """Return the shared `$ref` registry holding every registered artifact.

        `referencing.Registry` is immutable, so one instance per schema root is
        reused instead of re-copying the full inventory for each service.
        """
        cache_key = (
            str(self._schema_root),
            tuple(artifact.schema_id for artifact in self._artifacts),
        )
        registry = _REFERENCE_REGISTRY_CACHE.get(cache_key)
        if registry is None:
            registry = Registry().with_resources(
                (
                    artifact.schema_id,
                    Resource.from_contents(self.get_schema(artifact.key)),
                )
                for artifact in self._artifacts
            )
            _REFERENCE_REGISTRY_CACHE[cache_key] = registry
        return registry

    @staticmethod
    def clear_caches() -> None:
        """Drop the process-wide schema, registry, and meta-validation caches."""
        _SCHEMA_FILE_CACHE.clear()
        _REFERENCE_REGISTRY_CACHE.clear()
        _CHECKED_SCHEMA_CACHE.clear()

    def validate_inventory(self) -> Dict[str, Any]:
        """Meta-validate every artifact and its descriptor identity."""
        schema_ids = []
        for artifact in self._artifacts:
            schema = self._load_cached(artifact.key)
            Draft202012Validator.check_schema(schema)
            properties = schema.get("properties", {})
            schema_version = properties.get("schemaVersion", {}).get("const")
            kind = properties.get("kind", {}).get("const")
            if schema.get("$id") != artifact.schema_id:
                raise ValueError(f"Schema $id mismatch for {artifact.filename}.")
            if schema_version != artifact.schema_id:
                raise ValueError(f"schemaVersion mismatch for {artifact.filename}.")
            if kind != artifact.kind:
                raise ValueError(f"Schema kind mismatch for {artifact.filename}.")
            schema_ids.append(artifact.schema_id)
        return {
            "schemaCount": len(self._artifacts),
            "schemaIds": sorted(schema_ids),
        }

    def get_diagram_schema(self, diagram_type: Optional[str] = None) -> Dict[str, Any]:
        if diagram_type is not None:
            self._validate_diagram_type(diagram_type)
        return self.get_schema("diagram")

    def get_diagram_schema_summary(self, diagram_type: Optional[str] = None) -> Dict[str, Any]:
        if diagram_type is not None:
            self._validate_diagram_type(diagram_type)
        schema = self._load_cached("diagram")
        props = schema.get("properties", {})
        node_required: List[str] = schema.get("$defs", {}).get("node", {}).get("required", [])
        edge_required: List[str] = schema.get("$defs", {}).get("edge", {}).get("required", [])
        return {
            "schemaId": schema.get("$id"),
            "schemaVersion": props.get("schemaVersion", {}).get("const"),
            "requiredTopLevelFields": list(schema.get("required", [])),
            "supportedDiagramTypes": list(SUPPORTED_DIAGRAM_TYPES),
            "nodeRequiredFields": list(node_required),
            "edgeRequiredFields": list(edge_required),
        }

    def _load_cached(self, schema_name: str) -> Dict[str, Any]:
        if schema_name not in self._artifacts_by_key:
            raise KeyError(f"Unknown schema registry key: {schema_name}")
        if schema_name not in self._schemas:
            artifact = self._artifacts_by_key[schema_name]
            schema_path = self._schema_root / artifact.filename
            cache_key = (str(self._schema_root), artifact.filename)
            schema = _SCHEMA_FILE_CACHE.get(cache_key)
            if schema is None:
                if not schema_path.exists():
                    raise FileNotFoundError(f"Schema artifact not found: {schema_path}")
                try:
                    with schema_path.open("r", encoding="utf-8") as handle:
                        schema = json.load(handle)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Schema artifact contains invalid JSON: {schema_path}"
                    ) from exc
                if not isinstance(schema, dict):
                    raise ValueError(
                        f"Schema artifact must contain a JSON object: {schema_path}"
                    )
                _SCHEMA_FILE_CACHE[cache_key] = schema
            self._schemas[schema_name] = schema
        return self._schemas[schema_name]

    @staticmethod
    def _validate_artifact_descriptors(artifacts: Tuple[SchemaArtifact, ...]) -> None:
        keys = [artifact.key for artifact in artifacts]
        filenames = [artifact.filename for artifact in artifacts]
        schema_ids = [artifact.schema_id for artifact in artifacts]
        if len(keys) != len(set(keys)):
            raise ValueError("Schema registry keys must be unique.")
        if len(filenames) != len(set(filenames)):
            raise ValueError("Schema artifact paths must be unique.")
        if len(schema_ids) != len(set(schema_ids)):
            raise ValueError("Schema IDs must be unique.")

        by_kind: Dict[str, set[str]] = {}
        for artifact in artifacts:
            by_kind.setdefault(artifact.kind, set()).add(artifact.key)
        for kind, kind_keys in by_kind.items():
            if len(kind_keys) > 1 and frozenset(kind_keys) != _ALLOWED_DUPLICATE_KINDS.get(kind):
                raise ValueError(f"Schema kind {kind!r} is duplicated outside its approved family.")

    @staticmethod
    def _validate_diagram_type(diagram_type: str) -> None:
        if not is_supported_diagram_type(diagram_type):
            supported = ", ".join(TYPE_PROFILES)
            raise ValueError(
                f"Unsupported diagram type: {diagram_type!r}. Supported types: {supported}"
            )
