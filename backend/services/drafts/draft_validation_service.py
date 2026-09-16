"""Validate a host-authored diagram draft before anything is read or written.

Everything here is deterministic and free. The service answers one question — *is this
draft authorable, resolvable, and legal notation for its diagram type?* — and answers it
completely, so a host fixes every mistake in one pass.

It never repairs, coerces, or drops. An off-vocabulary semantic type is refused rather
than silently replaced by a default; a relationship end the notation forbids is refused
rather than deleted. Both would hide a real modelling error behind a diagram that looks
fine.
"""

from typing import Any, Dict, List, Mapping, Optional, Sequence

from jsonschema import Draft202012Validator

from services.diagrams.catalog.diagram_types import get_type_profile
from services.diagrams.catalog.element_catalog import container_semantic_types
from services.drafts.draft_contract import (
    BDD_STRUCTURAL_RELATIONSHIPS,
    END_POLICY,
    GUARDED_RELATIONSHIP,
    IRREFLEXIVE_RELATIONSHIPS,
    SEMANTIC_SCOPED_RELATIONSHIP_FIELDS,
    TYPE_SCOPED_ELEMENT_FIELDS,
    DraftFinding,
    DraftValidationResult,
)
from services.drafts.draft_safety import secret_findings, size_findings
from services.shared.schema_registry import SchemaRegistry

_DRAFT_SCHEMA_KEY = "diagram_draft"



def _is_edit(draft: Mapping[str, Any]) -> bool:
    """Whether this draft came from reading a saved diagram.

    `basis` is written by the read and absent on a create, which is based on nothing - so
    its presence is what tells a create-only rule to stand down. Two rules need it:

    * **the request log.** A create carries exactly one ask; an edit carries the saved list
      plus one. Only the write can check the second, because only it has the saved list.
    * **`user` assurance.** A host may never author one, but the projection hands one back
      for every element a person drew, and refusing it here would make those diagrams
      uneditable.

    Neither check is waived, only moved: `DiagramUpdateService` runs both against the file
    on disk, which is the only place the answer exists.
    """
    return bool(draft.get("basis"))


