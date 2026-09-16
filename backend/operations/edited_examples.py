"""Replay an edit, so the gallery can show what one costs a person's arrangement.

Every other pool shows a diagram. This one shows a **pair** — the same diagram before and
after a host edited it — because the thing worth reviewing is not either picture on its
own, it is what changed between them and what did not.

An example is one authored file:

```
assets/blueprints/<type>/examples/edited/<name>/
  scenario.json     authored: the create, the arrangement, the edit
  before.gp.json    generated: after a person arranged it
  output.gp.json    generated: after the host's edit
```

Both diagrams are **generated**, never stored by hand, so the pair is evidence about the
code as it is today rather than a screenshot of the day it was made. A diagram that only
survives because somebody saved it proves nothing about the merge still working.

## `edit` is fixture notation, not a product concept

**The product has no patch format.** A host calls `diagram_read`, edits the draft file it
is given, and sends the *whole document* back. Whole desired state: an element the file
does not mention is deleted. Nothing ever says "remove X".

So a scenario's `edit` block — `remove`, `relabel`, `change`, `addElements` — exists only
here, as a compact way of saying what the host changed. `replay` applies it to a fresh
projection and submits the result, which is a real whole draft.

That is a trade, and it has a cost worth stating: this exercises `_apply_edit`, which is
ours, rather than a host's own authoring. Storing the submitted draft verbatim instead
would be closer to reality and would go stale the first time the projection changed shape,
leaving the example testing a document `diagram_read` would never produce. Applying
operations to a current projection keeps it honest about shape at the price of being one
step removed from a real host.

The mitigation is that **both drafts are written out** — `read.draft.json` and
`submitted.draft.json` — so a reviewer reads the actual documents rather than the shorthand
that produced them.
"""

import json
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

from services.drafts.diagram_edit_service import DiagramEditService
from services.materialization.diagram_creation_service import DiagramCreationService
from services.materialization.diagram_update_service import DiagramUpdateService
from services.shared.workspace_storage_service import WorkspaceStorageService

#: `data` keys an arrangement may set on a node, beside geometry. These are the class-2
#: semantics a person types in the editor and no draft can express — the ones an edit is
#: most at risk of losing, so an example that does not exercise them proves less.
_ARRANGE_DATA = ("description", "metadata")


@dataclass(frozen=True)
class EditedPair:
    #: The four documents of one round trip, in the order they exist.
    before: Dict[str, Any]
    #: The draft `diagram_read` handed the host — the projection of `before`, before the
    #: host touched anything.
    projected: Dict[str, Any]
    #: The draft the host sent to `diagram_update`. **This is the real artifact**: whole
    #: desired state, with the edit already in it. The scenario's `edit` operations are
    #: fixture notation that produces this; the product has no such concept, and a
    #: reviewer checking whether a host authored something correctly needs to read this
    #: rather than the operations that stood in for one.
    submitted: Dict[str, Any]
    after: Dict[str, Any]
    #: What the write reported removing, so the card can show it rather than the reviewer
    #: having to diff two pictures to notice something went.
    removed: Tuple[Dict[str, Any], ...]
    added: Tuple[str, ...]
    #: Ids whose position is identical across the pair. The number a reviewer checks.
    held: Tuple[str, ...]
    moved: Tuple[str, ...]


def _apply_arrangement(diagram: Dict[str, Any], arrange: Mapping[str, Any]) -> None:
    """Stand in for a person in the browser.

    Four things a person does that no draft can express, and that an edit therefore has to
    preserve without ever being shown them: drag and resize a node, type a description,
    bend an edge, and draw something new.
    """
    nodes = arrange.get("nodes") or {}
    for node in diagram.get("nodes") or ():
        change = nodes.get(node["id"])
        if not change:
            continue
        if "position" in change:
            node["position"] = {"x": float(change["position"]["x"]),
                                "y": float(change["position"]["y"])}
        for size in ("width", "height"):
            if size in change:
                node[size] = float(change[size])
        for key in _ARRANGE_DATA:
            if key in change:
                node.setdefault("data", {})[key] = change[key]

    edges = arrange.get("edges") or {}
    for edge in diagram.get("edges") or ():
        change = edges.get(edge["id"])
        if change and "route" in change:
            edge["route"] = json.loads(json.dumps(change["route"]))

    # Something a person drew on the canvas. `user` is the only honest provenance: the
    # editor stamps it, a host may never author it, and it comes back through the
    # projection so a write carries it forward untouched.
    for drawn in arrange.get("drawn") or ():
        element = json.loads(json.dumps(drawn))
        element.setdefault("type", "gpNode")
        element.setdefault("origin", {
            "assurance": "user", "evidenceRefs": [], "assumptionRefs": [],
            "schemaRules": [], "rationale": "Added in the editor.",
        })
        if "source" in element and "target" in element:
            diagram.setdefault("edges", []).append(element)
        else:
            diagram.setdefault("nodes", []).append(element)

    # A person has saved from the editor, so the diagram is theirs now.
    diagram.setdefault("metadata", {})["authoring"] = "custom"


