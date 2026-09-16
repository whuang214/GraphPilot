"""Tell a host exactly how to author a draft for one diagram type.

Everything here is **derived**, never hand-maintained: the vocabulary comes from the type
profile, the shape and worked example from ``diagram-draft.json``, and the relationship
rules from the same ``END_POLICY`` table the validator enforces. A contract that was
written out by hand would drift from the code that rejects drafts, and the host would be
told one thing and refused for another.

Per-type prose lives beside the type in ``assets/blueprints/<type>/authoring.md``.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from django.conf import settings

from services.diagrams.catalog.diagram_types import (
    DIAGRAM_TYPE_MEANINGS,
    SUPPORTED_DIAGRAM_TYPES,
    get_type_profile,
)
from services.diagrams.catalog.constants import LONG_LABEL_LENGTH
from services.diagrams.catalog.element_catalog import (
    ELEMENT_CATALOG,
    container_semantic_types,
)
from services.diagrams.validation.structural_constraints import EXTEND_LOCATION_RULE
from services.drafts.draft_contract import (
    END_POLICY,
    GUARDED_RELATIONSHIP,
    scoped_element_fields,
    scoped_relationship_fields,
)
from services.shared.schema_registry import SchemaRegistry

_DRAFT_SCHEMA_KEY = "diagram_draft"

#: How a relationship's ends behave, in the host's terms rather than the validator's.
_END_PROSE = {
    "optional": "may carry a role and multiplicity",
    "forbidden": "carries none",
}

#: Ends whose role and multiplicity carry the most meaning, called out so a host states
#: them. The marker itself always comes from the relationship type, never from the data.
_SIGNIFICANT_END = {"composition": "source"}


class AuthoringContractService:
    def __init__(self, schema_registry: Optional[SchemaRegistry] = None) -> None:
        self._schemas = schema_registry or SchemaRegistry()

    @staticmethod
    def supported_types() -> Tuple[str, ...]:
        return tuple(SUPPORTED_DIAGRAM_TYPES)

    def build(self, diagram_type: str) -> Dict[str, Any]:
        """Return the machine-readable authoring contract for *diagram_type*."""
        if diagram_type not in SUPPORTED_DIAGRAM_TYPES:
            # get_type_profile would name `custom` as supported. It is a valid canvas to
            # save and validate, but it cannot be authored as a draft, so offering it
            # here sends the host somewhere diagram_create will refuse.
            raise ValueError(
                f"Unsupported diagram type: {diagram_type!r}. "
                f"Authorable types: {', '.join(SUPPORTED_DIAGRAM_TYPES)}."
            )
        profile = get_type_profile(diagram_type)
        schema = self._schemas.get_schema(_DRAFT_SCHEMA_KEY)
        purposes = dict(_ENVELOPE)
        contract: Dict[str, Any]
        scoped_out = {
            "element": scoped_element_fields(diagram_type),
            "relationship": _scoped_relationship_fields(profile),
        }
        contract = {
            "schemaVersion": schema["$id"],
            "kind": "diagramDraft",
            # Not `diagramType`: at the top level beside `schemaVersion` and `kind`, which
            # *are* draft fields, a host read it as one, copied it, and earned an
            # `additionalProperties` refusal. The response then carried a paragraph of
            # apology for its own shape. Naming it for what it is costs nothing.
            "contractFor": diagram_type,
            "meaning": DIAGRAM_TYPE_MEANINGS[diagram_type],
            "vocabulary": {
                "elements": _catalog_entries(profile.allowed_node_semantic_types),
                "relationships": _relationship_entries(profile.allowed_edge_semantic_types),
                "containers": sorted(
                    container_semantic_types() & set(profile.allowed_node_semantic_types)
                ),
            },
            # Optional arrays included: `assumptions` was named only inside the worked
            # example, which is the one part of the contract the Markdown channel never
            # carried.
            "topLevelFields": _top_level_fields(schema),
            # Every object a host fills in, expanded from the schema. Without this the
            # worked example was the only place the envelope existed, so a host that
            # asked for one type and got `example: null` could not author at all.
            "envelope": {
                name: {
                    "purpose": purposes[name],
                    "fields": _field_rows(schema, name, scoped_out.get(name, frozenset())),
                }
                for name in _envelope_names(diagram_type, profile)
            },
            # The meaning-stage rules, stated before a host trips one. An audit found
            # 14 of 19 refusal codes explained nowhere a host could read. Shape-stage
            # refusals are generated per jsonschema keyword and are not listed here; the
            # bounds on each field row are what makes them avoidable.
            "refusals": [{"code": code, "rule": rule} for code, rule in REFUSAL_GUIDE],
            "guidance": _guidance(diagram_type),
            "example": _example_for(schema, diagram_type),
        }
        _narrow_semantic_types(contract)
        _annotate_relationship_ends(contract)
        _annotate_parent_id(contract)
        _annotate_label_budget(contract)
        _annotate_composed_labels(contract)
        _annotate_extend_fields(contract)
        return contract

    def render_summary(self, contract: Mapping[str, Any]) -> str:
        """The `content` channel: orientation, and a pointer to the contract itself.

        The contract proper is `structuredContent`. This is deliberately short. The MCP
        specification pairs a brief human-readable `content` with the data in
        `structuredContent` — its own example is a one-line summary beside a full record
        set — and rendering all 26,000 characters into both channels was the most
        expensive shape the protocol allows.

        `content` cannot simply be dropped: the spec marks it required while
        `structuredContent` is optional.

        The last paragraph earns its place. A client that does not surface
        `structuredContent` leaves a host holding orientation and no contract, and a host
        that authors from orientation alone writes a draft that fails closed on fields it
        never saw. Telling it to stop and say so converts a silent failure into a
        reported one.

        It names the keys because "can you see it?" was the wrong question. Two hosts in
        one corpus run had this payload truncated by their terminal and reassembled it
        from an overflow file across three reads; one observed that **the realistic
        failure is partial visibility, not total**, and a host reading 60% of the contract
        gets no warning at all. A count and a list are checkable; "can you see it" is a
        yes a truncated host answers honestly and wrongly.
        """
        vocabulary = contract["vocabulary"]
        return "\n".join([
            f"# Authoring a `{contract['contractFor']}` draft",
            "",
            contract["meaning"],
            "",
            f"Submit one `{contract['schemaVersion']}` document to `diagram_create`. "
            "You author the semantics; GraphPilot builds the notation, layout, and files.",
            "",
            "**The contract is this response's `structuredContent`.** It carries every "
            f"top-level field, the {len(vocabulary['elements'])} element and "
            f"{len(vocabulary['relationships'])} relationship types with the direction "
            f"each one runs, the {len(contract['refusals'])} meaning-stage rules that can "
            "refuse a draft, and a complete worked example that `diagram_create` accepts "
            "exactly as written. Shape-stage refusals are not in that table — they are "
            "`schema_<keyword>`, avoided by obeying each field row's `shape`, which "
            "carries the real length and count limits.",
            "",
            f"**Count what arrived.** `structuredContent` has {len(contract)} top-level "
            f"keys and its `envelope` has {len(contract['envelope'])} sections. If you "
            "see fewer, or none, stop and say so: this summary cannot be authored from, "
            "and a draft guessed from a partial contract fails closed on fields you "
            "never saw.",
        ])


def _narrow_semantic_types(contract: Dict[str, Any]) -> None:
    """Replace the union of every type's vocabulary with this type's own.

    `element.semanticType` advertised all twelve semantic types across all three diagram
    types, and deferred to *"the draft validator reports the exact permitted set"* — a
    tool call for something the contract already knows and states a few keys away. A cold
    host reported this as the wrong list sitting closest to the work: the field a host
    reads while authoring offered values that earn `semantic_type_unsupported`.
    """
    for section, key in (("element", "elements"), ("relationship", "relationships")):
        rows = (contract["envelope"].get(section) or {}).get("fields") or ()
        permitted = [item["semanticType"] for item in contract["vocabulary"][key]]
        for row in rows:
            if row["field"] == "semanticType":
                row["shape"] = _enum_prose(permitted)
                row["note"] = (
                    f"The {len(permitted)} {section} types "
                    f"`{contract['contractFor']}` allows. Anything else is refused "
                    "`semantic_type_unsupported`."
                )


def _annotate_label_budget(contract: Dict[str, Any]) -> None:
    """Say the length that actually matters, not just the one that refuses.

    `label` read `"short text, up to 256 characters"` — the schema's hard limit, and the
    only number offered. The number a host meets first is `LONG_LABEL_LENGTH`, less than
    half of it, and nothing stated it. In one corpus run all three hosts authored inside
    256 and were warned at 141, 139 and 134; one bisected its own labels to recover the
    threshold, and every one of those warnings landed on a diagram already saved and
    impossible to overwrite.

    Derived from the constant the validator compares against, so the two cannot drift.

    The two sections do not get the same sentence, because they do not get the same
    check. `long_label` and the box-fit check read `nodes` only, so nothing measures a
    relationship's label until it has been drawn — telling an edge author that
    `diagram_check_draft` reports it was the same overstatement this fix set out to
    remove from the `checked` list.
    """
    measured = (
        f"Over {LONG_LABEL_LENGTH} earns a `long_label` warning, and a label too big for "
        "its box earns `label_truncated`. `diagram_check_draft` reports both before "
        "anything is written."
    )
    unmeasured = (
        "Nothing measures a relationship's label before it is drawn — `long_label` and "
        "the box-fit check read elements only — so an over-long one first appears as "
        "`hard_to_read` from `diagram_create`, on a diagram that is already saved."
    )
    for section, consequence in (("element", measured), ("relationship", unmeasured)):
        for row in (contract["envelope"].get(section) or {}).get("fields") or ():
            if row["field"] != "label":
                continue
            row["note"] = (
                f"{row['note']} **Keep it under {LONG_LABEL_LENGTH} characters.** The "
                "length in `shape` is the hard limit that refuses a draft; this is the "
                f"one you meet first. {consequence}"
            ).strip()


def _annotate_composed_labels(contract: Dict[str, Any]) -> None:
    """Say what a decorated field is *drawn* as, so a host budgets the right string.

    Three authored fields are decorated before they reach the picture: `condition` gains
    a keyword and brackets, `guard` gains brackets, `stereotype` gains guillemets. The
    schema already says who writes the punctuation; none of it said how much longer the
    result is. A host budgeted a 40-character `condition` against the documented
    120-character label limit and overflowed, because what was drawn was
    `«extend» [that condition]` — 11 characters of decoration it was never told about,
    on top of any authored `label`.

    `sourceRole` + `sourceMultiplicity` already got this treatment for the same reason
    (`_annotate_relationship_ends`); this is the rest of the same defect.

    The examples are **composed by the renderer's own functions**, so a change to the
    decoration changes the contract with it. A number typed in beside them would not.
    """
    # Local: the renderer pulls in drawsvg, and a contract build has no other reason to.
    from services.diagrams.rendering.diagram_render_service import (
        edge_display_label,
        stereotype_text,
    )

    def drawn(sample: str, **data: Any) -> Tuple[str, int]:
        composed = edge_display_label({"data": data})
        return composed, len(composed) - len(sample)

    extend_example, extend_cost = drawn("your condition", semanticType="extend",
                                        condition="your condition")
    guard_example, guard_cost = drawn("your guard", semanticType="controlFlow",
                                      guard="your guard")
    stereotype_example = stereotype_text("service")
    budget = (
        f"Budget the drawn string against the {LONG_LABEL_LENGTH}-character guide, not "
        "the field you typed."
    )
    notes = {
        "relationship": {
            "condition": (
                f"Drawn inside the relationship's label as `{extend_example}` — the "
                f"keyword and brackets cost {extend_cost} characters before your text, "
                "and an authored `label` sits between them. " + budget
            ),
            "guard": (
                f"Drawn as `{guard_example}`, appended to the relationship's `label` "
                f"with a space, so the drawn string is your guard plus {guard_cost} "
                "characters plus whatever the label already carries. " + budget
            ),
        },
        "element": {
            "stereotype": (
                f"That heading — `{stereotype_example}`, "
                f"{len(stereotype_example) - len('service')} characters wider than the "
                "word you write — is drawn on its own line above the label, inside the "
                "same box. So it does not lengthen the label; it takes a line the label "
                "no longer has. Budget the label for what is left."
            ),
        },
    }
    for section, by_field in notes.items():
        for row in (contract["envelope"].get(section) or {}).get("fields") or ():
            addition = by_field.get(row["field"])
            if addition:
                row["note"] = f"{row['note']} {addition}".strip()


def _annotate_extend_fields(contract: Dict[str, Any]) -> None:
    """Publish the `extend` rule as a conditional requirement, where both fields are read.

    The schema leaves `extensionLocations` and `extensionPoints` optional and the
    structural critic then demands them, so the contract said `required: no` about a
    field a draft can be refused for omitting. A host obeyed the honesty rule — *"prefer
    omission to a guess... nothing that says 'state this' is asking you to invent"* —
    left both out, was told its `extend` "must name an extension location", and complied
    by inventing a point name its source never uses. It reported that as the rule pushing
    it across the line the honesty rules drew, and it was right.

    Same shape as `_CONDITIONALLY_REQUIRED` for top-level fields, and the rule text comes
    from the module that enforces it.
    """
    conditions = {
        "relationship": {"extensionLocations": "if `extend`"},
        "element": {"extensionPoints": "if an `extend` targets this use case"},
    }
    for section, by_field in conditions.items():
        for row in (contract["envelope"].get(section) or {}).get("fields") or ():
            need = by_field.get(row["field"])
            if not need:
                continue
            row["required"] = need
            row["note"] = f"{row['note']} {EXTEND_LOCATION_RULE}".strip()


def _annotate_relationship_ends(contract: Dict[str, Any]) -> None:
    """Say which relationships may carry an end, on the end fields themselves.

    The rule lived only in `vocabulary.relationships[].ends` — a prose string on a nested
    array item, hundreds of lines from `sourceRole`. A cold host classified those items as
    "the vocabulary blurb" and moved past them, and reported avoiding an illegal end on a
    dependency only because the source file it happened to be diagramming stated the same
    rule: *"That is luck."* Supplying a forbidden end is `notation_invalid`, so the rule
    belongs where the field is read.
    """
    rows = (contract["envelope"].get("relationship") or {}).get("fields") or ()
    permitted = {"source": [], "target": []}
    for item in contract["vocabulary"]["relationships"]:
        policy = END_POLICY.get(item["semanticType"]) or {}
        for end in permitted:
            if policy.get(end) == "optional":
                permitted[end].append(item["semanticType"])
    for row in rows:
        end = "source" if row["field"].startswith("source") else "target"
        if not row["field"].endswith(("Role", "Multiplicity", "Navigable")):
            continue
        allowed = permitted[end]
        row["note"] = (
            f"{row['note']} Only on "
            + ", ".join(f"`{name}`" for name in allowed)
            + "; on any other relationship this is `notation_invalid`."
        ).strip() if allowed else (
            f"{row['note']} No relationship in `{contract['contractFor']}` carries a "
            f"{end} end."
        ).strip()
        if row["field"].endswith(("Role", "Multiplicity")):
            # The renderer joins the two with a space, so the string that has to fit is
            # longer than either field. A host reported `payments_received 0..*` colliding
            # with two node labels and could not have predicted the length: the contract
            # documented `sourceRole` and `sourceMultiplicity` separately and never said
            # they are drawn as one label.
            row["note"] = (
                f"{row['note']} `{end}Role` and `{end}Multiplicity` are drawn as **one "
                f"label**, joined by a space — `orders 0..*`. Budget the combined length, "
                "not each field's."
            )


def _annotate_parent_id(contract: Dict[str, Any]) -> None:
    """State the containment rule on `parentId`, where a host is reading.

    It used to be a generated sentence 126 lines below the field it governs — a cold host
    reported finding it only after it had already decided. `vocabulary.containers` carries
    the same fact as data, but an empty array is a weaker thing to read than a sentence
    saying the type has no container at all.
    """
    rows = (contract["envelope"].get("element") or {}).get("fields") or ()
    containers = contract["vocabulary"]["containers"]
    rule = (
        "Only " + ", ".join(f"`{name}`" for name in containers) + " can contain another element."
        if containers
        else f"`{contract['contractFor']}` has no container element, so this is unused."
    )
    for row in rows:
        if row["field"] == "parentId":
            row["note"] = f"{row['note']} {rule}".strip()


# ---- derivation ---------------------------------------------------------------------

#: Which way each relationship runs, stated as the host must author it.
#:
#: Hand-written because it cannot be derived: `END_POLICY` records whether an end may
#: carry a role, not which end is the part. That makes this the highest-consequence table
#: in the contract with the least machine backing — a `composition` authored backwards
#: validates cleanly and asserts the opposite ownership. `test_every_relationship_states
#: _its_direction` fails if a relationship gains an `END_POLICY` entry without one here.
_DIRECTION = {
    "composition": "part → whole",
    "association": "either",
    "generalization": "child → parent",
    "dependency": "client → supplier",
    "controlFlow": "predecessor → successor",
    "include": "base → included",
    "extend": "extension → base",
    "commentLink": "note → element",
}


def _catalog_entries(semantic_types) -> List[Dict[str, str]]:
    return [
        {
            "semanticType": name,
            "description": getattr(ELEMENT_CATALOG[name], "description", "") or name,
        }
        for name in sorted(semantic_types)
        if name in ELEMENT_CATALOG
    ]


def _relationship_entries(semantic_types) -> List[Dict[str, str]]:
    entries = []
    for name in sorted(semantic_types):
        policy = END_POLICY.get(name, {})
        entries.append(
            {
                "semanticType": name,
                "description": getattr(ELEMENT_CATALOG.get(name), "description", "") or name,
                "direction": _DIRECTION.get(name, "source → target"),
                "ends": _ends_prose(name, policy),
            }
        )
    return entries


def _ends_prose(name: str, policy: Mapping[str, str]) -> str:
    if name == GUARDED_RELATIONSHIP:
        return "none; carries an optional `guard`"
    described = []
    for end in ("source", "target"):
        if policy.get(end, "forbidden") != "optional":
            continue
        if _SIGNIFICANT_END.get(name) == end:
            # "state them" read as an order, and a host reported inventing a role name to
            # obey it — the one place in six diagrams it knowingly guessed. The field is
            # worth asking for and is not worth a fabrication, so the ask now says which.
            described.append(
                f"{end}: the part's role and multiplicity — give them when the source "
                f"names them, and omit them when it does not"
            )
        else:
            described.append(f"{end}: {_END_PROSE['optional']}")
    return "; ".join(described) if described else "none"


def _top_level_fields(schema: Mapping[str, Any]) -> Dict[str, Dict[str, str]]:
    """Every top-level draft field, read off the schema rather than restated.

    Optional ones are included. `assumptions` used to appear nowhere but the worked
    example — so a host whose client renders only the Markdown could not learn that it is
    a top-level array, while `orphan_assumption` refuses a draft that fails to reference
    one.

    Each row carries its `limit` for the same reason the field tables do. `diagramName` is
    a slug of at most 64 characters, `elements` caps at 256, `relationships` at 512 — and
    none of that was anywhere a host could read it. A cold host called `diagramName` "the
    thing you can permanently spend" and then had to guess its shape.
    """
    required = set(schema["required"])
    defs = schema.get("$defs") or {}
    out: Dict[str, Dict[str, str]] = {}
    for field, spec in schema["properties"].items():
        # A `$ref` carries no description of its own, so the row fell through to "see the
        # field table for `basis`" - a table that does not exist, because only the repeated
        # structures have one. A host reported chasing it. Resolve one level and the
        # definition's own description answers instead.
        if "$ref" in spec:
            spec = {**defs.get(spec["$ref"].rsplit("/", 1)[-1], {}), **spec}
        note = (spec.get("description") or "").strip()
        # `schemaVersion` and `kind` were excluded, while the section declared itself
        # exhaustive — so the table rejected the two fields the prose above it ordered a
        # host to copy. Listing them with their constant is shorter than explaining.
        if spec.get("const") is not None:
            note = f"Always `{spec['const']}`, copied exactly."
        if not note:
            # Only ever true for a structure the envelope really does describe below.
            note = f"See the `{field}` field table below."
        if field in required:
            need = "yes"
        else:
            need = _CONDITIONALLY_REQUIRED.get(field, "no")
        limit = _bounds_of(spec)
        if spec.get("pattern"):
            limit = f"matches `{spec['pattern']}`" + (f", {limit}" if limit else "")
        out[field] = {
            "required": need,
            "array": "yes" if spec.get("type") == "array" else "no",
            "limit": limit or "none",
            "note": note,
        }
    return out


#: Top-level fields the *schema* leaves optional and a later stage then demands. Reading
#: "no" off `required` alone was a lie a host could act on: `evidence_required` refuses an
#: `as_implemented` draft that cites nothing, which is most of them.
_CONDITIONALLY_REQUIRED = {"evidence": "if `as_implemented`"}


#: The objects a host actually fills in, in the order a draft is written. Each is expanded
#: from the schema rather than described by hand: prose beside a schema is prose that
#: drifts from it, and every one of these was a documented gap a cold host hit.
_ENVELOPE = (
    ("evidence", "Each cited region of the repository. **Every entry must be referenced "
                 "by some element or relationship through `evidenceRefs`** — an "
                 "uncited entry is refused, because the saved diagram lists only the "
                 "regions it was actually built from. Empty for a `conceptual` diagram."),
    ("locator", "Where a piece of evidence is. Paths are relative to `workspaceDir`."),
    # `locator.lineRange` cross-referenced this and nothing defined it. A cold host
    # authoring from the Markdown alone guessed the shape eight times over, and every
    # citation would have failed closed as `draft_invalid` if the guess was wrong.
    ("lineRange", "The lines a citation covers. 1-based, and both ends are included."),
    ("element", "One node."),
    ("features", "A **block's** compartments — only an element whose `semanticType` is "
                 "`block` may carry them. The four are named together and have three "
                 "different shapes, so each is expanded below."),
    ("property", "One row in the properties compartment."),
    ("operation", "One row in the operations compartment."),
    ("constraint", "One row in the constraints compartment."),
    ("relationship", "One edge."),
    ("multiplicity", "How many, at one end of a relationship, or on a property."),
    ("assumption", "Something you took as true without evidence. Must be referenced by "
                   "the element or relationship that relies on it, or the draft is refused."),
)

#: Envelope sections that exist only to describe `element.features`. They go wherever
#: `features` is not authorable — an activity host was reading a section whose own purpose
#: line said "BDD only".
_FEATURE_SECTIONS = ("features", "property", "operation", "constraint")


#: Relationship fields that describe an end. Meaningless where every relationship of the
#: type forbids both ends — and worse than meaningless, since supplying one is refused
#: `notation_invalid`. Dropping them is also what lets `multiplicity` go: leaving them in
#: while removing the section they point at produced a dangling `see multiplicity`.
_END_FIELDS = frozenset(
    {"sourceRole", "targetRole", "sourceMultiplicity", "targetMultiplicity",
     "targetNavigable"}
)


def _has_ends(profile) -> bool:
    return any(
        "optional" in (END_POLICY.get(name) or {}).values()
        for name in profile.allowed_edge_semantic_types
    )


def _scoped_relationship_fields(profile) -> frozenset:
    """Relationship fields no relationship of this type could carry.

    Two sources, same idea: an end nothing may state, and a field owned by a relationship
    type this diagram does not have. A BDD contract stops describing `guard`, `condition`
    and `extensionLocations`; an activity contract stops describing roles and
    multiplicities.
    """
    scoped = set(scoped_relationship_fields(profile.allowed_edge_semantic_types))
    if not _has_ends(profile):
        scoped |= _END_FIELDS
    return frozenset(scoped)


def _envelope_names(diagram_type: str, profile) -> Tuple[str, ...]:
    """The envelope sections this diagram type can actually author.

    Derived, never listed: `features` follows the same table the validator refuses on, and
    `multiplicity` follows `END_POLICY` — an activity diagram has no relationship end and
    no properties, so nothing in it can carry one.
    """
    scoped_out = scoped_element_fields(diagram_type)
    has_features = "features" not in scoped_out
    has_ends = _has_ends(profile)
    dropped = set()
    if not has_features:
        dropped.update(_FEATURE_SECTIONS)
    if not (has_features or has_ends):
        dropped.add("multiplicity")
    return tuple(name for name, _purpose in _ENVELOPE if name not in dropped)


#: Every *meaning-stage* way a draft can be refused, and the rule behind it — stated
#: *before* a host trips it. `orphan_evidence` was a hard refusal explained nowhere, and
#: all three cold hosts discovered it by being refused; an audit then found fourteen more
#: in the same state. A rule a host can only learn by failing is a rule the contract has
#: not stated.
#:
#: Shape-stage refusals are deliberately absent. They are generated one per jsonschema
#: keyword, so no fixed list can be complete, and the contract used to claim this table
#: held *"all N rules that can refuse a draft"* while a host was refused `schema_maxLength`
#: for a limit stated nowhere. The answer is not a longer table: it is that every field
#: row now carries its own bounds, so the rule arrives attached to the field it governs.
#:
#: `test_every_refusal_code_is_explained` fails when a code is added without a line here,
#: so this cannot drift back out of date.
REFUSAL_GUIDE: Tuple[Tuple[str, str], ...] = (
    ("requests_invalid", "`requests` is the wrong length, or an earlier entry changed. "
                         "A **create** carries exactly one. An **edit** carries the list "
                         "`diagram_read` gave you with exactly one appended, and the "
                         "earlier entries must come back unchanged \u2014 they are the record "
                         "of why the diagram looks the way it does."),
    ("basis_stale", "The diagram changed after `diagram_read`, or your draft has no "
                    "`basis` at all. An update submits the whole diagram, so one written "
                    "from a stale read deletes everything it does not mention. Read it "
                    "again and re-apply your change."),
    ("diagram_crossed", "The diagram holds elements from more than one diagram type, so "
                        "its type is `custom` and no draft can describe it. It can still "
                        "be edited in the browser."),
    ("duplicate_id", "Two items share an `id`. Ids are unique across the whole draft, "
                     "not just within their own list."),
    ("unresolved_reference", "A `source`, `target`, `parentId` or `evidenceRefs` names "
                             "something that is not in this draft."),
    ("evidence_required", "`authority: as_implemented` claims the diagram reflects the "
                          "source, so it must cite some."),
    ("evidence_unexpected", "`authority: conceptual` claims nothing about the repository, "
                            "so `evidence` must be empty."),
    ("assurance_unsupported", "`grounded` needs `evidenceRefs`; `assumed` needs an "
                              "`assumptionRef`; `conceptual` is only legal in a conceptual "
                              "diagram, where every element must use it."),
    ("semantic_type_unsupported", "The element or relationship type is not in this diagram "
                                  "type's vocabulary. The contract lists what is."),
    ("stereotype_unsupported", "Only a BDD block takes a `stereotype`."),
    ("containment_unsupported", "That `parentId` names an element that cannot contain "
                                "anything. The contract names the containers."),
    ("notation_invalid", "The notation forbids it — an end on a relationship that has "
                         "none, a self-referential composition, a guard on something that "
                         "is not a control flow, a `commentLink` with no note, or "
                         "compartments on an element that is not a block."),
    ("guard_required", "Every branch out of a decision node needs a `guard`, or the "
                       "diagram cannot say which way it goes."),
    ("orphan_evidence", "Every `evidence` entry must be cited by some element or "
                        "relationship. The saved diagram lists only the regions it was "
                        "actually built from."),
    ("orphan_assumption", "Every `assumptions` entry must be named by some element or "
                          "relationship through `assumptionRef`."),
    ("cyclic_parent", "Containment loops back on itself."),
    ("evidence_unreadable", "A cited file cannot be read, is empty, or the line range "
                            "runs past its end or backwards. Paths are relative to "
                            "`workspaceDir`."),
    ("evidence_symbol_not_in_range", "The `symbol` is not in the lines the citation points "
                                     "at, so the citation names one thing and points at "
                                     "another."),
    ("evidence_stale", "A region cited by a *saved* diagram has changed since. Re-read it "
                       "and author the evidence again."),
    ("diagram_exists", "That `diagramName` is taken. Nothing overwrites a saved diagram, "
                       "because it may carry edits this draft knows nothing about."),
    ("draft_invalid", "The document does not match the draft schema at all — a missing "
                      "field, a wrong type, a value outside an enum. It is **not** a "
                      "count: a well-formed draft that breaks one of the rules above "
                      "comes back under that rule's own code, however many findings there "
                      "are. `draft_invalid` means the shape is wrong, so nothing further "
                      "could be checked."),
    ("hard_to_read", "A warning, not a refusal: the diagram saved, and some of its labels "
                     "are clipped, buried or overlapping. Measured from the picture that "
                     "was drawn, so it cannot reach you before the write."),
    ("structural_constraint", "A warning: the draft is legal and the diagram is wrong in a "
                              "way a reader will notice — an activity with no start node or "
                              "two of them, a decision with one branch, an `extend` naming "
                              "no extension location, a composition that does not join a "
                              "part to a whole. `diagram_check_draft` reports these before "
                              "anything is written."),
    ("long_label", "A warning: an element label past the length in that field's `shape` "
                   "note. It saves, and it usually does not fit. Reported by "
                   "`diagram_check_draft` before the write."),
    ("label_truncated", "A warning: a label the renderer cannot fit inside its element even "
                        "at the smallest font, so the picture ellipsizes it. Also reported "
                        "by `diagram_check_draft` before the write."),
    ("content_lost", "A warning, and **our** bug rather than yours: your draft was accepted "
                     "and something in it did not survive into the diagram. Nothing you can "
                     "author differently will fix it — please report it."),
)


def _field_rows(
    schema: Mapping[str, Any], def_name: str, excluded: frozenset = frozenset()
) -> List[Dict[str, str]]:
    """Expand one `$defs` object into the rows a host needs to author it.

    Everything here is read from the schema: which fields are required, their types, their
    enums, their patterns. The contract used to say *"See the `request` section of the
    draft contract"* — a document that does not exist — and the only place the envelope was
    written down was the worked example. Three cold hosts guessed; one spent three of its
    four refusals on `assumptions` alone, whose four required fields appeared nowhere.

    *excluded* drops fields this diagram type may not author, so the contract never
    advertises something the validator will refuse.
    """
    defs = schema.get("$defs") or {}
    body = defs.get(def_name) or {}
    required = set(body.get("required") or ())
    rows: List[Dict[str, str]] = []
    for field, spec in (body.get("properties") or {}).items():
        if field in excluded:
            continue
        rows.append(
            {
                "field": field,
                "required": "yes" if field in required else "no",
                "shape": _shape_of(spec, defs),
                "note": _note_of(spec, defs),
            }
        )
    # Required first: a host reads far enough to author, and what it must supply should
    # not be interleaved with what it may.
    rows.sort(key=lambda row: (row["required"] != "yes", row["field"]))
    return rows


#: Named scalars whose `$ref` name says more than their pattern does. An id keeps its
#: pattern, because the required prefix is the thing a host gets wrong.
_SCALAR_PROSE = {
    "nonBlankText": "text, not blank",
    "shortText": "short text",
}


def _bounds_of(spec: Mapping[str, Any]) -> str:
    """The limits a host can actually trip, as a number rather than an adjective.

    `shortText` rendered as *"short text"* and the 256-character cap it names lived only
    in the schema. A cold host wrote a 271-character note label and was refused
    `schema_maxLength` — a code the refusal table deliberately does not carry, describing
    a limit the contract never stated. **"Short" is not a number**, and the host had no
    way to comply with one it was never given.

    Read off the schema rather than written beside it, so a bound cannot be changed in one
    place and documented in the other.
    """
    parts: List[str] = []
    low, high = spec.get("minLength"), spec.get("maxLength")
    if high:
        parts.append(
            f"{low} to {high} characters" if low and low > 1 else f"up to {high} characters"
        )
    low_items, high_items = spec.get("minItems"), spec.get("maxItems")
    if high_items:
        parts.append(
            f"{low_items} to {high_items} entries"
            if low_items
            else f"up to {high_items} entries"
        )
    return ", ".join(parts)


def _with_bounds(shape: str, spec: Mapping[str, Any]) -> str:
    bounds = _bounds_of(spec)
    return f"{shape}, {bounds}" if bounds and shape else shape or bounds


def _shape_of(spec: Mapping[str, Any], defs: Mapping[str, Any]) -> str:
    """One phrase for what a value must look like, resolved through `$ref`.

    Table-safe: an enum renders with `or` rather than a pipe, because a pipe inside a
    Markdown cell ends the column and silently mangles the row that documents it.
    """
    ref = str(spec.get("$ref") or "").rsplit("/", 1)[-1]
    if ref:
        target = defs.get(ref) or {}
        if target.get("enum"):
            return _enum_prose(target["enum"])
        if target.get("properties"):
            return f"object — see `{ref}`"
        return _with_bounds(_SCALAR_PROSE.get(ref) or _scalar_shape(target) or ref, target)
    if spec.get("enum"):
        return _enum_prose(spec["enum"])
    if spec.get("anyOf"):
        # `multiplicity.upper` is an integer or the exact string "*". Falling through here
        # printed "value", which is how the one encoding for "many" stayed invisible.
        return " or ".join(
            _shape_of(option, defs) for option in spec["anyOf"]
        ) or "value"
    if spec.get("type") == "array":
        item = spec.get("items") or {}
        item_ref = str(item.get("$ref") or "").rsplit("/", 1)[-1]
        if item_ref and (defs.get(item_ref) or {}).get("properties"):
            return _with_bounds(f"array of `{item_ref}` objects", spec)
        return _with_bounds(
            f"array of {_shape_of(item, defs) if item else 'value'}", spec
        )
    return _with_bounds(_scalar_shape(spec) or str(spec.get("type") or "value"), spec)


def _note_of(spec: Mapping[str, Any], defs: Mapping[str, Any]) -> str:
    """The field's own description, or the one on what it points at.

    `element.assurance` is a bare `$ref`, and the rule a host most needs — grounded needs
    evidence, assumed needs an assumption — lives on the target. Without this it showed a
    three-value enum and no hint that the values carry obligations.
    """
    own = (spec.get("description") or "").strip()
    if own:
        return own
    ref = str(spec.get("$ref") or "").rsplit("/", 1)[-1]
    if ref:
        return ((defs.get(ref) or {}).get("description") or "").strip()
    return ""


def _enum_prose(values) -> str:
    quoted = [f"`{value}`" for value in values]
    if len(quoted) == 1:
        return quoted[0]
    return ", ".join(quoted[:-1]) + " or " + quoted[-1]


def _scalar_shape(spec: Mapping[str, Any]) -> str:
    kind = spec.get("type")
    if isinstance(kind, list):
        return " or ".join(str(entry) for entry in kind)
    if spec.get("pattern"):
        return f"string matching `{spec['pattern']}`"
    return str(kind) if kind else ""


def _guidance(diagram_type: str) -> List[Dict[str, Any]]:
    """The per-type prose, as sections rather than one string.

    It used to ship as a single 1,759-character value holding a whole Markdown document,
    pipe tables included. A cold host reading the JSON channel had its reader truncate
    that value and could not recover it by line, because the entire document was one
    line — and what it lost included *"prefer the weaker true relationship"*, the rule
    that decided five of its seven edges. Sections truncate gracefully; a table read as
    rows beats a table read as `| --- |`.
    """
    path = Path(settings.BASE_DIR) / "assets" / "blueprints" / diagram_type / "authoring.md"
    sections: List[Dict[str, Any]] = []
    heading = ""
    buffer: List[str] = []

    def flush() -> None:
        body = "\n".join(buffer).strip()
        if not (heading or body):
            return
        section: Dict[str, Any] = {"heading": heading}
        rows = _markdown_table(body)
        # Whatever the table and the bullets do not account for is still prose, and
        # dropping it would repeat the defect this whole rewrite is chasing: the bdd
        # section that holds the "choosing" table also holds "prefer the weaker true
        # relationship", which is the rule a host actually acts on.
        remainder, points = [], []
        continuation = False
        for line in body.splitlines():
            if line.strip().startswith("|"):
                continuation = False
                continue
            if line.startswith("- "):
                points.append(line[2:].strip())
                continuation = True
            elif continuation and line.startswith("  ") and line.strip():
                points[-1] += " " + line.strip()
            else:
                continuation = False
                remainder.append(line)
        if rows:
            section["table"] = rows
        if points:
            section["points"] = points
        text = "\n".join(remainder).strip()
        if text:
            section["text"] = text
        sections.append(section)

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            flush()
            heading, buffer = line.lstrip("#").strip(), []
        else:
            buffer.append(line)
    flush()
    return sections


def _markdown_table(body: str) -> List[Dict[str, str]]:
    """Read a simple pipe table into rows, or return nothing if there is not one."""
    lines = [line.strip() for line in body.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3 or set(lines[1].replace("|", "").replace(" ", "")) - {"-", ":"}:
        return []
    cells = lambda line: [c.strip() for c in line.strip("|").split("|")]  # noqa: E731
    header = cells(lines[0])
    return [dict(zip(header, cells(line))) for line in lines[2:] if len(cells(line)) == len(header)]


def _example_for(schema: Mapping[str, Any], diagram_type: str) -> Optional[Dict[str, Any]]:
    """The worked example a host is served for this type.

    Read from `assets/blueprints/<type>/examples/training/`, which is where every other
    example lives and where the review gallery draws them from. Serving one from a
    different place than the one a reviewer looks at is how a teaching example rots
    unnoticed.

    The draft schema's own `examples` remain the fallback: they are what a JSON-schema
    reader sees, and a type whose training example is missing must still return something
    — the example is the only place the draft envelope is written down, so returning
    nothing leaves a host unable to author at all.
    """
    trained = _training_draft(diagram_type)
    if trained is not None:
        return trained
    for example in schema.get("examples") or ():
        if example.get("request", {}).get("diagramType") == diagram_type:
            return example
    return None


def _training_draft(diagram_type: str) -> Optional[Dict[str, Any]]:
    base = Path(settings.BASE_DIR) / "assets" / "blueprints" / diagram_type / "examples" / "training"
    for draft_path in sorted(base.glob("*/draft.json")):
        try:
            draft = json.loads(draft_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if draft.get("diagramType") == diagram_type:
            return draft
    return None
