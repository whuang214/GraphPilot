"""Service wrapper for supported diagram type lookups.

Centralises type registry access so API and MCP entry points never import
from the low-level ``diagram_types`` module directly.
"""

from services.diagrams.catalog.diagram_types import (
    CUSTOM_DIAGRAM,
    DIAGRAM_TYPE_GUIDE,
    DIAGRAM_TYPE_MEANINGS,
    SUPPORTED_DIAGRAM_TYPES,
    DiagramTypeProfile,
    conforms_to_type,
    get_type_profile,
    is_supported_diagram_type,
)


class DiagramTypeService:
    """Returns supported diagram type metadata from one backend location."""

    #: The universal "combine anything" canvas type — valid for save/validate, not generatable.
    CUSTOM_TYPE = CUSTOM_DIAGRAM

    def list_supported_types(self) -> list[str]:
        """Return the ordered generatable MVP type identifiers advertised by MCP."""
        return list(SUPPORTED_DIAGRAM_TYPES)

    def describe(self, diagram_type: str) -> str:
        """Return one plain sentence saying what *diagram_type* actually is.

        Returns an empty string for an unknown identifier rather than raising, so a
        caller can annotate a list without pre-filtering it.
        """
        return DIAGRAM_TYPE_MEANINGS.get(diagram_type, "")

    def choosing_guide(self) -> list[dict[str, str]]:
        """Every type as one entry carrying its identifier, meaning and when to pick it.

        Deliberately not a bare list of identifiers beside a separate map of meanings.
        That shape let a host read the names and skip the explanations, which is exactly
        how `bdd_diagram` got read as behaviour-driven development twice. There is no
        name-only view to skim here.
        """
        return [
            {"diagramType": name, **DIAGRAM_TYPE_GUIDE[name]}
            for name in SUPPORTED_DIAGRAM_TYPES
        ]

    def list_valid_types(self) -> list[str]:
        """Return every recognized saved type, including the non-generatable custom canvas."""
        return [*SUPPORTED_DIAGRAM_TYPES, CUSTOM_DIAGRAM]

    def is_supported(self, diagram_type: str) -> bool:
        """Return whether *diagram_type* is a supported MVP type."""
        return is_supported_diagram_type(diagram_type)

    def conforms_to_type(self, nodes, edges, diagram_type: str) -> bool:
        """Return whether every node/edge semanticType fits *diagram_type*'s allowed subset."""
        return conforms_to_type(nodes, edges, diagram_type)

    def get_type_profile(self, diagram_type: str) -> DiagramTypeProfile:
        """Return the per-type profile for *diagram_type*.

        Raises:
            ValueError: if *diagram_type* is not supported.
        """
        return get_type_profile(diagram_type)
