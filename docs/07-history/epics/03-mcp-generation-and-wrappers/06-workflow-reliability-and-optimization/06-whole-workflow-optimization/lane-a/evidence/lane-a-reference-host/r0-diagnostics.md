# r0 diagnostics — reference host, current interface

Companion to `r0.json`. `r0.json` is the machine-readable observation; this file holds the
detail needed to **fix** what the run exposed. Nothing here was read from the GraphPilot
repository: every schema fact below was recovered solely from `context_evidence_save`
validation findings during the run.

## Run identity

| Field | Value |
| --- | --- |
| Observation | `r0` |
| Host | Devin CLI, provider-free MCP entry point (`mcp_server.host_benchmark_server`) |
| Fixture | Todo API fixture workspace, commit `8627bac5169e3a8800ea7f3ddfb64e52b4fe92c7` |
| Authority mode | context |
| Diagram type | `bdd_diagram` |
| Evidence identity | `evidence-todo-api-r0` |
| Request id / diagram name | `request-todo-api-r0` / `todo-api-r0` |
| Provider calls | none — readiness, generation and render were never invoked |

## Outcome

**Blocked before JSON 1 could be saved.** `diagram_request_save` was therefore never reached.

The document reached a state where **every part except `evidence[]` validates**. Submitting the
manifest with `evidence: []` produced *no* schema findings at all — only 55 semantic
`missing_evidence_ref` findings for the dangling `support.evidenceRefs` and
`relatedEvidenceRefs`. That isolates the `evidence[]` item schema as the single blocker.

## MCP call ledger

| Tool | Calls | Notes |
| --- | --- | --- |
| `diagram_generation_workflow` | 1 | 8223-byte text payload (16812 bytes of Inspector stdout incl. envelope) |
| `context_evidence_status` | 1 | `missing`; 17 eligible files; default `.` scope kept |
| `context_evidence_save` | 22 | 6 genuine authoring attempts + 16 diagnostic probe submissions |
| **Total** | **24** | `tools/list` (discovery, not a tool call) additionally ran once |

Two of the 22 saves were **accidental unchanged resubmissions**: a probe generator script raised
before the MCP call in a chained shell command, so the previous candidate was resubmitted
byte-identical. Worth noting because the workflow explicitly forbids repeating an unchanged call —
the *host tooling*, not the operator, caused it.

Source files read from the fixture: **11** (`README.md`, `pyproject.toml`, and the nine
`src/todo_api/*.py` modules). Tests and the lockfile were deliberately not read.

## Recovered JSON 1 contract (complete, except `evidence[]`)

Recovered purely from findings. This is what a clean-room host *can* learn today.

**Document root** — `additionalProperties: false`. Required: `evidence`, `id`, `kind`, `scope`.
Also accepted: `schemaVersion`, `source`, `claims`, `uncertainties`.
`kind` is `const: "evidenceManifest"`.

**`source`** — required `kind`, `root`, `displayName`.

**`scope`** — required `baseline`, `includedConcerns`, `stoppingReason`; also `includedPaths`,
`excludedPaths`. `sourceDigest` is **rejected** here (the digest travels as the
`expectedSourceDigest` argument only).
- `baseline` is `const: "boundedArchitecture"`.
- `includedConcerns` enum: `systemPurpose`, `systemBoundaries`, `publicEntryPoints`,
  `topLevelComponents`, `externalSystems`, `publicCapabilities`, `importantInterfaces`,
  `majorWorkflows`, `importantConstraints`.

**`claims[]`** — required `id`, `kind`, `status`, `currentVersion`, `versions`.
`id` pattern `^claim-[a-z0-9]+(?:-[a-z0-9]+)*$`. No `label` property.
`kind` enum: `boundary`, `entity`, `capability`, `actorGoal`, `relationship`, `behaviorStep`,
`property`, `constraint`. Relationships are claims of kind `relationship` — there is **no**
top-level `relationships` array.

**`claims[].versions[]`** — required `appliesToViewpoints`, `payload`, `support`; also `version`,
`statement`, `createdAt`.
`appliesToViewpoints` enum: `as_implemented`, `as_designed`, `as_required`, `domain_fact`.

**`claims[].versions[].support`** — required `basis`, `derivation`; also `evidenceRefs`.
`confidence` is rejected. `basis` enum: `repositoryEvidence`, `userClarification`, `mixed`.
`derivation` accepted the value `direct`.

**`claims[].versions[].payload`** — discriminated by claim `kind` via conditional subschemas, so
findings are precise. Required per kind:

| Claim kind | Required payload | `name` allowed |
| --- | --- | --- |
| `boundary` | `included`, `external` | yes |
| `entity` | `role`, `purpose` | yes |
| `capability` | `subject`, `outcome` | no |
| `behaviorStep` | `actor`, `action` | no |
| `property` | `ownerClaimRef`, `valueType` | yes |
| `constraint` | `subjectClaimRef`, `rule` | no |
| `relationship` | `relationship`, `sourceClaimRef`, `targetClaimRef` | no |
| `actorGoal` | not exercised | — |

`summary` is rejected in every payload.

**Claim references** are objects `{ "id": "claim-…", "version": n }` — the key is `id`, not
`claimId`. This applies to `ownerClaimRef`, `subjectClaimRef`, `sourceClaimRef`,
`targetClaimRef` and `uncertainties[].relatedClaimRefs[]`.

**`uncertainties[]`** — required `id`, `kind`, `createdAt`, `relatedClaimRefs`,
`relatedEvidenceRefs`, `suggestedSearches`; also `statement`.
`id` pattern `^uncertainty-[a-z0-9]+(?:-[a-z0-9]+)*$`.
`kind` enum: `missing_information`, `ambiguous`, `contradictory`, `changed_source`,
`unsupported_inference`.
`relatedEvidenceRefs[]` are **strings** matching `^evidence-[a-z0-9]+(?:-[a-z0-9]+)*$`
(while `relatedClaimRefs[]` are objects — an easy asymmetry to trip on).

