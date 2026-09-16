# Slice 08: PyGraphviz Cutover

## Purpose

Make pinned PyGraphviz 2.0 the sole generation layout engine and remove the subprocess Graphviz/Grandalf implementation,
fallback behavior, dependency, configuration, setup guidance, and tests only after the Slice 7 parity proof and the
specific destructive-removal gate pass.

## Background

Slice 7 adds `PyGraphvizLayoutEngine` without changing production behavior and establishes the immediately prior
verified parity commit. This slice is deliberately separate because old-engine removal is destructive and changes
runtime failure behavior: a missing/broken PyGraphviz runtime must fail explicitly rather than select a geometrically
different algorithm. Rendering remains coordinate-driven and is not part of the engine removal.

## Design

The final layout path is one algorithm and one external identity:

```text
pygraphviz==2.0
→ PyGraphvizLayoutEngine
→ bundled libgvc dot
→ engine identity pygraphviz-dot
```

There is no runtime selector and no fallback. `DiagramLayoutService` always constructs/uses the PyGraphviz engine while
retaining sizing, per-type direction/spacing, containment, and relative-child ownership. Import/wheel/plugin failure
returns non-retryable `layout_engine_unavailable`; native failure or malformed, missing, or nonfinite native output
returns non-retryable `layout_failed`. Errors expose bounded safe details without raw native stack traces or local
library paths. No subprocess `dot`, Grandalf, source build, or alternate Graphviz program is attempted.

The destructive gate is ordered and cannot be collapsed:

```text
Slice 7 implementation committed
→ every native/geometry/concurrency/fixture/canvas-SVG parity gate reviewed and passing
→ exact supported platform/wheel identity recorded
→ specific user confirmation for the enumerated removal set recorded
→ one coherent PyGraphviz-only implementation/removal diff
→ repeat all parity plus full backend/frontend gates
→ commit atomically
```

The enumerated tracked removal set is `GraphvizLayoutEngine`, `GrandalfLayoutEngine`, `resolve_dot_path`, subprocess
`dot -Tplain` construction/parsing/tests, `GRAPHVIZ_DOT_PATH` settings/example/docs, portable `backend/.graphviz/` setup
guidance, the `grandalf` dependency/imports/tests, and silent fallback logic. An existing gitignored/user-owned local
`backend/.graphviz/` installation is not silently deleted; it becomes unused and is reported for optional owner cleanup.
`drawsvg` rendering remains in place.

Rollback is one ordinary revert of the complete Slice 8 implementation commit to the exact verified Slice 7 parity
commit. It restores old engines, dependency/config/docs/tests, selection order, and failure behavior together; no
partial engine reintroduction, compatibility flag, history rewrite, or local-artifact mutation is permitted.

## Plan Audit

- **Entry gate:** require the completed Slice 7 implementation commit and recorded passing malformed/nonfinite/
  close-on-error, repeatability, 256-node, ten-thread, spacing/no-overlap, containment, parallel-edge, fixture-gallery,
  supported-wheel, and canvas/SVG parity evidence. A plan-only or partially passing proof cannot authorize removal.
- **Destructive confirmation:** pause before deletion and record specific user confirmation (or an existing explicit
  approval naming this exact removal set) after parity evidence is available. Generic implementation permission does
  not waive this gate.
- **Sole-engine invariant:** select only `PyGraphvizLayoutEngine` with exact `pygraphviz==2.0`; add no environment
  selector, source-build path, subprocess/Grandalf fallback, or catch-all behavior that changes algorithms.
- **Failure contract:** distinguish unavailable import/wheel/plugin from failed/malformed native layout, map them to
  `layout_engine_unavailable`/`layout_failed`, redact unsafe native/path detail, and prove no secondary engine call.
- **Removal completeness:** before editing, inventory every active code/test/config/doc reference to
  `GraphvizLayoutEngine`, `GrandalfLayoutEngine`, `resolve_dot_path`, `GRAPHVIZ_DOT_PATH`, `dot -Tplain`, portable
  `.graphviz`, `grandalf`, and fallback selection. Remove/update the resulting exact list—code, imports, dependency,
  settings, `.env.example`, setup guidance, implementation-specific tests, and active-doc claims—together. Stale searches
  may allow historical research/archive and this explicit migration record only.
