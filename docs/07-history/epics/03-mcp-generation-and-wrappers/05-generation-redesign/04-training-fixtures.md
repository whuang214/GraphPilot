# Slice 04: Training Fixtures

## Purpose

Replace the legacy sorted-path direct few-shot examples with twelve approved, versioned, independently reviewed direct/context source fixtures and six immutable ordered set manifests whose runtime pairs, canonical outputs, digests, and render evidence are derived deterministically and cannot leak held-out identities.

## Background

The current runtime has four direct training directories per type and context generation projects those direct outputs despite their lack of context authority/origins. The redesign requires two fixed direct examples and two fixed context-native examples for each diagram type. Production packet builders from Slice 03 must fail when their exact set is absent or invalid; they may not retain the old pool, vary count, pick by tags/similarity, or silently substitute another example.

These are visible model-training fixtures, not built-in evaluation gold and not RepoBench cases. A runtime generation tool must never author its own fixture. Source authority and hand-authored logical gold are the reviewable inputs; compact `{input, output}` pairs, populated packets, canonical diagrams, SVG/gallery artifacts, and digests are derived outputs.

## Design

### Dependencies and canonical owners

- Slices 01–03 must be complete: fixture/example/manifest schemas and IDs, request validation/persistence, generation-input builders, six logical schemas, semantic profiles, and deterministic serialization are prerequisites.
- `docs/02-design-and-features/06-answer-key-generation-design.md` is the canonical fixture/authoring/sign-off owner after Phase 0B; `04-generation-design.md` owns runtime set loading and packet inclusion.
- `docs/03-development-and-delivery/01-testing-strategy.md` owns offline fixture/schema/render proof. Hidden evaluation cases remain under the evaluation design and cannot be authored or reserved here.

### Source and derived shapes

Use the promoted source layout beneath each type's blueprint area:

```text
direct-examples/training/<name>/
  request.gp-request.json
  expected.logical.json
  output.gp.json
  metadata.json

context-examples/training/<name>/
  evidence.gp-evidence.json
  request.gp-request.json
  expected.logical.json
  output.gp.json
  metadata.json
```

The expected logical graph is hand-authored against the exact mode/type schema. Direct request authority derives the compact direct input. Context evidence plus request passes the real resolver/projection path and derives the compact context input with exact selected claims, assumptions, allowlists, and smallest-sufficient origins. Runtime example files use the separate exact direct/context `{input, output}` contracts and are never edited independently.

Metadata uses `graphpilot.generation.training-fixture-metadata.v1` and records exact example ID, mode/type, foundational/advanced level, bounded domain/structure tags, author/time, a distinct reviewer/time, `reviewStatus: approved`, request/logical/profile versions, and input/output digests. Do not invent people, timestamps, approval, or use the same identity for author and reviewer. Fixture authoring is implementation work in this slice, not an entry prerequisite. The author produces authority/logical gold without seeing a generated alternative; a stateless independent reviewer receives the frozen source, derived artifacts, automated reports, and gallery but not author coaching, records evidence-backed findings, and approves only after every finding is resolved. Honest tool/agent role identities and actual UTC review times may be recorded; a placeholder, fabricated person, self-review, or merely copied approval cannot pass.

### Exact sets and order

| Set version | Foundational first | Advanced second |
| --- | --- | --- |
| `graphpilot.direct.training-examples.activity.v1` | `parcel-locker-pickup` | `device-repair-assessment` |
| `graphpilot.context.training-examples.activity.v1` | `return-authorization` | `multi-channel-alert-delivery` |
| `graphpilot.direct.training-examples.use-case.v1` | `pet-care-appointment-portal` | `makerspace-access-system` |
| `graphpilot.context.training-examples.use-case.v1` | `volunteer-shift-portal` | `equipment-maintenance-portal` |
| `graphpilot.direct.training-examples.bdd.v1` | `camping-stove-specification` | `digital-publishing-platform` |
| `graphpilot.context.training-examples.bdd.v1` | `irrigation-controller` | `laboratory-analyzer-platform` |

