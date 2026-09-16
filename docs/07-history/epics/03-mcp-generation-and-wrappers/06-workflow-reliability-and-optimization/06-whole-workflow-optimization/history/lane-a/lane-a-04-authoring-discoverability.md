# Lane A Slice 04: Authoring Discoverability

## Purpose

Cut the authoring rounds a cold host needs by making the evidence and request contracts learnable before submission and fully legible on failure, rather than discoverable only by exhausting the validator.

## Background

`r1` proved the workflow is completable but expensive: JSON 1 took seven attempts and JSON 2 took four, against a criterion of at most two each. The host's own account names the causes, and all four are GraphPilot-owned.

1. **No contract is retrievable.** No tool returns the evidence or request shape the way `diagram_get_schema` does for diagram types, so both documents were reverse-engineered from validator output. Enum and `const` values are learnable only by failing.
2. **Failures reveal one nesting layer per round.** Validation only reaches a level once the level above is satisfied, so each submission exposes the next layer: claim, then versions, then payload, then claim references.
3. **Truncation hides siblings.** `146 additional issues were omitted` concealed defects the host would otherwise have fixed in the same round.
4. **Rejection never names the alternative.** An unexpected property is reported without the allowed set, so three spellings of the locator line range were rejected in turn and the host abandoned line precision — degrading evidence from exact regions to whole files.

Item 4 is the clearest defect: it costs rounds *and* silently lowers evidence quality.

This slice therefore replaces the original contract-freeze scope, which was written before any of this was measured. Snapshot and host-interface contract work remains with A05 and A06.

## Design

A03 changed the reporting layer only; the schemas are exactly as they were. This slice builds on that state.

### Name the alternative on rejection

When a property is rejected as unexpected, report the allowed property names alongside it.

`jsonschema` attaches the failing subschema to the error, so the allowed set is the key set of that subschema's `properties`, sorted for determinism. When the subschema declares no properties, the message says so explicitly rather than printing an empty list. This is a deterministic reporting change with no contract effect, and it removes the guess-and-fail loop that cost line precision.

### Stop hiding sibling defects

The 255-issue cap exists to bound payload, not to withhold information. The bound is never exceeded; what changes is which issues survive it:

1. sort as today by `(path, code, message)`;
2. take the first issue of each distinct path in that order, giving one representative per path;
3. if that breadth pass alone exceeds the cap, truncate it at the cap, so the bound always holds even with more distinct paths than capacity;
4. otherwise fill the remaining capacity with the next issues in sorted order;
5. append the omitted-count marker whenever anything was dropped.

Breadth survives and only repetition is trimmed, deterministically.

### Deferred: recomposing `evidence[]`

A03's Outcome proposed recomposing the `evidence[]` `oneOf` into the conditional `if`/`then` form used by claim payloads, to make it self-describing. **That is deliberately not done here, because the evidence no longer supports it.**

The recomposition was proposed when every evidence failure returned one opaque `schema_oneOf`. A03's best-branch reporting removed that: `r1` contains no `schema_oneOf` anywhere, and evidence entries now fail with precise per-property codes. The diagnosability problem the recomposition existed to solve is already solved at the reporting layer, for every `oneOf` in the system rather than this one site.

Doing it anyway would mean non-trivial schema surgery for little gain. Conditional composition cannot keep `additionalProperties: false`, since the base cannot know branch-specific properties; it requires `unevaluatedProperties: false`, and proving the accepted document set unchanged across that switch is real work. That cost is not justified by a problem that no longer appears in the evidence.

Revisit only if a later observation shows `evidence[]` specifically causing rounds again.

### Retrieve the contract before submitting

Provide the selected mode and type authoring contract through the approved `diagram_generation_get_authoring_contract` lookup, returning ordered steps, the host-authored shape, one complete valid example, and the conditional type checklist. Prose in `content`, machine-actionable data in `structuredContent`.

The approved design deliberately keeps `diagram_get_schema` scoped to canonical diagram schemas, and this slice does not change that.

Implementation of the lookup tool itself belongs to A06; this slice freezes its contract, identity, and example assets.

The runtime discovery pointer — save-tool rejections and the workflow route naming where the contract can be fetched — **moves to A06 with the tool.** The audited plan placed it here, which is not achievable in this order: the tool is not registered until A06, so a rejection naming it would send a host to a tool that does not exist. Pointing at an unregistered tool is worse than silence. The requirement itself is unchanged and is frozen below as part of the contract; only its implementation moves to the slice that makes it true.

## Included Work

- Report allowed property names on unexpected-property rejections.
- Bound issue lists without hiding distinct paths, retaining the omitted count.
- Freeze the authoring-contract identity, bounded shape, leakage-disjoint example rule, and discovery requirement in the canonical MCP owner.
- Add focused tests for each behavior, including a regression proving the locator range spelling is now discoverable from a single rejection.
- Record the scope change and its evidence in the decision index.

## Not In Scope

