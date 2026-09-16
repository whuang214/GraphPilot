# Slice 07: PyGraphviz Parity

## Purpose

Add the final in-process PyGraphviz layout engine behind the existing flat layout seam and prove native safety,
coordinate correctness, deterministic geometry, supported-platform packaging, fixture rendering, and canvas/SVG parity
without switching the production/default engine or removing any current rollback path.

## Background

The existing `DiagramLayoutService` prefers subprocess Graphviz `dot -Tplain` and silently falls back to Grandalf.
The redesign requires one final engine, but removing working engines before the replacement passes native, geometry,
scale, concurrency, fixture, and render proof would create an unsafe cutover. This slice therefore adds and exercises
PyGraphviz in parallel; Slice 8 alone switches the default and removes the old implementation after the parity evidence
and destructive gate are satisfied.

## Design

### Engine and native lifecycle

Pin exactly `pygraphviz==2.0`. `PyGraphvizLayoutEngine` implements the existing flat `LayoutEngine` seam and reports
external identity `pygraphviz-dot`. Every call creates one directed, non-strict `AGraph`, adds safe node tokens and all
source/target pairs, applies exact `rankdir`, `nodesep`, `ranksep`, and fixed box sizes, and invokes
`layout(prog="dot")` through bundled libgvc. `strict=False` preserves parallel edges as separate layout constraints.
GraphPilot persists only semantic endpoints and continues to own connector routes; libgvc spline output is not
canonical.

A module-owned process-local `threading.Lock` covers the complete native object lifecycle:

```text
AGraph creation
→ graph/node/edge attribute mutation
→ layout(prog="dot")
→ node-position and graph-bounding-box reads
→ AGraph.close() in finally
```

Input preparation and final pure-Python normalization stay outside the lock. Every error path closes the native graph.
V1 makes no cross-process serialization claim; multi-process native layout remains unsupported until separately proven.

### Coordinate conversion

PyGraphviz returns Graphviz-point node centers and a graph bounding box with a bottom-left origin. For bounding box
`x0,y0,x1,y1`, node center `cx,cy`, and GraphPilot node `width,height` at the existing 72-points-per-inch convention,
conversion to GraphPilot top-left pixel coordinates is exactly:

```text
graphHeight = y1 - y0
x = cx - x0 - width / 2
y = graphHeight - (cy - y0) - height / 2
```

Every bounding-box and position value must parse and be finite, every input node must have exactly one position, and
the final map is translated so its minimum corner is `(0,0)`. The implementation must not treat PyGraphviz `y` as
top-down or perform a no-op point-to-inch round trip that omits the bounding-box flip.

`DiagramLayoutService._position` remains the sole containment owner: children are laid out as flat TB graphs, offset
below the parent header/padding, parent containers are resized, top-level layout edges are remapped to ancestors, and
child positions remain relative to their parent. PyGraphviz never receives canonical nesting. Ports/pins and connector
routing remain outside this migration.

### Trace, platform, and parity policy

Layout trace/capture may contain only:

```text
engine: pygraphviz-dot
pygraphvizVersion
runtimePlatform: windows-x64 | macos-x64 | macos-arm64 | linux-x64 | linux-aarch64
emulation: null | windows-x64-on-arm64
layoutConfigurationVersion: graphpilot.generation.layout.<type>.v1
nodeCount, edgeCount, durationMs
```

None enters canonical diagram JSON. PyGraphviz 2.0 binary wheels are the supported install path for Windows x64,
macOS x64/ARM64, and Linux x64/AArch64. Windows ARM64 V1 uses the packaged x64 GraphPilot/Python runtime under Windows
emulation and records `windows-x64-on-arm64`; native Windows ARM64 Python and automatic source builds are not fallbacks.

Parity compares structural/geometric invariants and reviewed galleries, not universal one-pixel equality across
Graphviz builds. Activity remains TB with horizontal fork/join bars. The old engine remains the production/default path
for this complete slice; PyGraphviz is selected explicitly only by focused/parity tests and proof tooling.

## Plan Audit

- **Dependencies:** require completed/audited Slices 1–6, especially layout/profile identities, all twelve signed-off
  fixtures, the accepted pre-layout candidate, and trace observer events. Require promoted generation/environment/
  testing owners before implementation.
- **Non-destructive sequencing:** add the dependency/engine/tests only. Do not switch the default, insert PyGraphviz as
  a silent fallback, remove old engines/config/dependencies/docs, or perform the Slice 8 destructive gate here.
- **Native safety:** one process-local module lock must span every libgvc-backed operation and `close()` in `finally`;
  stress/error tests must prove serialization and cleanup rather than relying on the GIL or per-instance locks.