class DraftValidationService:
    def __init__(self, schema_registry: Optional[SchemaRegistry] = None) -> None:
        self._schemas = schema_registry or SchemaRegistry()

    def validate(self, draft: Any) -> DraftValidationResult:
        """Every reason this draft cannot become a diagram, in one pass where possible.

        **The staging is the contract, not an implementation detail.** Three gates return
        early and alone — not a JSON object, past the size bound, or failing the schema —
        because everything after them indexes into fields the schema has not vouched for,
        and reporting both layers together buries the cause under its own consequences. A
        host that supplies a malformed `elements` array should be told that, not handed
        forty reference errors caused by it.

        The cost is real and is why `draft_invalid` reads the way it does: a field that is
        both absent *and* would break a rule reports twice, one call apart. That is two
        rounds by design, and neither costs anything, because a refusal writes nothing and
        does not consume the diagram name.

        After the schema passes, the meaning layers all run and their findings accumulate,
        so one call reports everything that is wrong at that level.
        """
        if not isinstance(draft, Mapping):
            return DraftValidationResult.from_findings(
                [DraftFinding("draft_invalid", "$", "A draft must be a JSON object.")]
            )

        oversize = size_findings(draft)
        if oversize:
            # Refuse before walking a document that is already past the bound.
            return DraftValidationResult.from_findings(oversize)

        schema_findings = self._schema_findings(draft)
        if schema_findings:
            # Structure first: reference and notation checks below index into fields the
            # schema has not yet vouched for, and reporting both layers at once would
            # bury the real cause under consequences of it.
            return DraftValidationResult.from_findings(schema_findings)

        findings: List[DraftFinding] = list(secret_findings(draft))
        findings.extend(self._identity_findings(draft))
        findings.extend(self._request_findings(draft))
        findings.extend(self._reference_findings(draft))
        findings.extend(self._authority_findings(draft))
        findings.extend(self._assurance_findings(draft))
        findings.extend(self._vocabulary_findings(draft))
        findings.extend(self._notation_findings(draft))
        return DraftValidationResult.from_findings(findings)

    # ---- layers -----------------------------------------------------------------

    def _schema_findings(self, draft: Mapping[str, Any]) -> List[DraftFinding]:
        schema = self._schemas.checked_schema(_DRAFT_SCHEMA_KEY)
        validator = Draft202012Validator(schema, registry=self._schemas.reference_registry())
        return [
            DraftFinding(
                f"schema_{error.validator}",
                _json_path(error.absolute_path),
                _schema_message(error),
            )
            for error in validator.iter_errors(draft)
        ]

    @staticmethod
    def _request_findings(draft: Mapping[str, Any]) -> List[DraftFinding]:
        """A new diagram is asked for once.

        The list is append-only and the saved diagram keeps it, so creating one takes
        exactly one entry. Editing takes the list back plus one, and that comparison needs
        the saved diagram — it belongs to the update path, not here.
        """
        if _is_edit(draft):
            return []
        requests = draft.get("requests") or ()
        if len(requests) == 1:
            return []
        return [
            DraftFinding(
                "requests_invalid",
                "$.requests",
                f"A new diagram is asked for once; this carries {len(requests)} entries. "
                "Send only the ask that produced it. Adding to the list is what editing "
                "an existing diagram does.",
                {"count": len(requests)},
            )
        ]

    @staticmethod
    def _identity_findings(draft: Mapping[str, Any]) -> List[DraftFinding]:
        findings: List[DraftFinding] = []
        for section in ("elements", "relationships", "evidence", "assumptions"):
            seen: Dict[str, int] = {}
            for index, item in enumerate(draft.get(section) or ()):
                identifier = item["id"]
                if identifier in seen:
                    findings.append(
                        DraftFinding(
                            "duplicate_id",
                            f"$.{section}[{index}].id",
                            f"'{identifier}' is already used by {section}[{seen[identifier]}]. "
                            "IDs are stable and reach the canonical diagram unchanged, so they must be unique.",
                        )
                    )
                else:
                    seen[identifier] = index

        # Element and relationship IDs share the canonical ID space.
        element_ids = {item["id"] for item in draft.get("elements") or ()}
        for index, relationship in enumerate(draft.get("relationships") or ()):
            if relationship["id"] in element_ids:
                findings.append(
                    DraftFinding(
                        "duplicate_id",
                        f"$.relationships[{index}].id",
                        f"'{relationship['id']}' is also an element ID. Nodes and edges share "
                        "one canonical ID space, so the two cannot collide.",
                    )
                )
        return findings

    @staticmethod
    def _reference_findings(draft: Mapping[str, Any]) -> List[DraftFinding]:
        findings: List[DraftFinding] = []
        elements = list(draft.get("elements") or ())
        element_ids = {item["id"] for item in elements}
        evidence_ids = {item["id"] for item in draft.get("evidence") or ()}
        assumption_ids = {item["id"] for item in draft.get("assumptions") or ()}

        for index, element in enumerate(elements):
            parent = element.get("parentId")
            if parent is not None and parent not in element_ids:
                findings.append(
                    DraftFinding(
                        "unresolved_reference",
                        f"$.elements[{index}].parentId",
                        f"'{parent}' is not an element in this draft.",
                    )
                )
            if parent == element["id"]:
                findings.append(
                    DraftFinding(
                        "cyclic_parent",
                        f"$.elements[{index}].parentId",
                        f"'{element['id']}' cannot contain itself.",
                    )
                )

        findings.extend(_parent_cycle_findings(elements))

        for index, relationship in enumerate(draft.get("relationships") or ()):
            for end in ("source", "target"):
                if relationship[end] not in element_ids:
                    findings.append(
                        DraftFinding(
                            "unresolved_reference",
                            f"$.relationships[{index}].{end}",
                            f"'{relationship[end]}' is not an element in this draft.",
                        )
                    )

        for section, items in (("elements", draft.get("elements") or ()), ("relationships", draft.get("relationships") or ())):
            for index, item in enumerate(items):
                for ref_index, ref in enumerate(item.get("evidenceRefs") or ()):
                    if ref not in evidence_ids:
                        findings.append(
                            DraftFinding(
                                "unresolved_reference",
                                f"$.{section}[{index}].evidenceRefs[{ref_index}]",
                                f"'{ref}' is not an evidence record in this draft.",
                            )
                        )
                assumption_ref = item.get("assumptionRef")
                if assumption_ref is not None and assumption_ref not in assumption_ids:
                    findings.append(
                        DraftFinding(
                            "unresolved_reference",
                            f"$.{section}[{index}].assumptionRef",
                            f"'{assumption_ref}' is not an assumption in this draft.",
                        )
                    )

        findings.extend(_orphan_findings(draft))
        return findings

    @staticmethod
    def _authority_findings(draft: Mapping[str, Any]) -> List[DraftFinding]:
        authority = draft["authority"]
        evidence = draft.get("evidence") or ()
        if authority == "as_implemented" and not evidence:
            return [
                DraftFinding(
                    "evidence_required",
                    "$.evidence",
                    "authority 'as_implemented' claims the diagram reflects the current source, "
                    "so it must cite at least one evidence record. Use 'conceptual' for a design "
                    "that makes no claim about this repository.",
                )
            ]
        if authority == "conceptual" and evidence:
            return [
                DraftFinding(
                    "evidence_unexpected",
                    "$.evidence",
                    "authority 'conceptual' makes no claim about the repository, so it cites no "
                    "evidence. Use 'as_implemented' to ground the diagram in source.",
                )
            ]
        return []

    @staticmethod
    def _assurance_findings(draft: Mapping[str, Any]) -> List[DraftFinding]:
        findings: List[DraftFinding] = []
        authority = draft["authority"]
        for section in ("elements", "relationships"):
            for index, item in enumerate(draft.get(section) or ()):
                assurance = item["assurance"]
                path = f"$.{section}[{index}].assurance"
                if assurance == "user" and not _is_edit(draft):
                    # A claim about who drew something, not about how well grounded it is.
                    # Only the editor can make it true, so a host authoring one states a
                    # fact about the world it is not in a position to know. On an edit it
                    # may carry one back unchanged \u2014 that is checked at the write,
                    # against the diagram on disk, because only there does "unchanged"
                    # have an answer.
                    findings.append(
                        DraftFinding(
                            "assurance_unsupported",
                            path,
                            "'user' means a person drew this in the editor, so you cannot "
                            "author one. Use 'grounded' with evidenceRefs, or 'assumed' "
                            "with an assumptionRef.",
                        )
                    )
                    continue
                if assurance == "grounded" and not item.get("evidenceRefs"):
                    findings.append(
                        DraftFinding(
                            "assurance_unsupported",
                            path,
                            "'grounded' asserts the repository establishes this, so it requires at "
                            "least one evidenceRefs entry. Use 'assumed' with an assumptionRef for "
                            "a judgement the source does not establish.",
                        )
                    )
                if assurance == "assumed" and not item.get("assumptionRef"):
                    findings.append(
                        DraftFinding(
                            "assurance_unsupported",
                            path,
                            "'assumed' requires an assumptionRef naming the accepted proposition, "
                            "so a reader can see what was taken on trust.",
                        )
                    )
                if assurance == "conceptual" and authority != "conceptual":
                    findings.append(
                        DraftFinding(
                            "assurance_unsupported",
                            path,
                            "'conceptual' is only available when request.authority is 'conceptual'.",
                        )
                    )
                if assurance not in ("conceptual", "user") and authority == "conceptual":
                    findings.append(
                        DraftFinding(
                            "assurance_unsupported",
                            path,
                            "A conceptual diagram cites no repository evidence, so every element and "
                            "relationship in it is 'conceptual'.",
                        )
                    )
        return findings

    @staticmethod
    def _vocabulary_findings(draft: Mapping[str, Any]) -> List[DraftFinding]:
        diagram_type = draft["diagramType"]
        profile = get_type_profile(diagram_type)
        findings: List[DraftFinding] = []

        for index, element in enumerate(draft.get("elements") or ()):
            semantic = element["semanticType"]
            if semantic not in profile.allowed_node_semantic_types:
                findings.append(
                    DraftFinding(
                        "semantic_type_unsupported",
                        f"$.elements[{index}].semanticType",
                        f"'{semantic}' is not an element type of {diagram_type}. "
                        f"Permitted: {_listed(profile.allowed_node_semantic_types)}.",
                        {"permitted": sorted(profile.allowed_node_semantic_types)},
                    )
                )
        for index, relationship in enumerate(draft.get("relationships") or ()):
            semantic = relationship["semanticType"]
            if semantic not in profile.allowed_edge_semantic_types:
                findings.append(
                    DraftFinding(
                        "semantic_type_unsupported",
                        f"$.relationships[{index}].semanticType",
                        f"'{semantic}' is not a relationship type of {diagram_type}. "
                        f"Permitted: {_listed(profile.allowed_edge_semantic_types)}.",
                        {"permitted": sorted(profile.allowed_edge_semantic_types)},
                    )
                )

        # An element field owned by another diagram type, or by another element within
        # this one. Refused rather than dropped: `features` and `extensionPoints` used to
        # validate, persist, and then go undrawn, because only the owning element's
        # primitive renders them.
        for field, rule in sorted(TYPE_SCOPED_ELEMENT_FIELDS.items()):
            wrong_diagram = rule["diagramType"] != diagram_type
            for index, element in enumerate(draft.get("elements") or ()):
                if element.get(field) is None:
                    continue
                if wrong_diagram:
                    reason = f"{diagram_type} has none."
                elif element["semanticType"] != rule["semanticType"]:
                    reason = f"a {element['semanticType']} is not a {rule['semanticType']}."
                else:
                    continue
                findings.append(
                    DraftFinding(rule["code"], f"$.elements[{index}].{field}", f"{rule['why']}; {reason}")
                )

        # Only some element kinds can visually contain another. Naming a non-container
        # parent would otherwise be dropped in silence and the diagram would come back
        # flat with no explanation.
        containers = container_semantic_types()
        by_id = {item["id"]: item for item in draft.get("elements") or ()}
        for index, element in enumerate(draft.get("elements") or ()):
            parent = by_id.get(element.get("parentId") or "")
            if parent is not None and parent["semanticType"] not in containers:
                permitted = sorted(containers & set(profile.allowed_node_semantic_types))
                findings.append(
                    DraftFinding(
                        "containment_unsupported",
                        f"$.elements[{index}].parentId",
                        f"A {parent['semanticType']} cannot contain another element. "
                        + (
                            f"In {diagram_type} only {_listed(permitted)} can."
                            if permitted
                            else f"{diagram_type} has no container element."
                        ),
                        {"permitted": permitted},
                    )
                )
        return findings

    @staticmethod
    def _notation_findings(draft: Mapping[str, Any]) -> List[DraftFinding]:
        diagram_type = draft["diagramType"]
        elements = {item["id"]: item for item in draft.get("elements") or ()}
        relationships = list(draft.get("relationships") or ())
        findings: List[DraftFinding] = []

        for index, relationship in enumerate(relationships):
            semantic = relationship["semanticType"]
            policy = END_POLICY.get(semantic)
            if policy is not None:
                for end in ("source", "target"):
                    if policy[end] != "forbidden":
                        continue
                    for suffix in ("Role", "Multiplicity"):
                        field = f"{end}{suffix}"
                        if relationship.get(field) is not None:
                            findings.append(
                                DraftFinding(
                                    "notation_invalid",
                                    f"$.relationships[{index}].{field}",
                                    f"A {semantic} has no {end} end, so it carries no {end} "
                                    f"{suffix.lower()}. Remove the field, or use a relationship "
                                    "type whose notation has that end.",
                                )
                            )

            if semantic in IRREFLEXIVE_RELATIONSHIPS and relationship["source"] == relationship["target"]:
                findings.append(
                    DraftFinding(
                        "notation_invalid",
                        f"$.relationships[{index}]",
                        f"'{relationship['source']}' cannot be its own {semantic} counterpart. "
                        "This relationship connects two different elements.",
                    )
                )

            # A field owned by another relationship type. `condition` and
            # `extensionLocations` were copied through only for an `extend`, so anywhere
            # else they validated and were then dropped in silence.
            for field, owner in sorted(SEMANTIC_SCOPED_RELATIONSHIP_FIELDS.items()):
                if relationship.get(field) is not None and semantic != owner:
                    findings.append(
                        DraftFinding(
                            "notation_invalid",
                            f"$.relationships[{index}].{field}",
                            f"Only a {owner} carries a {field}; this is a {semantic}.",
                        )
                    )

            if semantic == "commentLink":
                endpoints = [elements.get(relationship["source"]), elements.get(relationship["target"])]
                kinds = [item["semanticType"] for item in endpoints if item is not None]
                if len(kinds) == 2 and "note" not in kinds:
                    findings.append(
                        DraftFinding(
                            "notation_invalid",
                            f"$.relationships[{index}]",
                            "A commentLink attaches a note; neither endpoint is one.",
                        )
                    )

            if diagram_type == "bdd_diagram" and semantic in BDD_STRUCTURAL_RELATIONSHIPS:
                for end in ("source", "target"):
                    endpoint = elements.get(relationship[end])
                    if endpoint is not None and endpoint["semanticType"] != "block":
                        findings.append(
                            DraftFinding(
                                "notation_invalid",
                                f"$.relationships[{index}].{end}",
                                f"A {semantic} connects blocks; '{relationship[end]}' is a "
                                f"{endpoint['semanticType']}.",
                            )
                        )

        findings.extend(_decision_branch_findings(diagram_type, elements, relationships))
        return findings


