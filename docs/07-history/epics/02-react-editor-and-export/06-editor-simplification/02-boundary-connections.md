# Slice 02: Boundary Connections

## Purpose

Let users create and reposition relationships at the intended visible boundary position instead of being limited to four side-center creation points.

## Design

- Hovering a narrow boundary hit area shows a temporary connection indicator at the resolved visible perimeter point.
- Dragging from the boundary starts a connection; dropping on another boundary records both exact normalized anchors.
- The node interior remains reserved for selection and movement, and resize controls retain priority.
- Rectangles/bars use their box perimeter and circles/ellipses/diamonds project onto their visible outline; open or compound glyphs use their owned node boundary rather than a generic center point.
- Existing edge endpoints remain draggable around the complete perimeter.
- The canonical route contract continues storing only side/offset anchors; primitive-aware frontend/backend projection keeps canvas and SVG in parity.
- Boundary strips remain focusable and labelled for assistive discovery.

## Included Work

- Add reusable boundary hit-testing, anchor projection, and hover-indicator behavior.
- Integrate boundary gestures with React Flow connection start/end and exact anchor persistence.
- Preserve source/target semantics, default relationship creation, reconnect identity, undo/redo, and route resets.
- Add shape-family unit tests, adapter round-trip coverage, backend render parity, and browser interaction tests.
- Update canonical editor/architecture/rendering documentation.

## Not In Scope

- Semantic relationship presets or catalog changes.
- Connecting from the node interior.
- Curved boundary-following edges or freehand paths.
- New persisted connection-mode fields.

## Target Areas

- `frontend/src/editor/canvas/customNodes.tsx` and focused canvas tests.
- Boundary/anchor helpers under `frontend/src/editor/lib/`.
- `frontend/src/editor/EditorPage.tsx` connection lifecycle.
- `frontend/src/editor/canvas/FloatingEdge.tsx` endpoint editing.
- `frontend/src/adapters/reactFlow.ts` round-trip tests.
- `backend/services/diagrams/rendering/diagram_render_service.py` shape-aware anchor projection.
- Frontend E2E connection/reload/export coverage.

## Exit Criteria

- New relationships can start and end along the complete resolved boundary of every supported primitive.
- Hover indication is discoverable without blocking node selection, movement, resize, or inline editing.
- Exact source/target anchors persist through save/reload and do not alter semantic direction.
- Fork/join bars support distinct connection positions along their visible length.
- Boundary strips expose focusable, labelled source/target affordances without obscuring pointer interaction.
- Canvas and SVG attachment points and marker approaches remain equivalent.
- Relevant frontend/backend checks and browser coverage pass.

## Previous Slice

- [`01-minimal-edge-routing.md`](01-minimal-edge-routing.md)

## Next Slice

- [`03-landing-and-source.md`](03-landing-and-source.md)

## Outcome

**Completed.** Every node side is now a narrow source/target connection strip rather than a center dot. Pointer start/end positions are converted to exact normalized route anchors, new edges persist those anchors without legacy `sourceHandle`/`targetHandle`, and reconnecting a changed endpoint preserves the fixed end while replacing the moved handle with a route anchor. Hover shows a projected boundary indicator, while node interiors remain draggable and route endpoint controls use the same boundary calculation.

**Parity.** Rectangular/bar families use their complete box perimeter; circle/ellipse and diamond families project encoded anchors onto their visible outline in both canvas and SVG. Diamond source/target handles use four clipped diagonal hit bands, so hover and drag follow every sloped edge while the center remains available for selection/movement. Open/compound glyphs use their owned node boundary. Unmeasured just-created nodes fall back to catalog default dimensions before anchor calculation. The route schema is unchanged.

**Primitive-boundary corrections.** Diamond source/target handles use four clipped diagonal hit bands. Initial, Activity Final, Flow Final, Use Case, and Actor use four clipped quarter-ellipse bands and share ellipse projection in canvas/SVG; actor keeps its compound glyph inside that owned interaction envelope. Browser coverage creates relationships from and to every diamond slope, exercises each curved semantic family from a diagonal boundary point, confirms projected indicators, and confirms centers remain available for movement. Focused component and wide/tall projection tests preserve parity. Full-gate totals are recorded in the current-state board.

**Verification.** `cd frontend; npm run verify` passes lint, production build/typecheck, 393 unit tests, and 26 Playwright tests covering creation, persistence, reconnect, interior drag, and manual routes. `cd backend; uv run python manage.py test` passes 617 tests (3 skipped), including primitive anchor projection and all render parity coverage. `git diff --check` is clean.