- **Geometry:** implement the exact bottom-left-center/bounding-box to top-left conversion, finite/missing/malformed
  rejection, and `(0,0)` normalization. Keep pixel sizing and containment ownership outside PyGraphviz.
- **Graph semantics:** use a directed non-strict graph, preserve parallel edges, safe-token arbitrary IDs, exact
  per-type direction/gaps, and no semantic/endpoint mutation or canonical spline adoption.
- **Parity evidence:** cover empty/malformed data, repeatability, the 256-node boundary, ten-thread stress, direction,
  gaps/no overlap, containment, parallel edges, every current example, all twelve new fixtures, canonical validation,
  and reviewed canvas/SVG galleries. Record accepted snapshot deltas rather than asserting unjustified cross-build
  coordinate identity.
- **Platform boundary:** verify the exact 2.0 wheel/import/plugin identity for each supported packaged platform and the
  Windows ARM64 emulation policy. Missing wheel/plugin is typed `layout_engine_unavailable`; source build is not an
  automatic recovery path.
- **Observability:** report exact engine/version/platform/emulation/layout-config/count/duration identity through the
  established observer/trace contract and prove canonical JSON remains unchanged.
- **Reversibility:** rollback removes the new engine, parity harness, and `pygraphviz==2.0` pin in one ordinary revert.
  The current default engines remain untouched, so generated canonical diagrams require no migration.
- **Verification:** run focused layout/fixture/gallery/stress tests, full offline backend tests, and full frontend parity
  verification. Provider calls, hidden evaluation, production cutover, and destructive removal are forbidden.

Plan audit result: **Pass.** The audit confirmed the exact 2.0 pin, full native-lifecycle process lock, coordinate formula, directed non-strict graph, platform/emulation boundary, structural/gallery parity, add-only sequencing, and complete non-destructive rollback.

## Included Work

- Add the exact `pygraphviz==2.0` dependency pin and supported-wheel/import/plugin checks.
- Implement `PyGraphvizLayoutEngine` behind `LayoutEngine` with directed non-strict `AGraph`, safe IDs, exact graph
  attributes, `layout(prog="dot")`, and guaranteed close.
- Add the process-local full-native-lifecycle lock and ten-thread serialization/error cleanup proof.
- Implement exact bounding-box/center coordinate conversion, finite/completeness validation, and origin normalization.
- Reuse `DiagramLayoutService` sizing, containment, relative-child, edge-remapping, direction, and spacing ownership.
- Emit bounded PyGraphviz engine/version/platform/emulation/configuration/count/duration observer identity outside the
  canonical diagram.
- Add malformed/nonfinite/missing/empty/parallel-edge/repeatability/scale/gap/no-overlap/containment tests.
- Run every current example and twelve approved training fixtures through accepted candidate → PyGraphviz layout →
  canonical validation → canvas/SVG gallery parity and record reviewed snapshot deltas.
- Update active generation/environment/testing/layout documentation and this slice outcome with proof results while
  retaining old-engine behavior until Slice 8.

## Not In Scope

- Switching the default engine, removing subprocess Graphviz/Grandalf, or deleting any old dependency/configuration/
  test/documentation; Slice 8 owns that gated cutover.
- A `GRAPHPILOT_LAYOUT_ENGINE` selector, silent fallback to PyGraphviz, or source-build fallback.
- Cross-process native serialization or support for native Windows ARM64 Python.
- Layout-driven semantic repair, canonical edge splines, obstacle routing, ports/pins, or renderer redesign.
- Per-diagram LR/TB selection, vertical fork/join bars, mixed local orientations, or new request/logical fields.
- Public MCP/schema cutover, evaluation, live Azure calls, hidden gold, or production promotion.

## Target Areas

- `requirements.txt`
- `backend/services/generation/pipeline/diagram_layout_service.py` or a dedicated engine module behind its existing seam
- `backend/services/diagrams/catalog/constants.py` only where immutable layout configuration identity is assembled
- `backend/services/generation/pipeline/generation_pipeline.py` observer/engine identity plumbing
- `backend/tests/generation/test_layout_service.py`
- `backend/tests/generation/test_samples.py` and the twelve Slice 4 fixture/manifest proof surfaces
- `backend/tests/api/test_render_example_gallery.py`
- `backend/services/diagrams/rendering/diagram_render_service.py` and `frontend/src/editor/canvas/customNodes.tsx` as parity
  verification surfaces, not redesign targets
- frontend parity/unit/E2E tests affected by approved gallery snapshots
- active generation design, development-environment, testing, rendering/parity, and dependency documentation under
  `docs/`
- this slice document

## Exit Criteria

