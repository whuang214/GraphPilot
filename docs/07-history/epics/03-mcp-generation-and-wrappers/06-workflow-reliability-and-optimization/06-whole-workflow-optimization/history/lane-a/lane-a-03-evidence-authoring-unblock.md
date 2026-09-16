# Lane A Slice 03: Evidence Authoring Unblock

## Purpose

Make cold JSON 1 authoring possible and self-correcting: stop requiring the host to supply values only the backend can know, and report the intended schema branch's exact defects instead of one generic `oneOf` rejection.

## Background

A02 established that a cold host cannot complete JSON 1 authoring against the current interface. Two independent causes were proven from the recorded draft, both reproducible through the production validation path.

**Undecidable required fields.** `repositoryEvidence` requires `contentDigest`, `capturedInSourceDigest`, and `status`. A host cannot derive any of them, and `contentDigest` is additionally ambiguous because nothing states what to hash or how to canonicalize it. None is verified in production; a readiness test asserts `contentDigest` and `capturedInSourceDigest` are stripped before the provider sees them, and existing harnesses set `capturedInSourceDigest` mechanically to the manifest-level source digest on every entry.

**Unactionable failures.** All 32 entries returned one issue — `schema_oneOf` at `$.evidence[N]`, message `is not valid under any of the given schemas` — naming no missing property, no allowed enum value, and no branch. The workflow response never states the evidence contract either, so the shape is unobtainable through the interface.

Together these make the workflow a dead end by construction rather than a host weakness.

The `r0` reference observation isolated the blocker precisely. Submitting the manifest with `evidence: []` produced **no schema findings at all**, proving every other substructure validates. Roughly 1,480 evidence record shapes across 16 batched probe submissions all failed with the same opaque message.

The decisive contrast is inside the same schema: `claims[].versions[].payload` is composed with conditional `if`/`then` subschemas keyed on claim `kind`, so its findings are precise, and the host recovered the complete payload contract for seven claim kinds purely from validation output. `evidence[]` is the one structure that uses a bare `oneOf`, and it is the one structure that proved unlearnable. The schema already demonstrates the pattern that works.

The observation also exposed a third defect: issue lists are silently truncated, reported only as `additional_issues_omitted` at `$`. That matters more once branch reporting emits more issues per document.

## Design

### Derive what the backend already knows

`_normalize_manifest` already fills `digest`, `revision`, `createdAt`, and `updatedAt` before validation runs. Extend that same pass to fill, **only when the host omitted them**, per evidence entry:

- `capturedInSourceDigest` from the source fingerprint passed into normalization;
- `status` as `current`, which is what a current-only snapshot means;
- `contentDigest` from the canonical digest of the located source region identified by the entry's `locator`.

Filling only absent values keeps every existing writer valid, including the live-anchor harness, the workflow-audit runner, and the frozen S15 fixtures, all of which set these fields today.

Deliberately **no schema change**. The canonical manifest keeps its required properties, so no downstream consumer, fixture, or persisted artifact changes shape. The host simply stops being asked for values it cannot produce, leaving `{id, kind, locator, summary, capturedAt}`.

A locator that cannot be resolved is an explicit validation failure, never a silent empty digest.

### Report the intended branch

In `_schema_issues`, when a validator is `oneOf` or `anyOf`, descend into `error.context` rather than emitting the generic error:

1. Group sub-errors by branch index, taken from the first element of each sub-error's `schema_path`.
2. Select the intended branch: if exactly one branch constrains a discriminator property by `const` or `enum` and the document satisfies it, choose that branch; otherwise choose the branch with the fewest sub-errors, breaking ties by lowest branch index.
3. Emit that branch's sub-errors with their own `schema_<validator>` codes, messages, and absolute paths.

Non-`oneOf` errors keep their current mapping. Ordering stays deterministic through `_sorted_result`, because `jsonschema` produces the same sub-errors in the same order for a given document and schema.

Branch indexing was verified empirically rather than assumed. Although both evidence branches are `$ref`s, `jsonschema` resolves them and preserves the index at `schema_path[0]`, emitting `[0, 'required']` and `[1, 'required']`. On the recorded document neither discriminator matches, so the fewest-errors rule applies: `repositoryEvidence` yields 6 sub-errors against `userClarificationEvidence`'s 8, and the reported issues name the missing properties, the `kind` enum with its allowed values, and the unexpected `locator.lines` property.

