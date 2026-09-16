# Frontend Architecture

> **Design authority:** This document defines the intended frontend architecture. Runtime delivery status belongs
> only to [`epics/00-current-state.md`](../05-delivery/01-current-state.md).

## 1. Purpose

This document owns the React frontend architecture and the practical behavior of the visual editor. The editor's **UI design** — look/feel, layout, interaction model, and the bounded, draw.io-like north star — is defined in `docs/03-design/06-editor-ui.md`.

## 2. Frontend Responsibilities

The frontend is responsible for:

- loading saved diagram JSON from the backend
- adapting GraphPilot JSON to React Flow state
- providing manual visual editing (move, resize, relabel, recolor, connect, add from palette, undo/redo)
- adapting React Flow state back to GraphPilot JSON before save
- saving through Django API routes (or, for picker-opened files, through a File System Access handle)
- showing validation and save errors
- requesting server-side render through Django API routes for the preview comparison and for SVG/PNG export

The browser is a canonical-diagram editor rather than a context-authoring client. It preserves optional diagram
trace/provenance, maintains schema/type/runtime-guard parity, uses canonical `.graphpilot/diagrams/` paths, and
remains compatible with diagrams that have no provenance. Draft authoring is not a
browser action: a draft is written by a host that has read the source and can cite it.
added to the product contract.

## 3. Frontend Runtime

Stack: React 19 + `@xyflow/react` 12 (React Flow), built with Vite 8 and TypeScript ~6, styled with Tailwind v4 (the `@tailwindcss/vite` plugin; design tokens live in `src/index.css` and dark mode is a `.dark` class on `<html>`).

Source under `src/` is organized by role — `adapters/`, `api/`, `types/`, `ui/`, and the editor surface in `editor/`, itself grouped into `components/`, `canvas/`, `shell/`, `lib/`, and `hooks/` (per-file index in `frontend/src/editor/README.md`). Cross-folder imports use a `@/` path alias (`@` → `src/`), configured in `tsconfig.app.json`, `vite.config.ts`, and `vitest.config.ts`.

For local development:

- the React dev server runs at `http://localhost:5173`
- a valid editor URL may use a `diagramPath` query parameter; without one the standalone landing page is shown
- there is no routing library: the app reads `?diagramPath=` from `window.location`, keeps direct IDE opens in sync with `history.replaceState`, and renders landing/editor states from the same composition root
- the frontend never calls MCP directly
- the frontend talks only to Django API routes (the API base URL defaults to `http://localhost:8000`, overridable via `VITE_API_BASE_URL`)

## 4. Editor Route

The editor route uses a raw diagram path:

```text
/editor?diagramPath=/path/to/workspace/.graphpilot/diagrams/order-approval.gp.json
```

A valid `diagramPath` is passed to Django for path-owned load/save and opens directly from an IDE link. Without one, the standalone landing page offers a searchable descriptor-driven New Diagram chooser, Open file, file drop, reopenable Recents, and Clear recents; it does not infer or browse a project.

The editor keeps one internal source-session model with four persistence states:

1. **Path-owned** — an absolute backend path opened by IDE URL or a reopenable recent. Django owns load/save, render-on-save, opaque revision checks, and focus refresh.
2. **External writable** — a picker-opened File System Access handle owns Save after path-free backend validation.
3. **Read-only** — a dropped file has no writable handle and requires Save As.
4. **Unsaved blank** — a centralized diagram-type descriptor supplies chooser presentation and default name, then the client factory creates valid Activity, Use Case, BDD, or Custom canonical JSON with no persistence owner; first Save always delegates to Save As.

Path-owned sessions recheck their opaque backend revision and external writable handles re-read their content revision on focus/visibility: a clean changed session reloads, while a dirty changed session presents Review/Reload/Keep editing. Expected-revision path saves and pre-write external-handle checks reject stale overwrite until explicit resolution. Browser security still prevents deriving an arbitrary picker path or promising a picked handle survives restart.

There is no raw-path field, workspace browser, or persistent source chip. The transport-neutral header exposes available filename/path, write state, unsaved/revision state, and copy path only through one information popover. Persistent Recents contain only paths GraphPilot can reopen; clearing them never deletes files. Opening guards against losing unsaved edits, rejects malformed boundary payloads before React Flow sees them, and ignores stale responses when documents switch quickly.

## 5. React Flow Adapter

GraphPilot JSON is the canonical saved format. React Flow state is derived editor state.

```mermaid
flowchart LR
    A[Saved GraphPilot JSON] --> B[Frontend adapter]
    B --> C[React Flow nodes and edges]
    C --> D[User edits in visual editor]
    D --> E[Reverse adapter]
    E --> F[Updated GraphPilot JSON]
```