- **Local-file safety:** remove tracked setup/configuration support, not user-owned gitignored Graphviz binaries or any
  existing canonical diagram/trace/debug artifact. No automatic file migration or cleanup is introduced.
- **Parity preservation:** rerun every Slice 7 gate against the sole-engine path and retain exact coordinate,
  containment, parallel-edge, trace identity, platform, canvas, and SVG behavior.
- **Rendering boundary:** do not remove or replace `drawsvg`, saved-coordinate rendering, frontend node rendering, or
  connector routes; touch them only for parity verification if a proven defect appears.
- **Reversibility:** record the exact Slice 7 commit as rollback target and keep Slice 8 in one coherent implementation
  commit so an ordinary revert restores the entire prior behavior without aliases or partial configuration.
- **Verification:** run focused layout/stale-symbol/config/dependency checks and complete offline backend/frontend gates.
  No live provider call, hidden evaluation, push, or production-promotion claim belongs here.

Plan audit result: **Pass after correction.** The audit confirmed Slice 07 parity as a hard gate, existing explicit user removal approval, sole-engine/no-fallback failures, user-local-file safety, complete old-reference inventory, repeated parity/full gates, and one atomic ordinary-revert boundary.

## Included Work

- Change `DiagramLayoutService` to use `PyGraphvizLayoutEngine` as its only engine.
- Retain the exact `pygraphviz==2.0` pin, full native lifecycle lock, coordinate conversion, containment ownership, and
  `pygraphviz-dot` trace identity proven by Slice 7.
- Return typed `layout_engine_unavailable` or `layout_failed` with bounded safe details and no fallback attempt.
- After the destructive gate, remove subprocess `GraphvizLayoutEngine`, `GrandalfLayoutEngine`, `resolve_dot_path`, DOT
  serialization/plain-output parsing, fallback selection, and old imports.
- Remove `grandalf` from dependencies and delete its implementation-specific tests.
- Remove `GRAPHVIZ_DOT_PATH` from settings and `.env.example`, portable `.graphviz`/system/custom-dot setup guidance,
  old test assumptions, and all active documentation claiming Graphviz is optional or Grandalf is a fallback.
- Preserve user-owned local `.graphviz` contents, all canonical diagrams/artifacts, `drawsvg`, and saved-coordinate
  rendering.
- Rerun and record the complete Slice 7 native, geometry, scale, concurrency, fixture, supported-platform, and canvas/
  SVG parity matrix against the sole-engine path.
- Update active generation/environment/testing/backend/dependency owners and this slice outcome atomically with the
  implementation/removal.

## Not In Scope

- Changing the PyGraphviz version, native lock, coordinate formula, graph direction, spacing, sizing, or containment
  contract accepted in Slice 7 except to fix an evidence-backed parity defect before cutover.
- Retaining an old engine behind a feature flag, `GRAPHPILOT_LAYOUT_ENGINE`, compatibility alias, or emergency fallback.
- Deleting user-owned/gitignored `backend/.graphviz/` binaries or rewriting existing diagrams/trace/debug artifacts.
- Removing `drawsvg`, changing SVG/PNG rendering, or redesigning frontend connectors/nodes.
- New orientation features, ports/pins, Graphviz spline persistence, or cross-process native support.
- Public MCP/schema cutover, evaluation framework work, live Azure calls, hidden gold, or production promotion.

## Target Areas

- `backend/services/generation/pipeline/diagram_layout_service.py` and the Slice 7 PyGraphviz engine module, if separate
- `backend/services/generation/pipeline/generation_pipeline.py`
- `backend/graphpilot/settings.py`
- `backend/.env.example`
- `requirements.txt`
- `backend/tests/generation/test_layout_service.py`
- `backend/tests/generation/test_samples.py` and fixture/gallery parity tests
- `backend/tests/api/test_render_example_gallery.py`
- active code/tests/docs containing `GraphvizLayoutEngine`, `GrandalfLayoutEngine`, `resolve_dot_path`,
  `GRAPHVIZ_DOT_PATH`, portable `.graphviz`, `grandalf`, or fallback claims
- `backend/services/diagrams/rendering/diagram_render_service.py` and frontend canvas/SVG verification surfaces, without renderer
  redesign
- active generation design, backend architecture, development environment, testing strategy, dependency/setup docs,
  and decision owner under `docs/`