- Recomposing `evidence[]` into conditional composition, deferred with rationale above.
- The snapshot redesign, claim-version removal, and backend-issued version references, which remain with A05.
- Implementing the authoring-contract tool and the router, which remain with A06.
- Emitting the runtime discovery pointer, moved to A06 for the ordering reason given above.
- Extending `diagram_get_schema` to context documents.
- Excluding lockfiles from eligible source. It is evidenced and cheap, but it changes the source fingerprint and therefore stales existing canonical JSON 1, so it is a behavior change that belongs with the snapshot work in A05 where staleness is already being handled.
- Any host, provider, frontend, or Lane B behavior.

## Target Areas

- `backend/services/context/context_document_validator.py`
- `backend/mcp_server/server.py` issue-detail bounding
- `backend/tests/core/` and `backend/tests/mcp_server/` focused tests
- `docs/01-architecture/03-mcp-tools/` for the authoring-contract identity and discovery pointer
- `docs/02-design-and-features/decision-decisions.md`
- This Outcome

## Exit Criteria

- An unexpected-property rejection names the allowed properties, proven by a test in which one rejection is sufficient to discover the locator line-range spelling.
- Issue lists never exceed the bound, retain one issue per distinct path until capacity is reached, stay deterministic, and still report the omitted count.
- The authoring-contract identity, bounded shape, argument set, leakage-disjoint example rule, size budget, and discovery requirement are frozen in one canonical owner.
- That owner states that rejections must name where the contract is fetched, so A06 implements a written requirement rather than inventing one.
- No schema changes, so the accepted document set is unchanged by construction.
- Focused tests and the full backend suite pass, and an independent implementation audit confirms the scope held.

Whether these changes actually reduce authoring rounds is measured by a later reference observation, which this slice cannot run; that comparison is A08's exit criterion, not this one's.

## Previous Slice

[`lane-a-03-evidence-authoring-unblock.md`](lane-a-03-evidence-authoring-unblock.md)

## Next Slice

[`lane-a-05-snapshot-backend.md`](lane-a-05-snapshot-backend.md) and [`lane-a-06-host-interface.md`](lane-a-06-host-interface.md)

## Outcome

**Status:** Complete against its audited plan, with one item transferred to A06 for an ordering reason recorded below. Lane A pauses here.

**Completion:** Two of the four causes `r1` named are fixed in behavior, and the deepest one is now frozen as a contract for A06 to implement.

Unexpected-property rejections name the allowed properties, taken from the failing subschema and sorted for determinism, with an explicit message when a subschema allows none. This closes the loop that cost line precision: the host had three spellings of the locator range rejected in turn and abandoned exact regions for whole files, which was a silent evidence-quality loss rather than only wasted rounds.

Issue lists no longer hide whole regions of a document. Each distinct path receives a representative before remaining capacity is spent on repetition, within the unchanged 256 bound, still reporting the exact dropped count.

The selected authoring contract is frozen in the MCP public-surface owner: arguments, returned elements, the two mode-specific identities, the leakage-disjoint example rule, the size budget, side-effect freedom, and the requirement that save-tool rejections name where the contract can be fetched. Adding a not-yet-implemented tool to that table follows how the package already treats `diagram_update`; runtime status stays in the current-state board.

**Deviations:**

*The runtime discovery pointer moved to A06.* The audited plan placed it here, which the implementation proved impossible in this order: the lookup is not registered until A06, so a rejection naming it would send a host to a tool that does not exist — worse than silence. The requirement is not weakened or lost. It is frozen in the MCP owner as binding contract and added explicitly to A06's Included Work, so A06 implements a written requirement instead of rediscovering one.

*The `evidence[]` recomposition stays dropped.* A03's Outcome proposed it; the A04 plan audit challenged the claim that conversion preserves the accepted document set. Rather than specify and prove that conversion, it was dropped, because A03's best-branch reporting already removed the opacity it existed to fix and `r1` contains no `schema_oneOf` at all.

**Implementation audit:** An independent read-only audit over the combined committed and working-tree diff returned **pass with findings and no critical finding**.

Accepted and fixed: missing edge-case coverage for the truncation bound, now tested at empty input, exactly 256, exactly 257, and 300 distinct paths exceeding capacity; the risk that the transferred pointer could be lost, now bound into A06's Included Work; and a brittle assertion on `jsonschema`'s own wording, now asserting only the augmentation this slice owns.

Rejected with reasons: a request to annotate the frozen contract as "not yet implemented" was declined, because `.devin/rules/graphpilot.md` requires design owners to describe the intended system in present tense and keep implementation status in the current-state board and slice Outcomes. A defensive `None` check on the failing subschema was declined as a non-defect, since `isinstance(None, Mapping)` is already false and the empty-schema path is covered.

The audit confirmed the bound is never exceeded, the dropped count is arithmetically correct, only `message` changes while `code` and `path` are untouched, no consumer depends on message text, no schema file changed, and no Lane B, provider, live-anchor, or `.env` path was touched.

**Verification:** Focused context-validator, context-persistence, and MCP context-tool tests pass at 90 tests. Full backend suite passes. `git diff --check` is clean. Zero provider calls; no `.env` or secret file was read or modified.

**Follow-up:** Lane A pauses here for the planned Block 6 documentation reorganization. A05 and A06 have not started and no Outcome was written for either. The next measurement is A08's reference observation, which is the only thing that can show whether these changes actually reduce authoring rounds below `r1`'s seven and four.