Each `graphpilot.generation.training-example-set.v1` manifest fixes one mode/type, exactly those two ordered IDs, fixture-metadata digest, runtime input/output digests, and canonical set digest. One fixture change versions only its mode/type set. Runtime generation records set version/digest and ordered IDs; it never selects by directory sort, tag, lexical match, embeddings, environment count, or token pressure.

### Required semantic coverage

- Direct Activity: guarded success/failure for Parcel Locker Pickup; fork/join followed by a guarded decision for Device Repair Assessment.
- Context Activity: exact claim/schema grounding for Return Authorization; concurrent email/SMS work, retry, merges/join, and one accepted assumption for Multi-Channel Alert Delivery.
- Direct Use Case: subject/actors/associations/include for Pet Care Appointment Portal; include/extend, target extension point, condition, and actor generalization for Makerspace Access System.
- Context Use Case: fully grounded subject/actors/capabilities/include for Volunteer Shift Portal; grounded include/extend/extension location/generalization for Equipment Maintenance Portal.
- Direct BDD: one compact Block with typed features and no edges for Camping Stove Specification; separate definitions plus association/composition/generalization/dependency for Digital Publishing Platform.
- Context BDD: claim-grounded composition, properties, multiplicity, and association for Irrigation Controller; mixed structures plus a bounded accepted multiplicity assumption for Laboratory Analyzer Platform.

Every direct logical element has no origin. Every context node/edge has one smallest-sufficient allowlisted origin; only a neutral Activity initial node may use `activity.initial-node`. Relationship direction, containment, guards, extension locations, BDD multiplicities/features, and no unsupported filler match the promoted exact fixture owner.

### Derivation, layout handoff, and removal

A deterministic fixture tool/test derives runtime pairs and digests, validates logical topology/provenance, produces or checks canonical `output.gp.json`, runs canonical validation, round-trip checks, and renders an SVG/gallery for review without an LLM. Because PyGraphviz integration is Slice 07, this slice proves the authored semantics and canonical/render output are **PyGraphviz-ready** and records the mandatory S07 re-layout/gallery parity gate; it must not claim that the future runtime engine was already integrated. S07 may change derived layout evidence, not silently alter fixture authority or logical gold.

After all twelve replacements, manifests, loaders, packet snapshots, and galleries pass—and only within the exact destructive scope already approved—remove these twelve legacy runtime training directories atomically:

```text
activity_diagram: 01-employee-onboarding, 02-password-reset, 03-coffee-order, 04-support-ticket
use_case_diagram: 01-recipe-app, 02-it-helpdesk, 03-fitness-tracker, 04-library-portal
bdd_diagram: 01-drone, 02-smart-thermostat, 03-account-types, 04-online-store
```

Do not remove or relabel existing `eval/` directories, hidden/evaluation artifacts, prompts, schemas, or any other blueprint directory in this slice. Verify the actual deletion list against the approved migration record immediately before removal; any mismatch stops the slice.

Rollback is one atomic revert of the fixture/set/loader commit, restoring all twelve tracked legacy directories and removing the replacement assets together. Never leave a mixed direct/context set or manually reconstruct deleted files. Generated gallery output outside tracked fixture sources is disposable only when it is clearly slice-owned; user artifacts are never deleted.

## Plan Audit

The plan audit must verify:

- **Dependencies:** S01 schemas/IDs, S02 request validation, and S03 builders/logical contracts exist before fixture authoring/activation.
- **Exact inventory:** all twelve scenario IDs, modes, types, foundational/advanced levels, and six manifest orders match the promoted owner exactly.
- **Authority:** source request/evidence precedes hand-authored logical gold; a runtime generator never authors or approves its own examples.
- **Context grounding:** every context element cites only selected/accepted/allowlisted refs with smallest-sufficient origins; schema-only meaning is limited to the neutral Activity initial node.
- **Derivation:** runtime pair, populated input, canonical output, digest, and SVG/gallery evidence are reproducible from source and cannot be edited independently.
- **Sign-off:** author/reviewer are real, distinct roles and contexts; the reviewer sees frozen source/derived evidence, records findings independently, and signs only after automated/semantic/gallery review and finding resolution. Placeholders, self-review, copied, or fabricated approval cannot pass.
- **Selection:** exactly two examples are loaded in manifest order with no sorted-directory, configurable-count, similarity, fallback, drop, or substitution path.
- **Leakage:** no training identity overlaps held-out/RepoBench identities, no `eval/` key enters a runtime packet, and no gold path/content reaches unrelated generation inputs.
- **Layout sequence:** S04 proves PyGraphviz-ready semantic/canonical/render fixtures; S07 owns actual PyGraphviz engine/gallery parity and must not be falsely reported here.
- **Destructive scope:** only the twelve explicitly approved legacy training directories are removed after replacement gates; `eval/`, user files, and all other assets remain.
- **Reversibility:** the set changes and deletions are one atomic commit/revert boundary with no partial mix.
- **Verification:** add failing fixture/manifest/packet/schema/provenance/canonical/render tests before fixture activation; keep them provider-free, then require the full backend suite, gallery command/tests, stale identity searches, and `git diff --check`.

Plan audit result: **Pass after correction.** The audit confirmed the exact twelve scenarios/manifests, source-first authority, deterministic derivation, context-origin minimality, fixed selection, visible-training versus hidden-gold separation, honest independent review protocol, explicit pre-deletion list check, and atomic replacement rollback.

## Included Work

- Author six direct and six context source fixtures under the exact scenarios and source shapes above.
- Hand-author exact logical gold and canonical expected output; derive compact runtime pairs and populated packet snapshots deterministically.
- Add complete metadata with distinct author/reviewer sign-off and exact contract/profile/input/output identities.
- Add six immutable two-entry ordered set manifests with canonical per-entry and set digests.
- Replace directory-sorted/configurable few-shot loading with exact manifest loading for both modes; fail closed on any missing/corrupt/mismatched asset.
- Add fixture validation for request/evidence, strict logical schemas, current core vocabulary, graph topology, context allowlists/origins, canonical output, round trip, and render.
- Extend the backend gallery path/tests to review all twelve outputs without requiring Azure.
- Add leakage/inventory tests proving production packets use only the intended training pair and no held-out/RepoBench identity.
- Remove exactly the twelve approved legacy runtime training directories only after all replacement and consumer gates pass.
- Record the S07 PyGraphviz re-layout/parity dependency without claiming it complete.

## Not In Scope

- Authoring, reserving, reviewing, or running any of the future 48 hidden built-in cases or RepoBench golds.
- Using a live/runtime LLM to draft fixture authority or logical gold.
- Changing evaluation `eval/` directories into training, deleting them, or using them in runtime packets.
- PyGraphviz dependency/engine integration or old-layout removal; those are Slices 07–08.
- Semantic runtime review, evaluator matcher/judge, live embedding/generation calls, or production certification.
- Public MCP cutover, frontend feature work, `.env` access, database/auth changes, or arbitrary blueprint cleanup.

## Target Areas

- `backend/assets/blueprints/{activity_diagram,use_case_diagram,bdd_diagram}/{direct-examples,context-examples}/training/`
- versioned training-set manifests under the promoted blueprint/example asset owner
- the deterministic fixture derivation/seeding utility under `backend/assets/blueprints/`
- Slice 03's generation example-set loader and packet builders under `backend/services/generation/`
- `backend/operations/management/commands/render_example_gallery.py`
- `backend/tests/generation/test_samples.py`, focused fixture/manifest/packet/provenance tests, and `backend/tests/api/test_render_example_gallery.py`
- the twelve exact legacy `backend/assets/blueprints/<type>/examples/training/<name>/` directories listed above, only after replacement proof
- `docs/02-design-and-features/06-answer-key-generation-design.md`, `04-generation-design.md`, and `docs/03-development-and-delivery/01-testing-strategy.md` only for implementation-backed corrections
- this slice document and the live current-state board for implementation outcome/status only