## The blocker: `evidence[]`

Every submitted evidence record returns exactly one finding:

```
schema_oneOf | $.evidence[N] | {…the record…} is not valid under any of the given schemas
```

No `required`, no `enum`, no `additionalProperties`, no branch name, no `$ref`. The error
envelope (`error.details`) contains only `issues`; there is no `schemaRef` or hint field.

### Why this is unrecoverable by probing

Each branch appears to enforce `additionalProperties: false`, so a probe passes only if its
property set sits **exactly** between the branch's required set and its allowed set. Adding a
guess is as fatal as omitting a requirement, which defeats group testing: the search is
exponential in an unknown vocabulary with no feedback gradient.

### Probe coverage (all negative — ~1480 record shapes over 16 batched submissions)

The evidence array length is unconstrained, so up to ~230 shapes were tested per call.

- **`kind` values (110+)**: `repository`, `repositoryEvidence`, `repositoryFile`,
  `repositorySymbol`, `repositoryExcerpt`, `sourceFile`, `sourceEvidence`, `file`, `code`,
  `source`, `document`, `userClarification`, `mixed`, snake_case forms, capitalised forms, and
  `kind` omitted entirely.
- **Container shape**: `locator` object, `locator` array, `locators` array, inline `path`,
  `paths`, `payload`, `location`, `reference`, `ref`, `file`, `sourceRef`, `artifact`; bare
  string item; bare `{path}` object; empty-ish items.
- **Locator shape (22)**: `{path}`, `+symbol`, `+lines {start,end}`, `lines [a,b]`, `lines "a-b"`,
  `{from,to}`, `{startLine,endLine}`, `startLine`/`endLine`, `lineStart`/`lineEnd`,
  `firstLine`/`lastLine`, `range`, `span`, inner `kind`, `repoRelativePath`, `workspacePath`,
  `relativePath`, `+sha256`, `+digest`.
- **Identity key**: `id`, `evidenceId`, `ref`, `key`, `name`, `uid`, `identifier`, `slug`, none.
- **Property-name sweep**: 182 distinct single additions (timestamps, digests, text/excerpt
  variants, reference arrays, classification, provenance, quality, scope fields).
- **Subset sweeps**: all pairs of 20 likely names; all size-3 subsets of 10 names; all size-3..8
  subsets of 8 names; size-0..3 subsets crossed with three locator shapes.
- **Value-type variants**: text vs object vs array for `excerpt`/`content`/`statement`/`summary`;
  claim-ref arrays for `supports`/`claimRefs`.
- **Structural mirrors**: claim-shaped `{status, currentVersion, versions[]}`, embedded
  `support`, embedded `payload`.
- **Kitchen sink** (42 properties at once, 8 `kind` values, plus every leave-one-out): all fail,
  which is what establishes `additionalProperties: false` on the branches.

## Recommended fixes

1. **Make `evidence[]` diagnosable.** Replace the bare `oneOf` with the same conditional
   (`if`/`then` on `kind`) composition already used by `claims[].versions[].payload`. That alone
   converts an opaque dead end into the precise findings that made every other structure
   learnable. This is the single highest-value change.
2. **If `oneOf` must stay**, have the validation layer select the best-matching branch (e.g.
   jsonschema `best_match`, or discriminate on `kind` before validating) and surface that
   branch's `required`/`enum`/`additionalProperties` findings.
3. **Expose the JSON 1 contract through the tool surface.** There is a `diagram_get_schema` for
   diagram types but no equivalent for the evidence manifest or the request. A
   `context_get_schema` (or extending `diagram_get_schema` with the manifest/request schema ids)
   would let any host author correctly on the first attempt instead of by validation archaeology.
4. **Stop truncating findings silently.** `additional_issues_omitted: "46 additional issues were
   omitted."` hides which paths were dropped; findings appear to be ordered by path, so late
   sections (`evidence`, `scope`, `uncertainties`) are the ones that vanish. Either report a
   per-section summary of what was omitted, or cap per path prefix rather than globally.
5. **Reduce avoidable first-attempt churn.** Several conventions are guessable-but-unstated by
   the workflow instructions and cost a round trip each: `kind: "evidenceManifest"`, the three
   `id` patterns, `scope.baseline` as a const string rather than an object, digest belonging to
   the call argument rather than the document, relationships being claims, and claim refs keyed
   `id` while evidence refs are plain strings. Naming these in the workflow instructions (or in
   the schema tool from fix 3) would remove most of the six authoring attempts.
6. **Align the instructions with the schema.** The workflow text describes `locator.path` with
   "optional symbol/lines"; whatever the evidence record actually requires beyond that is not
   described anywhere a host can see.

## Artifacts left behind

- Best-effort JSON 1 draft (never promoted, since a failed save writes nothing) at
  `.graphpilot/context/drafts/todo-api-r0.gp-evidence.candidate.json` in the fixture workspace:
  52061 bytes, 34 claims (16 subject + 18 relationship), 32 evidence records, 2 uncertainties.
  Everything in it validates except the evidence records.
- The fixture's tracked source and tests are unmodified; `git status` shows only the untracked
  `.graphpilot/` directory.
- No `.graphpilot/requests/` artifact exists, because JSON 2 was never authored.

## Follow-ups not done here

The clean-room rule barred reading anything in the GraphPilot repository, so the epic's
`00-current-state.md` board and slice `## Outcome` sections were **not** updated. Someone with
the repository open should fold this observation into the delivery docs.
