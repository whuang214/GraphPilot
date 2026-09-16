"""Immutable identities for GraphPilot's persisted contracts."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class SchemaIdentity:
    schema_id: str
    kind: str
    filename: str


def _schemas(*values: tuple[str, str, str, str]) -> Mapping[str, SchemaIdentity]:
    return MappingProxyType(
        {
            key: SchemaIdentity(schema_id=schema_id, kind=kind, filename=filename)
            for key, schema_id, kind, filename in values
        }
    )


# The canonical diagram schema is registered separately by ``SchemaRegistry``; this
# registry carries the additional contracts.
SCHEMA_IDENTITIES = _schemas(
    ("diagram_draft", "graphpilot.draft.v1", "diagramDraft", "diagram-draft.json"),
)

LAYOUT_CONFIGURATION_VERSIONS = MappingProxyType(
    {
        "activity_diagram": "graphpilot.generation.layout.activity.v1",
        "use_case_diagram": "graphpilot.generation.layout.use-case.v1",
        "bdd_diagram": "graphpilot.generation.layout.bdd.v1",
    }
)