# ---- helpers ---------------------------------------------------------------------


def _decision_branch_findings(
    diagram_type: str,
    elements: Mapping[str, Mapping[str, Any]],
    relationships: Sequence[Mapping[str, Any]],
) -> List[DraftFinding]:
    """A decision with more than one way out must say which way is which."""
    if diagram_type != "activity_diagram":
        return []
    outgoing: Dict[str, List[int]] = {}
    for index, relationship in enumerate(relationships):
        if relationship["semanticType"] != GUARDED_RELATIONSHIP:
            continue
        outgoing.setdefault(relationship["source"], []).append(index)

    findings: List[DraftFinding] = []
    for source, indexes in outgoing.items():
        element = elements.get(source)
        if element is None or element["semanticType"] != "decisionNode" or len(indexes) < 2:
            continue
        for index in indexes:
            if relationships[index].get("guard") is None:
                findings.append(
                    DraftFinding(
                        "guard_required",
                        f"$.relationships[{index}].guard",
                        f"'{source}' is a decision with {len(indexes)} branches, so each one needs "
                        "a guard saying when it is taken.",
                    )
                )
    return findings


def _orphan_findings(draft: Mapping[str, Any]) -> List[DraftFinding]:
    """Evidence and assumptions nobody cites.

    ``metadata.evidence`` in the saved diagram means *the regions this diagram was built
    from*. An uncited record would be persisted into that list and break the invariant,
    so it is refused rather than quietly dropped — the host either cites it or removes it.
    """
    cited_evidence: set = set()
    cited_assumptions: set = set()
    for section in ("elements", "relationships"):
        for item in draft.get(section) or ():
            cited_evidence.update(item.get("evidenceRefs") or ())
            if item.get("assumptionRef"):
                cited_assumptions.add(item["assumptionRef"])

    findings: List[DraftFinding] = []
    for index, record in enumerate(draft.get("evidence") or ()):
        if record["id"] not in cited_evidence:
            findings.append(
                DraftFinding(
                    "orphan_evidence",
                    f"$.evidence[{index}].id",
                    f"'{record['id']}' is not cited by any element or relationship. Cite it "
                    "with evidenceRefs, or remove it — the saved diagram lists only the "
                    "regions it was built from.",
                )
            )
    for index, assumption in enumerate(draft.get("assumptions") or ()):
        if assumption["id"] not in cited_assumptions:
            findings.append(
                DraftFinding(
                    "orphan_assumption",
                    f"$.assumptions[{index}].id",
                    f"'{assumption['id']}' is not named by any element or relationship. "
                    "Reference it with assumptionRef, or remove it.",
                )
            )
    return findings