The schema contains one other `oneOf`, at `$defs.multiplicity.properties.upper`, which mixes a `$ref` branch with an inline `const`. It is covered by regression tests so the mixed form is proven to group correctly.

### Surface omitted issues honestly

Truncation currently collapses into a single `additional_issues_omitted` marker at `$`, so a host cannot tell how much it is not being told. Report the omitted count and keep the marker deterministic, so a host knows to resubmit for the remainder rather than assuming it has seen every defect.

### Why the reporting layer rather than the schema

The strongest structural fix is to recompose `evidence[]` with the conditional `if`/`then` form already used by claim payloads. That is a **schema change**, so it belongs to A04's contract work, where owners, examples, and compatibility are handled together.

A03 deliberately takes the reporting-layer fix instead, for three reasons: it is sufficient to convert the dead end into precise findings, it needs no schema or contract change, and it protects every other `oneOf` in the system rather than this one site. If A04 later recomposes `evidence[]`, best-branch reporting remains valuable as the general safety net.

### Why both changes share one slice

They are the two halves of one outcome and share one proof. Derivation removes the impossible fields; branch reporting makes whatever the host still gets wrong self-correcting. Neither alone satisfies the cold completion criterion.

## Included Work

- Extend evidence normalization to derive `contentDigest`, `capturedInSourceDigest`, and `status` when absent.
- Replace generic `oneOf`/`anyOf` reporting with best-branch selection.
- Report the number of omitted issues rather than only the `additional_issues_omitted` marker.
- Add focused tests: a host-authorable candidate containing only `{id, kind, locator, summary, capturedAt}` promotes successfully; derived values are stable across repeated runs; host-supplied values are preserved rather than overwritten; an unresolvable locator fails explicitly; the recorded failing entry now yields named defects; the discriminator-match path selects a branch even when it carries more sub-errors; the mixed `multiplicity.upper` branch groups correctly; non-`oneOf` issues and passing documents are unchanged; ordering is deterministic under an equal-count tie.
- Run the cold-authoring retest and record its classification as slice evidence.

No canonical design owner update is required. `02-validation-design.md` owns canonical **diagram** validation; context-document validation has no separate design owner and its codes live in `services/context/context_validation_contract.py`. This slice changes which sub-errors are reported and which values are derived, not the code vocabulary or any contract. If the implementation audit finds an owner that documents these codes, update it in the same change.

## Not In Scope

- Schema or contract changes, including removing any required property.
- The router and authoring-contract tools, which remain with A04 and A06.
- The diagram validation service, a separate owner that may share the `oneOf` pattern; record it as a follow-up rather than changing it here.
- Any host, provider, frontend, or Lane B behavior.

## Target Areas

- `backend/services/context/context_persistence_service.py`
- `backend/services/context/context_document_validator.py`
- `backend/tests/core/test_context_persistence_service.py`
- `backend/tests/core/test_context_document_validator.py`
- `evidence/lane-a-reference-host/` retest record
- This Outcome

## Exit Criteria

- A candidate whose evidence entries contain only host-authorable properties promotes successfully, and the canonical manifest that results is schema-valid and unchanged in shape.
- Derived values are deterministic across runs; host-supplied values are preserved; an unresolvable locator fails with an explicit issue.
- Revalidating the recorded draft yields no `schema_oneOf` and names every missing property, the allowed `kind` values, and the unexpected `locator.lines`.
- The mixed `multiplicity.upper` branch reports actionable sub-errors; non-`oneOf` issues, passing documents, and existing writers are unchanged.
- Truncated issue lists report how many issues were omitted.
- A host-authorable candidate derived from the `r0` recovered contract promotes end to end, proving the blocker is removed rather than relocated.
- The cold-authoring retest is executed and its failures classified as guidance, payload, or semantic.
- Focused tests and the full backend suite pass, and an independent implementation audit confirms no schema, contract, or persisted-artifact change.

## Previous Slice

[`lane-a-02-devin-host-transition.md`](lane-a-02-devin-host-transition.md)

## Next Slice

[`lane-a-04-authoring-discoverability.md`](lane-a-04-authoring-discoverability.md), scoped by the retest classification.

## Outcome

**Status:** Complete · implementation verified and the cold-host retest passed its blocking gate.

