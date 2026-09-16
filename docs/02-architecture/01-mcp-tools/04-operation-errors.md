# MCP Operation Results and Errors

This document owns GraphPilot's final intended MCP mapping for handled operational problems, successful domain gates,
post/optional-operation warnings, exact public operation codes, retryability, bounded `details`, and host recovery.
Shared backend value semantics are defined in
[`01-backend-architecture.md`](../03-backend.md#121-shared-operational-problem); this file owns their MCP
transport and public code registry.

Runtime delivery status belongs only to the delivery board. Codes are additive and
stable once public.

**The code tables below are checked against the registry by
`tests/shared/test_error_code_registry.py` and `tests/docs/test_operation_errors_doc.py`.**
They were hand-maintained once and had drifted to 50 codes that do not exist and 22
that were missing, including two added the same week.

## `OperationProblem`

Every handled operational problem has exactly:

```json
{
  "code": "request_conflict",
  "message": "The canonical request changed after it was loaded.",
  "retryable": true,
  "details": {
    "expectedDigest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "currentDigest": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  }
}
```

| Field | Required | Contract |
| --- | --- | --- |
| `code` | Yes | Stable lowercase-snake-case identifier, `1..128`. Hosts branch on this value. |
| `message` | Yes | Safe nonblank user-facing explanation, `1..2,000`. Hosts do not branch on message text. |
| `retryable` | Yes | Whether a later call may succeed after the reported condition changes. It never authorizes an identical automatic retry. |
| `details` | No | Bounded code-specific object. Omitted, not null, when the code defines no details. Unknown detail fields are rejected. |

A problem never contains credentials, `.env` values, raw source, or a native stack trace
with library paths. The rule matters most where it is easiest to break: a citation failure
knows the file it could not read and the lines it wanted, and says so — it does not quote
what it found there.

*(This list once also excluded provider responses, prompts and evaluator gold. `P0` removed
the provider pipeline, so there is nothing of that kind left to leak.)*

## MCP outer mapping

### Actual operation failure

A failed requested operation returns:

```json
{
  "content": [
    {
      "type": "text",
      "text": "The canonical request changed after it was loaded."
    }
  ],
  "structuredContent": {
    "error": {
      "code": "request_conflict",
      "message": "The canonical request changed after it was loaded.",
      "retryable": true,
      "details": {
        "expectedDigest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "currentDigest": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
      }
    }
  },
  "isError": true
}
```

Rules:

- `structuredContent` has top-level `error`; it is not wrapped in `data`.
- `content` is a short safe summary and does not expand raw details.
- Enabled diagnostics that were safely written before an error may appear as nullable sibling `diagnostics`; they
  never move inside `error.details`.
- Unexpected exceptions are logged internally after sanitization and map to `internal_error` with no details.

### Successful domain result

An unfavourable answer is still a successful call. `isError: false` on:

- `diagram_validate` returning `valid: false`;
- `diagram_check_draft` returning findings, which is the call doing its job; and
- `diagram_create` returning warnings, because the diagram was written.

Validation issues and structural findings are domain values, not `OperationProblem`s. A
host branches on them; it does not treat them as transport failures.

### Successful optional/post-operation warning

`diagram_create` returns `operationWarnings` alongside `outcome: created` and
`isError: false`. Every one is advice about a diagram that **was saved**:

| Code | Why it is a warning rather than a refusal |
| --- | --- |
| `long_label` | The label is past the guide length. It saves and usually does not fit |
| `label_truncated` | The renderer could not fit it even at the smallest font |
| `structural_constraint` | The diagram is legal and a reader will notice the oddity |
| `hard_to_read` | Measured from the drawn SVG, so no check could have reached it first |
| `content_lost` | **A GraphPilot defect.** The draft was accepted and something in it did not survive materialization. Nothing the author can write differently will fix it |
| `evidence_stale` | On `diagram_update`: a region cited by the saved diagram has changed since. Refusing would put the edit at the mercy of files it never looked at |
| `render_failed` | The diagram was saved; only its picture failed. `svgPath` comes back `null` |
| `layout_overlap` | On `diagram_update`: **R2** grew a box to fit its content and **R5** forbids moving anything to make room, so two elements now overlap. Carries the colliding `pairs`. Nothing is moved on the author's behalf — the arrangement is a person's work |

The last three are assembled by hand rather than by validation, so they are registered in
`_WARNING_CODES` and this table is compared against that registry in both directions. The
first three reach `operationWarnings` as `ValidationCode` members.

A warning never means the call failed. Refusing here would throw away a diagram that is
already better than no diagram.

## Retryability policy

`retryable: true` means the reported condition can be changed before a later attempt — correct an argument or a path, free a name, repair a local write or render environment. **It never means "call the same tool again unchanged."**

A refusal is the clearest case. `diagram_create` writes nothing when it refuses and does not consume the diagram name, so calling again with the *same* draft gets the *same* answer — and calling again with the finding fixed costs nothing.

## Refusals — the draft broke a rule

Every one is explained in the authoring contract before a host can trip it, which is what `REFUSAL_GUIDE` is for, and these rows are generated from it.

| Code | Retryable | What it means |
| --- | ---: | --- |
| `assurance_unsupported` | `false` | `grounded` needs `evidenceRefs`; `assumed` needs an `assumptionRef`; `conceptual` is only legal in a conceptual diagram, where every element must use it. |
| `containment_unsupported` | `false` | That `parentId` names an element that cannot contain anything. The contract names the containers. |
| `cyclic_parent` | `false` | Containment loops back on itself. |
| `draft_invalid` | `false` | The document does not match the draft schema at all — a missing field, a wrong type, a value outside an enum. It is **not** a count: a well-formed draft that breaks one of the rules above comes back under that rule's own code, however many findings there are. `draft_invalid` means the shape is wrong, so nothing further could be checked. |
| `draft_too_large` | `false` | — |
| `duplicate_id` | `false` | Two items share an `id`. Ids are unique across the whole draft, not just within their own list. |
| `evidence_required` | `false` | `authority: as_implemented` claims the diagram reflects the source, so it must cite some. |
| `evidence_stale` | `false` | A region cited by a *saved* diagram has changed since. Re-read it and author the evidence again. |
| `evidence_symbol_not_in_range` | `false` | The `symbol` is not in the lines the citation points at, so the citation names one thing and points at another. |
| `evidence_unexpected` | `false` | `authority: conceptual` claims nothing about the repository, so `evidence` must be empty. |
| `evidence_unreadable` | `false` | A cited file cannot be read, is empty, or the line range runs past its end or backwards. Paths are relative to `workspaceDir`. |
| `guard_required` | `false` | Every branch out of a decision node needs a `guard`, or the diagram cannot say which way it goes. |
| `notation_invalid` | `false` | The notation forbids it — an end on a relationship that has none, a self-referential composition, a guard on something that is not a control flow, a `commentLink` with no note, or compartments on an element that is not a block. |
| `orphan_assumption` | `false` | Every `assumptions` entry must be named by some element or relationship through `assumptionRef`. |
| `orphan_evidence` | `false` | Every `evidence` entry must be cited by some element or relationship. The saved diagram lists only the regions it was actually built from. |
| `possible_secret` | `false` | — |
| `basis_stale` | `false` | The diagram changed after `diagram_read`, or the draft carries no `basis` at all. An update submits the whole diagram, so one written from a stale read deletes everything it does not mention. Read it again and re-apply. |
| `diagram_crossed` | `false` | The diagram holds elements from more than one diagram type, so its type is `custom` and no draft can describe it. It can still be edited in the browser. |
| `requests_invalid` | `false` | `requests` carries more or fewer than one entry. A new diagram is asked for once; send only the ask that produced it. Adding to the list is what editing an existing diagram does. |
| `semantic_type_unsupported` | `false` | The element or relationship type is not in this diagram type's vocabulary. The contract lists what is. |
| `unresolved_reference` | `false` | A `source`, `target`, `parentId` or `evidenceRefs` names something that is not in this draft. |

## Transport, path, and operation codes

Raised by the surface rather than by a rule in the draft.

| Code | Retryable |
| --- | ---: |
| `diagram_exists` | `false` |
| `diagram_not_found` | `true` |
| `internal_error` | `false` |
| `invalid_arguments` | `true` |
| `invalid_diagram` | `true` |
| `invalid_diagram_json` | `true` |
| `invalid_json` | `true` |
| `invalid_path` | `true` |
| `invalid_workspace` | `true` |
| `layout_engine_unavailable` | `false` |
| `layout_failed` | `false` |
| `list_failed` | `true` |
| `load_failed` | `true` |
| `missing_path` | `true` |
| `not_found` | `true` |
| `render_failed` | `true` |
| `save_failed` | `true` |
| `source_changed` | `true` |
| `unsafe_path` | `true` |
| `unsupported_diagram_type` | `false` |
| `validation_failed` | `true` |
| `validation_unavailable` | `true` |
| `workspace_resolution_error` | `true` |

## Host recovery invariants

- Branch on `code`, never on `message`. Messages are written for people and change; codes are stable once public.
- `retryable: false` means the same call will fail the same way. Change the input or report it.
- A refusal leaves the workspace untouched. Nothing is written, and the diagram name is still free.
- A **warning** is not an error: the diagram saved. `hard_to_read` and `content_lost` arrive on a successful `diagram_create`, and the second is a GraphPilot defect rather than something the draft can fix.
- A saved diagram is never overwritten, and nothing on this surface removes one. `diagram_exists` is the refusal; the answer is another name. Removing a diagram is the user's decision, in their own repository.
