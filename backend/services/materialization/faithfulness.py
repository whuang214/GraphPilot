"""Did the diagram keep everything the draft said?

Every other check in the product asks whether the diagram is **legal**: does it match the
canonical schema, do the structural rules hold, is the text readable, do the citations
resolve. All of them examine the output alone.

None of them asks whether the output still says what the *input* said. So when
materialization quietly discarded a field, the result was valid, structurally clean,
legible, correctly cited — and missing data. Every badge green.

That is not hypothetical. `parameters` on an operation were accepted by the draft schema,
validated, and then dropped on the floor by canonical assembly, because the draft supplies
a string and assembly only accepted an object. A host authored them, `diagram_create`
succeeded, and the saved diagram had none. `returnType` and a constraint's `name` survived
to disk and were then never drawn. All three went unnoticed through 600 tests and three
corpus runs.

**Accepted-then-discarded is the worst of the three possible behaviours.** Refusing the
draft would at least have told the author. Silence lets them believe it landed.

## Why this compares tokens rather than fields

A field map — *"`sourceRole` becomes `data.sourceEnd.role`"* — would be hand-maintained
prose beside the transform, and would drift from it exactly as the authoring contract used
to drift from the validator. Materialization is also legitimately *reshaping*: a draft's
`"mode: Mode"` becomes `{"name": "mode", "type": "Mode"}`, so nothing survives verbatim.

So the question asked here is deliberately weaker and unmaintainable-proof: **every word
the draft wrote about an element must appear somewhere in that element's node.** Reshaping
passes. Dropping does not. No map to keep in step.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Set

_TOKEN = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class Loss:
    """Something the draft said that the diagram does not."""

    kind: str
    item_id: str
    field: str
    detail: str

    def __str__(self) -> str:
        return f"{self.kind} '{self.item_id}': {self.detail}"


def _tokens(value: Any) -> Set[str]:
    """Every word in a value, however deeply nested.

    Single characters are dropped: a multiplicity of `1` or a one-letter role carries no
    signal and matches almost anything, so requiring it would be noise in both directions.
    """
    found: Set[str] = set()
    if isinstance(value, Mapping):
        for item in value.values():
            found |= _tokens(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            found |= _tokens(item)
    elif isinstance(value, bool):
        found.add(str(value))
    elif value is not None:
        found |= {t for t in _TOKEN.findall(str(value)) if len(t) > 1}
    return found


def _by_id(items: Iterable[Mapping[str, Any]]) -> Dict[str, Mapping[str, Any]]:
    return {str(item.get("id")): item for item in items if item.get("id") is not None}


def _check(
    kind: str,
    declared: Sequence[Mapping[str, Any]],
    built: Mapping[str, Mapping[str, Any]],
) -> List[Loss]:
    losses: List[Loss] = []
    for item in declared:
        identifier = str(item.get("id"))
        target = built.get(identifier)
        if target is None:
            losses.append(Loss(kind, identifier, "id", "it is not in the diagram at all"))
            continue
        survived = _tokens(target)
        for field, value in item.items():
            if field == "id":
                continue
            missing = sorted(_tokens(value) - survived)
            if missing:
                losses.append(Loss(
                    kind, identifier, field,
                    f"`{field}` was dropped — "
                    + ", ".join(repr(token) for token in missing[:6])
                    + (f" and {len(missing) - 6} more" if len(missing) > 6 else "")
                    + " appear nowhere in the diagram",
                ))
    return losses


def check(draft: Mapping[str, Any], diagram: Mapping[str, Any]) -> List[Loss]:
    """Everything the draft declared that the diagram does not carry.

    An empty list is the only acceptable result for a diagram the product built. A loss
    here is **our** defect, never the host's: their draft was accepted.
    """
    if not isinstance(draft, Mapping) or not isinstance(diagram, Mapping):
        return []

    losses = _check("element", draft.get("elements") or (), _by_id(diagram.get("nodes") or ()))
    losses += _check(
        "relationship", draft.get("relationships") or (), _by_id(diagram.get("edges") or ())
    )

    # Evidence lives in `metadata`, not on the elements that cite it, so it is checked
    # against the whole document rather than against one node.
    metadata_tokens = _tokens(diagram.get("metadata") or {})
    for record in draft.get("evidence") or ():
        missing = sorted(_tokens(record) - metadata_tokens)
        if missing:
            losses.append(Loss(
                "evidence", str(record.get("id")), "record",
                "the citation was dropped — "
                + ", ".join(repr(token) for token in missing[:6])
                + " appear nowhere in the diagram's metadata",
            ))

    # The ask is now carried rather than discarded, which puts it inside this check for
    # the first time. It is the one field with no other copy anywhere: an element the
    # diagram drops is at least visible by its absence, while a dropped request leaves
    # nothing behind to notice.
    for index, text in enumerate(draft.get("requests") or ()):
        missing = sorted(_tokens(text) - metadata_tokens)
        if missing:
            losses.append(Loss(
                "request", str(index), "text",
                "the ask was dropped — "
                + ", ".join(repr(token) for token in missing[:6])
                + " appear nowhere in the diagram's metadata",
            ))

    # Only the assumptions something actually rests on. An unreferenced one is already a
    # refusal (`orphan_assumption`), so it can never reach here.
    referenced = {
        item["assumptionRef"]
        for section in ("elements", "relationships")
        for item in draft.get(section) or ()
        if item.get("assumptionRef")
    }
    for assumption in draft.get("assumptions") or ():
        if assumption.get("id") not in referenced:
            continue
        missing = sorted(_tokens(assumption) - metadata_tokens)
        if missing:
            losses.append(Loss(
                "assumption", str(assumption.get("id")), "body",
                "an element is marked `assumed` and the assumption behind it was dropped — "
                + ", ".join(repr(token) for token in missing[:6]),
            ))

    return losses


def describe(losses: Sequence[Loss]) -> str:
    """One sentence naming what was lost, or empty when nothing was."""
    if not losses:
        return ""
    lines = "; ".join(str(loss) for loss in losses[:5])
    more = len(losses) - 5
    return (
        f"Materialization dropped {len(losses)} thing(s) the draft declared: {lines}"
        + (f"; and {more} more" if more > 0 else "")
        + ". This is a GraphPilot defect, not a problem with the draft."
    )
