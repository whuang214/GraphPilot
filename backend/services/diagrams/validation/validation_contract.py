"""Shared contract types for diagram validation results.

These dataclasses are used by both the Django API and the MCP server so that callers
receive the same structured response regardless of entry point.
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Severity(str, Enum):
    """Issue severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationLayer(str, Enum):
    """The validation layer that produced an issue.

    Only the four layers that live inside ``DiagramValidationService`` and emit
    issues are represented here. Layer 1 (request/file safety) and Layer 6
    (operation-specific) are enforced by the entry points and operation callers
    respectively, and surface through ``OperationProblem`` rather than as
    ``ValidationIssue`` objects. See
    ``docs/02-design-and-features/02-validation-design.md``.
    """

    SCHEMA = "schema"
    STRUCTURE = "structure"
    BLUEPRINT = "blueprint"
    RENDER_READINESS = "render_readiness"


class ValidationLevel(str, Enum):
    """Overall validation result level."""

    PASS = "pass"
    PASS_WITH_WARNINGS = "pass_with_warnings"
    FAIL = "fail"


# Schema-layer issues use a dynamic code family: ``schema_<jsonschema-keyword>``
# (e.g. ``schema_required``, ``schema_type``). The keyword comes from the
# jsonschema validator, so these codes are registered by this prefix rather than
# enumerated in :class:`ValidationCode`.
SCHEMA_CODE_PREFIX = "schema_"


class ValidationCode(str, Enum):
    """The stable ``code`` vocabulary emitted by ``DiagramValidationService``.

    One registry for every issue code the service can emit, except the dynamic
    ``schema_*`` family (see :data:`SCHEMA_CODE_PREFIX`). Codes are part of the
    published contract: treat existing values as stable — add new members rather
    than renaming, and mirror any change in the issue-code table in
    ``docs/02-design-and-features/02-validation-design.md``.
    """

    # Schema layer (fixed codes; the dynamic ``schema_*`` family is separate).
    INVALID_ROOT_TYPE = "invalid_root_type"
    NON_FINITE_NUMBER = "non_finite_number"

    # Structural graph layer.
    NO_NODES = "no_nodes"
    DUPLICATE_NODE_ID = "duplicate_node_id"
    MISSING_NODE_PARENT = "missing_node_parent"
    CYCLIC_NODE_PARENT = "cyclic_node_parent"
    EMPTY_NODE_LABEL = "empty_node_label"
    INVALID_POSITION = "invalid_position"
    INVALID_SIZE = "invalid_size"
    INVALID_MULTIPLICITY = "invalid_multiplicity"
    DUPLICATE_EDGE_ID = "duplicate_edge_id"
    MISSING_EDGE_SOURCE = "missing_edge_source"
    MISSING_EDGE_TARGET = "missing_edge_target"
    NO_EDGES = "no_edges"
    DISCONNECTED_NODE = "disconnected_node"
    OVERLAPPING_POSITION = "overlapping_position"
    HIGH_NODE_COUNT = "high_node_count"
    HIGH_EDGE_COUNT = "high_edge_count"

    # Advisory blueprint/type layer.
    UNSUPPORTED_DIAGRAM_TYPE = "unsupported_diagram_type"
    BLUEPRINT_KEY_MISMATCH = "blueprint_key_mismatch"
    UNEXPECTED_NODE_TYPE = "unexpected_node_type"
    UNEXPECTED_NODE_SEMANTIC_TYPE = "unexpected_node_semantic_type"
    UNEXPECTED_NODE_STEREOTYPE = "unexpected_node_stereotype"
    UNEXPECTED_EDGE_SEMANTIC_TYPE = "unexpected_edge_semantic_type"
    UNEXPECTED_EDGE_STEREOTYPE = "unexpected_edge_stereotype"

    # Structural well-formedness (the per-type critic, advisory) — surfaced in Layer 4.
    STRUCTURAL_CONSTRAINT = "structural_constraint"

    # Render-readiness layer.
    LONG_LABEL = "long_label"
    LABEL_TRUNCATED = "label_truncated"
    INVALID_STYLE = "invalid_style"

    @classmethod
    def is_registered(cls, code: str) -> bool:
        """Return whether *code* is known: a member value or a ``schema_*`` code."""
        if code.startswith(SCHEMA_CODE_PREFIX):
            return True
        return code in cls._value2member_map_


@dataclass
class ValidationIssue:
    """A single validation issue."""

    severity: Severity
    layer: ValidationLayer
    code: str
    message: str
    path: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class ValidationStats:
    """Optional statistics returned with a validation result."""

    node_count: int = 0
    edge_count: int = 0


@dataclass
class ValidationResult:
    """Structured result returned by the validation path."""

    valid: bool
    level: ValidationLevel
    summary: str
    issues: List[ValidationIssue] = field(default_factory=list)
    stats: Optional[ValidationStats] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-friendly dict.

        Enum values are serialized as strings, and ``stats`` is emitted with
        camelCase keys (``nodeCount``/``edgeCount``) to match the rest of the
        JSON contract.
        """
        data = asdict(self)
        data["level"] = self.level.value
        for issue in data.get("issues", []):
            issue["severity"] = issue["severity"].value
            issue["layer"] = issue["layer"].value
        if data.get("stats") is not None:
            data["stats"] = {
                "nodeCount": self.stats.node_count,
                "edgeCount": self.stats.edge_count,
            }
        return data

    @classmethod
    def from_issues(
        cls,
        issues: Optional[List[ValidationIssue]] = None,
        *,
        stats: Optional[ValidationStats] = None,
    ) -> "ValidationResult":
        """Build a result by deriving ``valid``, ``level``, and ``summary`` from *issues*.

        - any ``error`` issue produces ``valid=False`` and level ``fail``
        - only ``warning``/``info`` issues produce ``valid=True`` and level
          ``pass_with_warnings``
        - no issues produce ``valid=True`` and level ``pass``
        """
        issues = issues or []
        error_count = sum(1 for issue in issues if issue.severity == Severity.ERROR)
        warning_count = sum(1 for issue in issues if issue.severity == Severity.WARNING)

        if error_count:
            level = ValidationLevel.FAIL
            valid = False
            summary = f"Diagram failed validation with {error_count} error(s)."
        elif warning_count:
            level = ValidationLevel.PASS_WITH_WARNINGS
            valid = True
            summary = f"Diagram passed validation with {warning_count} warning(s)."
        else:
            level = ValidationLevel.PASS
            valid = True
            summary = "Diagram passed validation."

        return cls(valid=valid, level=level, summary=summary, issues=issues, stats=stats)