def _parent_cycle_findings(elements: Sequence[Mapping[str, Any]]) -> List[DraftFinding]:
    """Report containment loops of length two or more.

    A self-parent is a loop too, but it gets its own clearer message from the caller, so
    reporting it here as well would hand the host the same path twice.
    """
    parents = {item["id"]: item.get("parentId") for item in elements}
    index_of = {item["id"]: index for index, item in enumerate(elements)}
    findings: List[DraftFinding] = []
    for start in parents:
        if parents[start] == start:
            continue
        seen = {start}
        current = parents[start]
        while current is not None and current in parents:
            if current in seen:
                findings.append(
                    DraftFinding(
                        "cyclic_parent",
                        f"$.elements[{index_of[start]}].parentId",
                        f"Containment starting at '{start}' loops back on itself.",
                    )
                )
                break
            seen.add(current)
            current = parents[current]
    return findings


def _schema_message(error) -> str:
    """State the rule that was broken, not only that something broke it.

    `jsonschema` says *"'…' is too long"* and echoes the whole offending value, which is
    the one thing the author already has. A host binary-searched `diagram_check_draft` to
    discover that a label may be 256 characters. `pattern` errors quote their regex and
    were never a problem, so the fix is to make the length and type errors match: say the
    limit, and for a length, say what was actually supplied.
    """
    rule = error.validator
    limit = error.validator_value
    if rule == "maxLength":
        return f"{_short(error.instance)} is {len(error.instance)} characters; the limit is {limit}."
    if rule == "minLength":
        return f"{_short(error.instance)} is too short; it needs at least {limit} character(s)."
    if rule == "maxItems":
        return f"{len(error.instance)} entries; at most {limit} are allowed."
    if rule == "minItems":
        return f"{len(error.instance)} entries; at least {limit} are required."
    if rule == "type":
        expected = limit if isinstance(limit, str) else " or ".join(limit)
        article = "an" if expected[:1] in "aeiou" else "a"
        message = (
            f"{_short(error.instance)} is {_article(type(error.instance).__name__)}; "
            f"{article} {expected} is required here."
        )
        # Saying "object" and stopping is what cost one host six probe drafts to learn
        # that a constraint is `{"expression": ...}`. The subschema knows the keys, so
        # naming them here turns two round trips into none.
        required = (error.schema or {}).get("required") if isinstance(error.schema, dict) else None
        if required:
            message += " Required key(s): " + ", ".join(f"`{key}`" for key in required) + "."
        return message
    return error.message


def _article(word: str) -> str:
    return ("an " if word[:1] in "aeiou" else "a ") + word


def _short(value, width: int = 60) -> str:
    """The offending value, quoted and clipped — a 258-character echo helps nobody."""
    text = value if isinstance(value, str) else repr(value)
    return repr(text if len(text) <= width else text[: width - 1] + "\u2026")


def _json_path(path) -> str:
    rendered = "$"
    for part in path:
        rendered += f"[{part}]" if isinstance(part, int) else f".{part}"
    return rendered


def _listed(values) -> str:
    return ", ".join(sorted(values))