Adapter rules:

- GraphPilot JSON is canonical
- React Flow state is derived and should be rebuilt from the saved diagram
- GraphPilot edge `source` and `target` map directly to React Flow `source` and `target`
- GraphPilot `position` and `size` map to React Flow layout state
- the forward adapter passes the real GraphPilot `node.type`, full canonical `node.data`, visual style as runtime `data.gpStyle`, and `parentId`; `gpNode` resolves the core or retained compatibility `semanticType`, while BDD Block `stereotype` supplies its primary heading
- core `parentId` editing owns use cases inside a displayed System Boundary; retained legacy/custom ownership still round-trips without being offered as new core authoring
- visual node style travels in `data.gpStyle` (drawn by the custom renderer and edited by the property panel), not the React Flow wrapper `style`, which carries only sizing; the reverse adapter reads visual style back from `data.gpStyle`
- edge markers, line style, keyword/guard labels, association-end adornments, and item-flow labels are derived from exact relationship identities plus structured edge data; they are never persisted as React Flow marker fields
- optional canonical `edge.route` stores per-edge `orthogonal`/`straight` mode, authored source/target boundary anchors, orthogonal-only waypoints, and central-label offset; missing mode remains orthogonal, calculated paths remain runtime-only, and primitive-aware projection keeps canvas/SVG attachment parity
- the reverse adapter whitelists every canonical structured node/edge data field explicitly, so React Flow runtime/session state (`selected`, `dragging`, `measured`, `positionAbsolute`, marker fields, measured sizes, calculated routes, …) never leaks into saved JSON

## 6. Editor Capabilities

Core element editing:

- moving, resizing, relabeling, recoloring, connecting, and reconnecting elements
- predictable per-edge straight or manual-first orthogonal connectors: straight primitive-boundary segments; zero-bend aligned/minimal non-aligned orthogonal routes independent of unrelated nodes; reusable primitive-aligned anchors (including overlapping diamond slopes/cardinal targets, visible control circles, the use-case ellipse, and the Actor figure envelope); valid-target guidance, overridable visual-cardinal aim-lock, preserved parallel edges, movable anchors/labels, orthogonal segment/corner editing, and no node-movement waypoint inference
- selecting only the loaded diagram type's core authoring identities; BDD primary stereotype suggestions/custom text vary one Block shape without adding node types
- a fixed Content/Appearance/Advanced inspector with compact one-row-at-a-time structured editors, validation-targeted/status-marked tabs, content-fit BDD sizing, and copyable identifiers
- editing structured node data: BDD primary/applied stereotypes, core properties, operations, receptions, constraints, literals, extension points, definition details, join specs, and metadata
- editing structured edge data: roles, multiplicity, navigability, qualifiers, use-case extension data, activity guards/weights, metadata, applied stereotypes, and permitted arrow overrides
- adding nodes from bounded Diagram/Notation shape groups and choosing relationships plus Straight/Orthogonal mode from one connector tray; selected-edge tray actions reuse inspector updates, and All authorable still excludes compatibility-only identities
- System Boundary/use-case containment plus compatibility round-trip for retained legacy owners; display-only canvas tiers keep containers below edges and ordinary nodes, raise only selected ordinary nodes, and never persist `zIndex` or change `parentId` without an explicit node-drag gesture
- saving changes

Supporting editor capabilities:

- undo/redo (`useUndoRedo`, up to 50 snapshots, including React Flow keyboard deletion) and opt-in autosave (toggled via a `gp.autosave` localStorage flag); a failed autosave waits for the next edit rather than retrying in a loop
- dark mode (`shell/useColorMode`, toggling the `.dark` class) and a clearable persistent list containing only reopenable path-owned recents
- canvas affordances: MiniMap, a 16px visual grid with neighbour alignment guides computed in absolute canvas coordinates across parented/top-level nodes (positions are not grid-snapped), and a live zoom %
- a standalone landing page for blank/open/drop/recent entry; project/workspace listing is not part of the frontend
- a render preview (`PreviewMenu`): the server-rendered SVG plus a JSON diff of what a save would write versus the last successful save; closing an in-flight preview invalidates its pending response
- SVG/PNG export (`ExportMenu` + `exportImage.ts`), server-rendered via `POST /api/diagrams/render`
- open-any-file plus Save / Save As via the File System Access API (`fileSystem.ts`) on Chromium

Adding a node stamps the real `node.type` + core `data.semanticType` onto the new React Flow node; BDD Blocks may add an optional primary `data.stereotype`. New edges carry the selected core relationship identity, except any edge incident to a Note is inferred as `commentLink`. This confirms the **React Flow → GraphPilot** direction works for canvas-created elements and type-first blank diagrams, not just for re-saving a loaded document. Blank diagrams allocate no backend file and Save As through the existing validated external-file path before ordinary Save is available.

