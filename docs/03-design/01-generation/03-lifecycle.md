# Lifecycle, Assurance, and Freshness

## `diagram_create`

One call takes a [draft](01-draft.md) to a diagram on disk.

```text
1  validate draft        schema · IDs · endpoints · evidence refs ·
                         assurance pairing · notation legality
2  read evidence         resolve each locator, hash the cited region
3  materialize           draft → logical → canonical
4  layout                PyGraphviz
5  validate canonical    DiagramValidationService
6  persist               atomic write of <diagramName>.gp.json
7  render                sibling <diagramName>.svg
8  return                paths, counts, warnings, editor URL
```

Steps 1–2 are the only places a *user* mistake is reported. Steps 3–5 failing means
GraphPilot has a defect, and it says so rather than saving something malformed.

### Refusing to overwrite

`diagram_create` fails if `.graphpilot/diagrams/<diagramName>.gp.json` already exists.

A diagram may have been edited in the browser since it was created, and a create call
carries no knowledge of those edits — so silently replacing it would destroy user work.
Starting over is an explicit delete, and changing an existing diagram is
[an update](../05-edit/README.md).

### Result

```json
{
  "outcome": "created",
  "diagramPath": ".graphpilot/diagrams/todo-structure.gp.json",
  "svgPath": ".graphpilot/diagrams/todo-structure.svg",
  "editUrl": "http://localhost:5173/editor?diagramPath=...",
  "nodeCount": 14,
  "edgeCount": 19,
  "assurance": { "authority": "as_implemented", "assumedElementIds": [] },
  "operationWarnings": []
}
```

A diagram whose canonical JSON persisted but whose SVG failed is still **created**: the
result carries `svgPath: null` and a `render_failed` warning. The host re-renders from the
saved file; it never re-creates for an image.

## Assurance

Every element and relationship carries one of three classes.

| Class | Means | Requires | Canvas and export show |
| --- | --- | --- | --- |
| `grounded` | Backed by cited source | ≥1 `evidenceRefs` | normal |
| `assumed` | Accepted judgement, not established | an `assumptionRef` | amber `?` badge |
| `conceptual` | Not a claim about any repository | `authority: conceptual` | normal |

A fourth class, `user`, appears only on elements a person drew in the editor. It cannot be
authored in a draft, and carries a blue `✎` badge.

A badge is an admission, and an admission is only information beside something it is not —
which is why `grounded` carries none. So a diagram whose every element is `user` carries
none either: a diagram drawn entirely by hand marking every element "drawn by hand" is the
noise that teaches a reader to ignore badges. The canvas and the SVG export apply that rule
identically, and both place the badge on the visible shape rather than the layout box.

Draft validation enforces the pairing: `grounded` without evidence and `assumed` without
an assumption are both save errors. **An assumption may never be presented as repository
fact**, and this is the mechanism that guarantees it.

The diagram records the summary:

```json
{
  "metadata": {
    "authority": "as_implemented",
    "requests": [
      { "at": "2026-08-05T09:10:44Z", "text": "Show how the todo service is put together." }
    ],
    "assurance": { "assumedElementIds": ["sql-repository"] },
    "evidence": [
      {
        "id": "ev-todo-service",
        "kind": "code",
        "locator": { "path": "src/todo_api/services/todo_service.py", "lineRange": { "start": 25, "end": 100 } },
        "contentDigest": "sha256:…",
        "summary": "TodoService checks permissions and domain rules, then persists."
      }
    ]
  }
}
```

## Evidence lives in the diagram

`metadata.evidence` carries the full evidence records, not references to a side file.
`metadata.requests` sits beside it for the same reason: every ask the diagram has answered,
oldest first, stamped by the backend from the same clock read as `createdAt`. It is the
only durable record of *why* the diagram looks the way it does, for a reader who never saw
the conversation.

The diagram is therefore **self-contained**: it can be read, validated, re-rendered,
checked for freshness, and projected back into draft shape with nothing but itself. There
is no manifest to bind, no digest to reconcile, and no second document that can go stale.

This is also what makes the draft disposable. Everything durable is in the diagram.

## Freshness is per cited region

```text
create        hash each cited region → metadata.evidence[].contentDigest
later         re-hash the same regions
                all match       → current
                any differs     → stale, naming the exact evidence IDs and files
unrelated file edited           → no effect
```

The retired model fingerprinted the whole repository, so any edit anywhere staled the
evidence and forced a complete regather. Binding freshness to the exact cited lines means a
diagram of the service layer is unaffected by a change to an unrelated module.

A `conceptual` diagram cites nothing and has no freshness contract.

## What is durable

```text
.graphpilot/
└── diagrams/
    ├── todo-structure.gp.json    canonical diagram, carrying its own evidence
    └── todo-structure.svg        rendered sibling
```

That is the whole managed layout for generation. No evidence manifest, no request file, no
draft file, no diagnostics run directory.

| Question | Authoritative artifact |
| --- | --- |
| What the repository says | The source files |
| What diagram exists, and what supports each element | `<diagramName>.gp.json` |
| What a reader looks at | The sibling `.svg`, or the editor |

## Errors

Draft problems are reported per path so a host can fix them in one pass rather than
discovering them one round at a time.

The refusal's `code` names the **cause**, chosen by precedence so a host fixes the right
thing first: identity → vocabulary → notation → the claims made about it. A block mistyped
as an `opaqueAction` also breaks every relationship touching it, so it reports
`semantic_type_unsupported`, not `notation_invalid`.

| Code | Cause |
| --- | --- |
| `draft_too_large` | The draft exceeds the local size bound |
| `possible_secret` | A prose field reads like a credential, and prose is copied into the saved diagram |
| `duplicate_id` | An ID is reused, or an element and a relationship collide in one ID space |
| `unresolved_reference` | An endpoint, `parentId`, `evidenceRefs`, or `assumptionRef` names nothing in the draft |
| `cyclic_parent` | Containment loops back on itself |
| `semantic_type_unsupported` | The type is not in this diagram type's vocabulary; the permitted set is named |
| `containment_unsupported` | The named `parentId` is not a container element |
| `stereotype_unsupported` | A stereotype outside BDD, which has no primary heading to select |
| `notation_invalid` | A relationship end the notation forbids, a guard on a non-flow, a `commentLink` without a note, a non-block BDD endpoint, or an irreflexive relationship pointing at itself |
| `guard_required` | A decision with more than one branch left a branch unlabelled |
| `assurance_unsupported` | `grounded` without evidence, `assumed` without an assumption, or a class that contradicts `authority` |
| `evidence_required` | `as_implemented` cites nothing |
| `evidence_unexpected` | `conceptual` cites something |
| `orphan_evidence` | An evidence record no element or relationship cites |
| `orphan_assumption` | An assumption no element or relationship names |
| `evidence_unreadable` | A locator is missing, unsafe, empty, inverted, or runs past EOF |
| `evidence_stale` | A cited region changed since the digest was taken |
| `diagram_exists` | The target diagram is already present |
| `schema_*` | A structural violation, named after the JSON Schema keyword |

Every one is deterministic, free, and returned before anything is written. Findings come
back **complete and sorted by path** — a host that rediscovers its mistakes one call at a
time pays for each one.
