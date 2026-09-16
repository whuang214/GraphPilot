# A05 · Authoring Contract Lookup

**State: planned.** Provider-free; no G3 authorization needed.

Lane state: [`../plan.md`](../plan.md). Frozen contract:
[`03-mcp-tools/README.md`](../../../../../../../02-architecture/01-mcp-tools/README.md).

## Plan

### Why this candidate

The integrated baseline's Lane A-owned finding, `host_boundary_evidence_simulated`,
is not actionable here: replacing simulated W01–W03 needs separately bound external
host evidence, not a GraphPilot change, and this lane's host is the implementing
agent. So the candidate comes from host observation `r1`.

`r1` completed the workflow but needed **7 JSON 1 attempts and 4 JSON 2 attempts**
against a two-attempt criterion. It named four causes. A03 and A04 fixed two —
opaque `oneOf` rejections, then unnamed allowed properties and truncation hiding
sibling defects. The two that remain are one problem:

- no tool returns the evidence or request contract, so both documents are
  reverse-engineered from validator output;
- enum and `const` values are learnable only by failing.

This package closes that gap. It is the largest remaining Lane A cause, and it is
provider-free.

### What it delivers

**The lookup.** `diagram_generation_get_authoring_contract(generationMode,
diagramType)` implemented exactly as A04 froze it in the MCP owner: two required
arguments, no workspace or provider input, no filesystem or provider side effect,
one selected recipe rather than the union of modes and types, prose in `content`
and machine-actionable data in `structuredContent`, and the two mode-specific
identities.

**The discovery pointer.** A04 froze the requirement that `context_evidence_save`
and `diagram_request_save` rejections name where the contract can be fetched, but
could not implement it: the tool was unregistered, so a rejection naming it would
have sent a host nowhere. That precondition is removed by this package, so the
pointer lands here with the tool that makes it true.

Discovery must not depend on cooperation. A host that never calls the workflow route
and never calls the lookup still learns the contract exists from the rejection it
actually receives.

### Boundaries

Scope is the host-facing authoring surface only. Not in scope: the snapshot redesign
and claim-version removal; lockfile exclusion from eligible source, which changes the
source fingerprint and stales existing canonical JSON 1; recomposing `evidence[]`,
retired by `r1`; and anything owned by Lane B — generation, semantic review, or
provider runtime.

No schema file changes. No provider call.

### Verification

Focused tests for argument validation, selected-only output, both mode identities,
side-effect freedom, the byte budget, and a rejection that names the lookup. Full
backend suite. Independent implementation audit.

Whether this actually reduces authoring rounds is measured by a later clean-room
reference observation `r2` using the frozen prompt, not by this package. `r2` is
recorded as its own item, because a package cannot verify its own field result.

### Exit criteria

1. The lookup returns exactly one mode and type recipe with a complete,
   placeholder-free, leakage-disjoint example, and never the union.
2. Its two required arguments are enforced, and it has no workspace, provider,
   filesystem, or trace input.
3. Invocation has no filesystem or provider side effect.
4. Save-tool rejections name where the contract is fetched.
5. The combined route plan plus one recipe stays within the 8,212-byte budget.
6. No schema change; the accepted document set is unchanged by construction.
7. Focused tests and the full backend suite pass; independent audit has no
   unresolved critical, high, or medium finding.

## Plan audit

🔄 Pending.

## Implementation

🔄 Not started.

## Implementation audit

🔄 Pending.

## Verification

🔄 Pending.

## Outcome

🔄 To be completed.