**Completion:** Evidence normalization now derives `capturedInSourceDigest`, `status`, and `contentDigest` for repository evidence, only when the host omitted them, extending the pass that already fills `digest`, `revision`, `createdAt`, and `updatedAt`. No schema changed, so the canonical manifest keeps its shape and existing writers — the live-anchor harness, the workflow-audit runner, and the frozen S15 fixtures — are untouched. Deterministic validation now reports the intended branch of a failed `oneOf`/`anyOf` instead of the generic rejection, selecting by matched discriminator and otherwise by fewest defects with a deterministic tie-break.

Against the exact `r0` failing entry, one opaque `schema_oneOf` becomes six actionable defects: the four missing properties, the `kind` enum with its allowed values, and the unexpected `locator.lines`.

**Deviations:** Three planned items changed on evidence.

The "silently truncated issue lists" defect was **not implemented, because it does not exist**. `_issue_details` already appends the omitted count in the marker's message. No code was added for a problem that is already handled.

Digest derivation was **narrowed to eligible source only**. The implementation audit raised symlink following as critical; investigation showed the real exposure was broader, since a locator could name `.env` directly with no symlink involved. Derivation now skips excluded paths and links on the same terms as source fingerprinting, so a derived digest can never read a secret, a generated artifact, or a link target the fingerprint refuses to walk. That is stricter than the audit's recommendation and semantically correct: `contentDigest` describes eligible source.

The audit's fragility note about `schema_path[0]` was **rejected for the plan's original claim but retained as a caution**: an empirical probe confirmed `jsonschema` resolves `$ref` branches and preserves the branch index, and the recursion handles nesting. Its redundant-fingerprinting observation is pre-existing behavior and out of this slice's scope.

**Verification:** Full backend suite **1080 tests, 6 skipped**, up from 1069 by eleven new tests. Focused validator and persistence tests pass. An end-to-end proof through the real MCP `context_evidence_status` and `context_evidence_save` tools, over real Todo fixture source in a temporary workspace, promoted a candidate whose evidence entries carried only `{id, kind, locator, summary, capturedAt}`, with all three managed values correctly derived. Security and edge cases are covered: excluded and secret paths, symlinks, path escape, directories, non-UTF-8 content, and line ranges beyond end of file all decline a digest and surface a normal missing-property issue. Zero provider calls.

**Retest result:** A clean-room cold host ran the frozen prompt against the untouched fixture and **completed the workflow**, recorded in `evidence/lane-a-reference-host/r1.json`.

| | `r0` before | `r1` after |
| --- | --- | --- |
| JSON 1 | never saved | 69,823 bytes · 48 claims · 20 relationships |
| JSON 2 | never reached | 10,532 bytes |
| `context_evidence_save` calls | 22, including ~1,480 probed shapes | 7 |
| `schema_oneOf` issues | every evidence entry | **none** |

The blocking defect is removed in the wild: no generic `oneOf` rejection appears anywhere in `r1`, replaced by precise per-property codes, and the host never authored a derived value. The workflow response is unchanged, as expected, since this slice did not touch it.

**The cold completion criterion is not yet met.** It requires at most two attempts per document; `r1` needed seven and four. The interface is usable but still expensive, so the gate stands for A04 through A06.

**Classification for A04:** the residual cost is dominated by **guidance**, not payload.

1. No tool returns the evidence or request contract the way `diagram_get_schema` does for diagram types, so both documents were reverse-engineered from validator output. Enum and `const` values are learnable only by failing.
2. Validation reveals one layer at a time — claim, then versions, then payload, then claim references — because each level is only reached once the level above is satisfied. Every round exposes the next layer.
3. Truncation cost real rounds: `146 additional issues were omitted` hid sibling problems.
4. Line narrowing was abandoned after three rejected spellings of the locator range, so evidence degraded from precise regions to whole files. That is a **quality** loss caused by naming, not by policy.

Payload remains secondary but real at 69.8 KB and 48 claims for a 17-file repository.

**Correction to this slice's own deviation record:** the truncation finding was dismissed above as non-existent because `_issue_details` reports the omitted count. That was half right and wrong on impact. The count is reported, but the 255-issue cap still hides sibling defects, and `r1` shows it directly costing extra authoring rounds. Truncation belongs in A04's scope; the earlier dismissal stands corrected here rather than being quietly edited away.

**Follow-up:** A04 is now scoped by evidence rather than assumption. Its strongest candidates are contract discoverability for evidence and request documents, the `evidence[]` conditional recomposition, locator range naming, truncation behavior, and excluding lockfiles, which account for 38 KB of the fixture's 68 KB.