## Exit Criteria

- Immediately before removal, the actual candidate deletion list matches exactly the twelve tracked directories recorded in `migration-plan-approval.json`; any extra/missing path stops the slice, and `eval/`, user artifacts, and all unlisted paths remain untouched.
- All twelve source fixtures validate against their exact request/evidence and mode/type logical schemas and use only the current core profile.
- Exact topology, direction, containment, guards, extension locations, feature fields, multiplicities, and context origin intent match the promoted fixture specification.
- Every runtime pair and canonical output is reproducibly derived; recorded input/output/metadata/set digests match exact canonical bytes.
- Every metadata record has a real author, a distinct real reviewer, approved timestamps/status, and completed semantic review; no placeholder remains.
- Each set manifest contains exactly its foundational then advanced example, and runtime packet tests prove exact set version/digest/order with no fallback or configurable count.
- Context refs are selected/accepted/allowlisted, direct output has no origins, schema-only grounding is limited correctly, and identity-leakage tests pass.
- All twelve canonical outputs validate, round-trip, render, and appear in the reviewed backend gallery; S07's separate PyGraphviz parity obligation is recorded, not claimed complete.
- Exactly the twelve approved legacy training directories are absent after activation; all `eval/` directories and unrelated assets remain untouched, and stale-loader/identity searches pass.
- Focused fixture/manifest/packet/gallery tests and `cd backend; uv run python manage.py test` pass fully offline; no provider call occurs.
- `git diff --check` and the implementation audit pass with no unresolved finding; rollback has been reviewed as one atomic set revert.

## Previous Slice

- [`03-strict-generation-contracts.md`](03-strict-generation-contracts.md)

## Next Slice

- [`05-pre-layout-repair-pipeline.md`](05-pre-layout-repair-pipeline.md)

## Outcome

**Completion:** Replaced the twelve legacy direct training directories with six direct and six context-native fixed source
fixtures across Activity, Use Case, and BDD; derived deterministic runtime pairs and canonical outputs; recorded honest
distinct agent author/reviewer identities; and wrote six immutable foundational-then-advanced manifests with complete
metadata/input/output/set digests. Added fail-closed source/semantic/origin/PyGraphviz/canonical validation and manifest
loading, moved current direct/context compatibility loaders to the new mode-specific sources, and extended the gallery to
render both training modes.

**Deviations:** Canonical fixture outputs use the current deterministic Grandalf-backed assembly only as a persisted
pre-S07 gallery baseline; every strict logical source also passed direct `pygraphviz==2.0` layout proof, and Slice 07 owns
the final re-layout/parity snapshots. Machine-authored training sign-off records distinct stateless agent identities rather
than representing them as people; hidden certification still requires its separate human-independence policy. A
namespace-first context evidence schema omitted from S01 was added in corrective commit `aa938c8` before fixture work.

**Verification:** All twelve source fixtures pass exact request/evidence/logical schemas, context manifest/claim semantics,
origin allowlists/minimality review, current-core topology, canonical validation, structural checks, deterministic round
trip, PyGraphviz layout, and SVG render. Independent reviewers accepted all sets after four Activity origin-minimality
corrections. The 12-card real-browser gallery shows every card valid/structurally clean and zero console errors. Six
manifest loaders, tamper/leakage/sign-off tests and 111 focused fixture/generation/gallery tests pass. The implementation
audit found no implementation defect; all 733 backend tests passed (4 skipped) and `git diff --check` is clean.

**Removal:** Immediately before deletion, the exact twelve-path candidate list was matched against the specifically
approved record at `docs/research/generation-redesign/migration-plan-approval.json`. Exactly those directories were
removed; all `examples/eval/` and unlisted blueprint/user paths remain untouched.

**Follow-up:** Slice 05 consumes the immutable set loader in deterministic pre-layout generation/repair; Slice 07 repeats
all twelve through the final PyGraphviz engine and records reviewed parity deltas.