- this slice document

## Exit Criteria

- The exact Slice 7 parity implementation commit and all required parity/platform evidence are recorded before removal.
- Specific confirmation for the enumerated destructive removal set is recorded before tracked deletions begin.
- `pygraphviz==2.0` is the only layout dependency/engine; every production/example/fixture path reports
  `pygraphviz-dot` and uses the proven full-lifecycle native lock and coordinate conversion.
- Missing import/wheel/plugin returns `layout_engine_unavailable`; native/malformed/missing/nonfinite output returns
  `layout_failed`; both are bounded, non-retryable, and make zero calls to another algorithm.
- Subprocess Graphviz, Grandalf, `resolve_dot_path`, `GRAPHVIZ_DOT_PATH`, portable setup, old parser/fallback tests, and
  `grandalf` dependency/imports are absent from active code/config/tests/docs.
- No `GRAPHPILOT_LAYOUT_ENGINE`, source-build fallback, alias, dual engine, or silent catch-and-switch path exists.
- Existing user-owned `.graphviz` contents and all canonical/trace/debug artifacts are untouched; `drawsvg` and saved-
  coordinate rendering remain present.
- Every Slice 7 native safety, coordinate, repeatability, 256-node, ten-thread, gap/no-overlap, containment, parallel-
  edge, fixture-gallery, supported-platform, and canvas/SVG parity gate passes on the sole engine.
- Focused layout/failure tests, stale symbol/config/dependency/doc searches, and the required PowerShell verification
  pass:

  ```powershell
  cd backend
  uv run python manage.py test
  cd ..\frontend
  npm run verify
  cd ..
  git diff --check
  ```

- Plan and implementation audits have no unresolved findings; the exact prior parity commit and one-command ordinary
  revert procedure are recorded in the completed outcome.

## Previous Slice

[`07-pygraphviz-parity.md`](07-pygraphviz-parity.md)

## Next Slice

[`09-atomic-public-cutover.md`](09-atomic-public-cutover.md)

## Outcome

**Completion:** Cut over `DiagramLayoutService` to the sole pinned `PyGraphvizLayoutEngine` and removed the complete
tracked legacy layout runtime: old engine classes, executable resolution/serialization/parser path, alternate dependency,
fallback/selection logic, environment setting, example/config/setup guidance, implementation-specific tests, and stale
active-owner claims. Alternate engine injection now fails, availability is probed once, and no secondary algorithm can
run. Direct and context generation preserve exact non-retryable `layout_engine_unavailable` versus `layout_failed`
operation identities with bounded `engine`/`stage` details and no raw native/path data.

**Destructive gate and safety:** Entry parity commit `2c17cf3` was the immediate verified rollback boundary. The approved
removal record is `docs/research/generation-redesign/migration-plan-approval.json` amendment at
`2026-07-17T23:29:45Z`. Runtime/code/config/dependency inventory was rechecked before removal. No user diagram, trace,
debug artifact, `.env`, or gitignored/user-owned local Graphviz file was deleted or rewritten; the legacy local directory
remains ignored and unused. Rollback is the ordinary one-commit revert of this Slice 08 implementation back to
`2c17cf3`.

**Verification:** Added stale-symbol/dependency/config/no-selector/local-file-safety tests and sole-engine availability,
alternate-injection, no-secondary-call, public direct mapping, and context mapping tests. The parity suite still covers
exact native lifecycle locking/cleanup, malformed/nonfinite coordinates, repeatability, parallel edges, 256 nodes,
ten-thread stress, all twelve strict candidates, all 48 curated diagrams, containment, canonical validation, and SVG.
Focused cutover tests passed 144 cases. The complete backend suite passed 807 tests (4 skipped). Frontend `npm run verify`
passed lint, build, 406 Vitest tests, and all 40 Playwright canvas/SVG flows. Environment inspection showed only
`pygraphviz 2.0`; the removed dependency was not installed. Python compilation and `git diff --check` passed.

**Deviations:** Completed historical delivery outcomes retain their original facts under explicit historical notices;
research and this migration record retain removal terminology for auditability. Rendering, connector routing, canonical
artifacts, layout configuration, coordinate conversion, platform policy, and PyGraphviz parity geometry were unchanged.

**Follow-up:** Slice 09 consumes this sole typed layout path in the atomic public generation cutover.