def _apply_edit(draft: Dict[str, Any], edit: Mapping[str, Any]) -> None:
    """What the host changes in the file `diagram_read` handed it."""
    removed = set(edit.get("remove") or ())
    if removed:
        draft["elements"] = [e for e in draft["elements"] if e["id"] not in removed]
        draft["relationships"] = [
            r for r in draft["relationships"]
            if r["id"] not in removed
            and r["source"] not in removed and r["target"] not in removed
        ]
    for element_id, label in (edit.get("relabel") or {}).items():
        for element in draft["elements"]:
            if element["id"] == element_id:
                element["label"] = label
    # Any class-1 field on an existing element or relationship: a role, a multiplicity, a
    # rewired endpoint, a stereotype. Everything a host can legitimately change about
    # something that already exists, without the scenario format growing a verb per field.
    for item_id, fields in (edit.get("change") or {}).items():
        for item in draft["elements"] + draft["relationships"]:
            if item["id"] == item_id:
                item.update(json.loads(json.dumps(fields)))
    draft["elements"].extend(json.loads(json.dumps(edit.get("addElements") or [])))
    draft["relationships"].extend(json.loads(json.dumps(edit.get("addRelationships") or [])))

    # Removing an element usually orphans the citation only it referenced, and an uncited
    # record makes `metadata.evidence` — "the regions this diagram was built from" — false.
    # A host doing this by hand has to notice; here it is part of the edit.
    cited = set()
    for item in draft["elements"] + draft["relationships"]:
        cited.update(item.get("evidenceRefs") or ())
    if draft.get("evidence"):
        draft["evidence"] = [e for e in draft["evidence"] if e["id"] in cited]

    draft["requests"].append(edit["request"])


def replay(scenario: Mapping[str, Any]) -> EditedPair:
    """Create, arrange, read, edit, update — through the real services, in a temp workspace.

    Nothing is faked. The same `DiagramCreationService`, `DiagramEditService` and
    `DiagramUpdateService` a host reaches through MCP, so a regression in any of them
    shows up as a changed picture on the page.
    """
    work = tempfile.mkdtemp(prefix="gp-edited-")
    try:
        create = json.loads(json.dumps(scenario["create"]))
        name = create["diagramName"]
        DiagramCreationService().create(work, create)

        storage = WorkspaceStorageService(work)
        path = storage.diagram_file_path(name)

        arranged = json.loads(path.read_text(encoding="utf-8"))
        _apply_arrangement(arranged, scenario.get("arrange") or {})
        path.write_text(json.dumps(arranged, indent=2), encoding="utf-8")
        before = json.loads(path.read_text(encoding="utf-8"))

        result = DiagramEditService().read(work, name)
        draft = json.loads(result.draft_path.read_text(encoding="utf-8"))
        projected = json.loads(json.dumps(draft))
        _apply_edit(draft, scenario["edit"])
        submitted = json.loads(json.dumps(draft))
        outcome = DiagramUpdateService().update(work, draft)

        after = json.loads(path.read_text(encoding="utf-8"))

        was = {node["id"]: node["position"] for node in before["nodes"]}
        now = {node["id"]: node["position"] for node in after["nodes"]}
        survivors = sorted(set(was) & set(now))
        return EditedPair(
            before=before,
            after=after,
            projected=projected,
            submitted=submitted,
            removed=tuple(item.as_dict() for item in outcome.removed),
            added=tuple(outcome.added_ids),
            held=tuple(i for i in survivors if was[i] == now[i]),
            moved=tuple(i for i in survivors if was[i] != now[i]),
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def load_scenario(example_dir: Path) -> Optional[Dict[str, Any]]:
    path = example_dir / "scenario.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
