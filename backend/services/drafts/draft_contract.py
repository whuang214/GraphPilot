"""Result types for draft validation.

Deliberately separate from ``ValidationIssue``: that contract describes a canonical
diagram GraphPilot assembled, this one describes the input a host submitted. They never
see the same document, so sharing a shape would only invite the two to be confused.
"""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True)
class DraftFinding:
    """One reason a draft was refused, addressed to the host that wrote it."""

    code: str
    path: str
    message: str
    details: Optional[Mapping[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "code": self.code,
            "path": self.path,
            "message": self.message,
        }
        if self.details:
            payload["details"] = dict(self.details)
        return payload


@dataclass(frozen=True)
class DraftValidationResult:
    """Every reason at once.

    Findings are returned complete and sorted rather than one at a time: a host that
    has to rediscover its mistakes across successive calls pays for each one, and the
    previous surface cost five and four attempts per document exactly that way.
    """

    valid: bool
    findings: Tuple[DraftFinding, ...]

    @classmethod
    def from_findings(cls, findings: Sequence[DraftFinding]) -> "DraftValidationResult":
        ordered = tuple(sorted(findings, key=lambda item: (item.path, item.code, item.message)))
        return cls(valid=not ordered, findings=ordered)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "findings": [finding.to_dict() for finding in self.findings],
        }


#: Relationship-end policy per semantic type. ``optional`` means the host may state a
#: role or multiplicity; ``forbidden`` means the notation has no such end, so supplying
#: one is a modelling mistake and is reported rather than silently dropped.
END_POLICY: Mapping[str, Mapping[str, str]] = MappingProxyType(
    {
        "composition": MappingProxyType({"source": "optional", "target": "optional"}),
        "association": MappingProxyType({"source": "optional", "target": "optional"}),
        "generalization": MappingProxyType({"source": "forbidden", "target": "forbidden"}),
        "dependency": MappingProxyType({"source": "forbidden", "target": "optional"}),
        "commentLink": MappingProxyType({"source": "forbidden", "target": "forbidden"}),
        "controlFlow": MappingProxyType({"source": "forbidden", "target": "forbidden"}),
        "include": MappingProxyType({"source": "forbidden", "target": "forbidden"}),
        "extend": MappingProxyType({"source": "forbidden", "target": "forbidden"}),
    }
)

#: Relationship semantic types whose endpoints must both be BDD blocks.
BDD_STRUCTURAL_RELATIONSHIPS = frozenset(
    {"association", "composition", "generalization", "dependency"}
)

#: Relationships that are meaningless between an element and itself. A thing cannot be
#: its own part, its own parent, its own included behaviour, or its own annotation.
#:
#: ``association`` and ``dependency`` are deliberately absent: a self-association is
#: legitimate modelling (an Employee who manages an Employee), and so is a module that
#: depends on another version of itself.
IRREFLEXIVE_RELATIONSHIPS = frozenset(
    {"composition", "generalization", "include", "extend", "commentLink"}
)

#: The only relationship that may carry a guard.
GUARDED_RELATIONSHIP = "controlFlow"

#: Relationship fields owned by one relationship type, as ``field -> owning type``.
#:
#: ``guard`` was already refused elsewhere. ``condition`` and ``extensionLocations`` were
#: not: materialization copies them only when the relationship is an ``extend``, so on
#: anything else a host's input validated and was then dropped without a word. Same class
#: as ``features`` on a non-block — valid, accepted, and silently discarded.
SEMANTIC_SCOPED_RELATIONSHIP_FIELDS: Mapping[str, str] = MappingProxyType(
    {
        "guard": GUARDED_RELATIONSHIP,
        "condition": "extend",
        "extensionLocations": "extend",
    }
)


def scoped_relationship_fields(edge_semantic_types) -> frozenset:
    """Relationship fields no relationship of this diagram type could carry."""
    allowed = set(edge_semantic_types)
    return frozenset(
        field
        for field, owner in SEMANTIC_SCOPED_RELATIONSHIP_FIELDS.items()
        if owner not in allowed
    )

#: Element fields only one diagram type can author, as ``field -> (owning type, refusal
#: code, why)``. The validator refuses them elsewhere and the authoring contract stops
#: documenting them elsewhere, both reading this table — so a field cannot be advertised
#: to a type that will reject it.
#:
#: ``stereotype`` was already gated and keeps its own code. ``features`` and
#: ``extensionPoints`` were not: a host could author compartments on an activity node,
#: pass validation, have them persisted, and never see them drawn, because only a
#: ``classifier-box`` primitive renders a compartment. They refuse under
#: ``notation_invalid`` rather than adding two more codes to every contract; the finding's
#: path names the exact field, which is what a host acts on.
#: ``semanticType`` narrows it further. Gating on the diagram type alone left the same
#: hole one level down: a `note` inside a BDD diagram could carry `features`, validate,
#: persist, and draw nothing, because only a ``classifier-box`` renders a compartment.
#: The published refusal already says "Only a BDD **block** takes a `stereotype`", so the
#: prose was right and the check was not.
TYPE_SCOPED_ELEMENT_FIELDS: Mapping[str, Mapping[str, str]] = MappingProxyType(
    {
        "stereotype": MappingProxyType({
            "diagramType": "bdd_diagram",
            "semanticType": "block",
            "code": "stereotype_unsupported",
            "why": "A stereotype selects a BDD Block's primary heading",
        }),
        "features": MappingProxyType({
            "diagramType": "bdd_diagram",
            "semanticType": "block",
            "code": "notation_invalid",
            "why": "Compartments belong to a BDD Block",
        }),
        "extensionPoints": MappingProxyType({
            "diagramType": "use_case_diagram",
            "semanticType": "useCase",
            "code": "notation_invalid",
            "why": "Extension points belong to a use case",
        }),
    }
)


def scoped_element_fields(diagram_type: str) -> frozenset:
    """Element fields *this* type may not author."""
    return frozenset(
        field
        for field, rule in TYPE_SCOPED_ELEMENT_FIELDS.items()
        if rule["diagramType"] != diagram_type
    )