- `requirements.txt` pins exactly `pygraphviz==2.0`, and supported packaged-runtime evidence records wheel/import,
  bundled plugin, PyGraphviz version, platform, and Windows ARM64 emulation behavior where applicable.
- Every layout call uses one directed non-strict graph and a module-owned process-local lock across creation, mutation,
  layout, reads, and `close()`; close-on-success and every error path are proven.
- Coordinate tests assert the exact bounding-box flip equations, arbitrary nonzero `x0/y0`, finite values, missing/
  malformed/nonfinite rejection, node-size offsets, and final minimum `(0,0)` normalization.
- Safe IDs, empty graphs, parallel edges, Activity TB/horizontal bars, per-type direction/gaps, no-overlap, and parent/
  child containment/relative coordinates remain correct.
- Identical input/configuration is repeatable, the 256-node boundary completes, and ten concurrent calls serialize
  native work without corruption, leaks, omissions, or deadlock.
- All current examples and twelve approved fixtures pass strict/canonical validation and reviewed canvas/SVG gallery
  parity; accepted old/new deltas and exact platform/layout identities are recorded.
- Trace/debug observer output reports `pygraphviz-dot` and the approved bounded identity fields; canonical `.gp.json`
  contains none of them.
- The current engine remains production/default, no old code/config/dependency/doc is removed, and no fallback order is
  changed in this slice.
- Focused layout/fixture/gallery/stress tests, dependency/stale checks, and the required PowerShell verification pass:

  ```powershell
  cd backend
  uv run python manage.py test
  cd ..\frontend
  npm run verify
  cd ..
  git diff --check
  ```

- Plan and implementation audits have no unresolved findings, and the Slice 7 implementation commit is recorded as the
  verified non-destructive rollback boundary for Slice 8.

## Previous Slice

[`06-semantic-review-and-diagnostics.md`](06-semantic-review-and-diagnostics.md)

## Next Slice

[`08-pygraphviz-cutover.md`](08-pygraphviz-cutover.md)

## Outcome

**Completion:** Added exact `pygraphviz==2.0` and an explicit `PyGraphvizLayoutEngine` behind the existing flat seam. The
adapter uses a directed non-strict safe-token graph, fixed point-sized boxes, exact per-type rank/gap configuration, the
specified bottom-left-center/bounding-box conversion, finite/completeness checks, origin normalization, and one
process-local lock spanning AGraph construction through attribute mutation, `dot` layout, reads, and `close()` in
`finally`. Added exact wheel/plugin/version and supported-platform/emulation checks, typed unavailability, bounded
thread-local trace identity plus observer events, and an explicit in-memory PyGraphviz gallery option. The current
subprocess-Graphviz/Grandalf selection remains the default and never probes PyGraphviz in this slice.

**Fixture/parity delta:** Re-derived all twelve fixed training `output.gp.json` files through PyGraphviz; source requests,
evidence, strict logical answers, metadata, runtime digests, and all six set digests remained byte-for-byte logically
unchanged, so the accepted delta is geometry-only. The 48-card parity run (12 training + 36 eval; 16 per type) produced
48 valid, structurally clean, rendered SVGs with full vocabulary coverage. A real-browser inspection found 48/48
`pygraphviz-dot` cards, zero error badges, zero structural warnings, and zero console errors. Independent visual review
accepted Activity TB/fork-join, Use Case LR/containment, BDD labels/relationships, clipping/overlap, and canvas-contract
parity.

**Verification:** Focused tests cover malformed/missing/nonfinite geometry, exact coordinate flip, safe arbitrary IDs,
parallel edges, close-on-error, no explicit-engine fallback, default non-selection, repeatability, direction/gaps,
horizontal fork/join bars, containment, all twelve strict candidate assemblies, all 48 curated canonical validation/SVG
renders, the 256-node boundary, and mock plus real ten-thread stress. The backend suite passed 813 tests (4 skipped).
Frontend lint/build and 406 Vitest tests passed after replacing stale legacy fixture globs; the 40 Playwright canvas/SVG
flows were moved to the new PyGraphviz-derived Activity fixture and passed after one route test selected a routable
Action edge. `git diff --check` and Python compilation passed.

**Deviations:** Cross-build parity intentionally records structural/geometry acceptance rather than universal one-pixel
coordinates. Native Windows ARM64 Python and automatic source builds remain unsupported; Windows ARM64 uses the x64
packaged runtime under emulation. No old engine, setting, dependency, documentation path, or user-local `.graphviz`
content was removed.

**Follow-up:** Slice 08 now owns the separately authorized atomic default cutover and complete subprocess/Grandalf/
`GRAPHVIZ_DOT_PATH` removal after rechecking this parity evidence.