The palette is driven by `frontend/src/editor/lib/elementCatalog.ts`, a typed presentation mirror of the backend catalog, but it exposes only authorable core/custom entries. Retained specialist entries may still resolve for loaded compatibility documents without appearing in palettes, All authorable, or semantic selectors. Per-type and Custom relationship tools come from the bounded catalog; BDD choices are Association, Composition, Generalization, Dependency, and Comment Link, with part-to-whole Composition and atomic Swap ends.

## 7. State Management

The editor tracks this state.

| State area | Purpose |
| --- | --- |
| Loaded diagram JSON | Canonical data from the backend (or an opened file) |
| React Flow nodes and edges | Derived editor state |
| Selected element | Current node or edge being edited |
| Dirty state | Tracks unsaved changes (drives the `beforeunload` guard) |
| Undo/redo history | Snapshot stack (up to 50) for undo/redo |
| Diagram session source | Path + revision, external writable handle, read-only drop, or unsaved blank; persistence and refresh capabilities derive from this internal owner while the header stays transport-neutral |
| Color mode | Light/dark preference |
| Validation and save state | Tracks save progress and validation results |
| Error state | Tracks load, save, validation, and render errors |

## 8. Save Flow

The save flow is:

1. the user edits the diagram in the visual editor
2. the user clicks Save (a manual save shows an overwrite confirm first; autosave is implicit consent, so it skips the confirm and debounce-saves)
3. the UI converts React Flow state back to canonical GraphPilot JSON
4. the UI persists through the active session owner:
   - **path-owned source** — `POST /api/diagrams/save` with the loaded `expectedRevision`; the backend rejects stale overwrite, validates, atomically writes, and refreshes the sibling SVG (best-effort)
   - **external writable source** — `POST /api/diagrams/validate`, then the browser writes the normalized JSON through its File System Access handle (`Save As` adopts a new external handle)
   - **read-only or unsaved source** — Save delegates to Save As
5. the UI adopts the normalized saved diagram returned by the save/validate boundary, resets the JSON-diff
   baseline, and shows success or validation errors; if save succeeded but SVG refresh failed, it preserves the
   saved state and presents the returned `warning: OperationProblem` without retrying the save

The backend never writes outside the `.graphpilot` workspace it derives from the path. For path-based diagrams the backend owns the write; for picker-opened local files the browser performs the write itself through a user-granted File System Access handle, after the backend has validated the JSON.

## 9. Catalog-Driven Node/Edge Rendering

The editor uses one persisted React Flow node family, `gpNode`. `customNodes.tsx` resolves core or retained compatibility `data.semanticType` through the shared catalog and selects a reusable primitive.

- Activity core primitives cover Initial, Action, Decision, Merge, Fork, Join, Activity Final, and Note.
- Use-case core primitives cover Actor, Use Case with extension points, System Boundary, and Note.
- BDD core primitives cover one Block with primary `stereotype` heading and compartments derived from `data.features`, plus Note.
- Note rendering includes both the clipped top-right outer diagonal and inner dog-ear crease on canvas and SVG.
- Narrow primitive-aware connection strips start/finish relationships at exact normalized perimeter anchors; node interiors remain draggable/selectable, existing endpoints remain movable, and focusable handles preserve assistive identification.
- The forward adapter derives edge notation from core relationship semantics. Include/extend/dependency are dashed open arrows; generalization uses a hollow triangle; composition uses a target filled diamond; comment links have no arrowhead.
- Core `parentId` represents displayed System Boundary containment. Parent-before-child ordering and retained legacy ownership remain preserved for React Flow.

The reverse adapter restores node visual style from `data.gpStyle`, preserves structured semantic fields, and excludes markers and all other React Flow runtime/session fields from canonical JSON.

## 10. Error States

The API client parses every non-2xx handled backend failure as `{ "error": OperationProblem }`, branches on its
stable `code`, displays its safe `message`, and reads only the registered code-specific `details`. Client-only
network/timeout failures are normalized into the same UI error state but are not fabricated backend responses.
Validation/reporting results with `valid: false` remain successful domain responses.

The frontend handles these error states clearly:

- explicit standalone landing state when `diagramPath` is absent
- load failure (including network/timeout when the backend is unreachable)
- invalid JSON returned or loaded
- validation failure on save (blocking issues are surfaced to the user)
- save failure
- render failure for the preview and SVG/PNG export flows
- unexpected React render failure (app-level recovery screen with reload/home actions)
