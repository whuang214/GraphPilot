# Slice 04: Integration Audit Cleanup

## Purpose

Remove stale internal obstacle-routing surface and wording found by the final cross-slice audit so the simplified implementation, fixtures, and canonical mapping design describe one model.

## Background

Slices 01–03 are implemented and verified. Their integration audit found no runtime blocker, but the shared route fixture/result shape still carried ignored `obstacles`/`blocked` fields and the mapping design still described retired fan-out/corridor behavior.

## Included Work

- Remove ignored obstacle parameters and always-false blocked results from the private frontend/backend route resolver signatures.
- Simplify shared route fixtures, the frontend fixture type, and backend/frontend parity assertions to the active minimal route result shape.
- Update all resolver signatures and call sites without changing canonical `edge.route` JSON.
- Preserve the browser proof that unrelated nodes do not affect automatic paths while renaming its fixture node for clarity.
- Replace stale fan-out/corridor wording in the canonical mapping design.
- Rename the browser fixture node from Obstacle to Unrelated while preserving the unrelated-node routing assertion.
- Re-run route-focused and full repository gates, then audit the resulting diff.

## Not In Scope

- Canonical route schema changes.
- Removing the intentionally retained WorkspaceBrowser module or public list API.
- Routing behavior, boundary interaction, source-session behavior, or semantic-catalog changes.
- New product functionality.

## Target Areas

- `frontend/src/editor/lib/edgeRouting.ts` and tests.
- `frontend/src/editor/canvas/FloatingEdge.tsx`.
- `backend/services/diagrams/rendering/diagram_render_service.py` and render tests.
- `backend/tests/edge_routing_fixtures.json`.
- `frontend/e2e/smoke.spec.ts`.
- `docs/02-design-and-features/01-diagram-json-mapping-design.md`.

## Exit Criteria

- No active routing function, fixture, or test carries ignored obstacle inputs or blocked outputs.
- Canvas/SVG route fixtures still match exactly.
- The unrelated-node browser proof remains explicit and green.
- Canonical mapping documentation states the active direct/minimal/manual routing behavior.
- The implementation audit finds no material regression or scope drift.
- Full frontend and backend gates pass.

## Previous Slice

- [`03-landing-and-source.md`](03-landing-and-source.md)

## Next Slice

- End of Epic 2's `06-editor-simplification/` group.

## Outcome

**Completed.** The private frontend/backend route resolver now accepts only source, target, and optional authored geometry; the ignored obstacle parameter and always-false blocked result are removed. Shared fixture types/data and parity assertions use that same minimal result shape, while canonical `edge.route` JSON remains unchanged.

**Documentation and proof.** The canonical mapping design now states direct aligned/minimal non-aligned/manual behavior with unrelated nodes ignored. The browser parity fixture names its intervening node `Unrelated` and still proves the canvas and SVG choose the same direct path.

**Audits.** The pre-implementation plan audit approved the bounded cleanup after adding explicit fixture-type, signature/call-site, and browser-proof coverage. The post-implementation audit found no blockers, stale active wording, call-site drift, schema change, or unrelated scope.

**Verification.** `cd frontend; npm run verify` passes lint, production build/typecheck, 400 unit tests, and 27 Playwright tests. `cd backend; uv run python manage.py test` passes 617 tests (3 skipped). `git diff --check` is clean.
