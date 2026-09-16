# Backlog

Consolidated, categorized backlog of deferred, out-of-scope, and potential features gathered from the active documentation set (`docs/00-*` through `docs/03-*`). Items here are not yet scheduled; when one is picked up, promote it into the relevant epic/slice plan and remove it from this list.

This is distinct from `epics/00-current-state.md` (live delivery status) and from `docs/05-delivery/04-decisions.md` (the authoritative tracker for design decisions). Several entries below also appear there as `Deferred` or `Open` rows; this file collects them as feature work rather than restating the decision rationale.

## How to read this

Entries are intentionally short: what the item is, why it is deferred, and a rough area/approach. Everything here is **deferred** (not yet scheduled) unless tagged otherwise; when an item is picked up, promote it into the relevant epic/slice plan and remove it from this list.

Status tags used in the entries below:

- **Delivered** — since shipped; the entry is kept for traceability.
- **Partially delivered** — part shipped, the remainder still deferred.
- **Promoted** — moved into an epic/slice plan (tracked there now; kept here for traceability rather than deleted).

Larger entries marked as a **theme** are fuller planning write-ups (goal / non-goals / phases), not single features.

## Contents

1. [Product direction and distribution](#product-direction-and-distribution)
2. [Editor and UX](#editor-and-ux)
3. [Diagram types and notation](#diagram-types-and-notation)
4. [Schema, storage, and API](#schema-storage-and-api)
5. [Generation, validation, and quality](#generation-validation-and-quality)
6. [Export, import, and interoperability](#export-import-and-interoperability)
7. [MCP tools](#mcp-tools)
8. [Collaboration](#collaboration)
9. [Testing, CI/CD, and delivery tooling](#testing-cicd-and-delivery-tooling)
10. [Notes](#notes)

## Product direction and distribution

### Local internal distribution (theme)

High-level theme, not yet broken into slices. The intended direction is a downloadable, per-machine, fully local-hosted internal app with **no server deployment** — each user runs GraphPilot on their own computer and all diagram data stays local. Target audience is both **technical users** (devs / architects / systems engineers via IDE + MCP, diagrams stored next to code) and **non-technical business users** (BAs / PMs / ops using the app directly without an IDE).

Sub-themes to detail later:

- **Single-process serve** — have Django serve the built React frontend so the app runs as one local process instead of separate dev servers. First step; small architectural change.
- **Installer / launcher** — one internal installer + single "start GraphPilot" entry point so users do not manage multiple terminals. Assumes Python/Node are present.
  - **First step — dev launcher (small, no packaging):** a repo-root launcher (e.g. `run.py` + double-clickable `dev.bat` / `dev.sh` wrappers) that starts `manage.py runserver` (`:8000`) and `npm run dev` (`:5173`) **together**, streams both logs (prefixed), opens `http://localhost:5173`, and stops both on Ctrl+C. Stdlib `subprocess` only — no new dependency; still assumes deps are installed. Can also bootstrap (venv/`migrate`) on first run. The *Single-process serve* item then collapses this to one process/port, and the *Zero-dependency desktop app* removes the install requirement. (Note: the MCP server stays IDE-launched; this launcher is for the browser app.)
- **Zero-dependency desktop app** — package as a double-click app (e.g. Tauri/Electron or a frozen binary) that bundles the runtimes, so non-technical users need no dev tooling installed. Larger effort; supersedes the installer for that audience.
- **In-UI AI generate flow** — let the browser app prompt → generate → edit → export without an IDE, so non-technical users get the AI value (today generation is gated behind MCP/IDE). Relates to the deferred "AI agent inside the UI" item.
- **MCP registration as part of install** — make wiring the local MCP server into the IDE part of the technical-user setup.
- **Internal update / versioning story** — how new versions are distributed and updated across machines (re-run installer, auto-update, or shared share).

> A detailed breakdown of the hosting / distribution / LLM-access options behind this theme lives in `03-deployment-and-distribution-options.md`.

## Editor and UX

### Editor enhancements (Epic 2 area)

- **Undo** — revert the last editing action (move, connect/reconnect, relabel, recolor, resize, delete) in the React Flow editor. **Delivered** (`04-editor-ui-ux`, Slice 04): `useUndoRedo`, a 50-snapshot history stack over `nodes`/`edges`, with Ctrl+Z.
- **Redo** — reapply an undone action. **Delivered** (`04-editor-ui-ux`, Slice 04): shares the undo history stack; Ctrl+Shift+Z.
- **Load diagram from directory** — let the user open a diagram by browsing a workspace `.graphpilot/` directory instead of passing an explicit `?diagramPath=...`. **Delivered** (`04-editor-ui-ux`, Slice 06): the workspace `Browse` dialog backed by the additive `GET /api/diagrams/list`; plus Slice 07's native "Open file…" picker via the File System Access API.
- **Autosave** — automatically persist edits instead of manual save only. **Delivered** (`04-editor-ui-ux`, Slice 05): opt-in, debounced, off by default, persisted.
- **Richer property panel** — expand node/edge editing beyond the limited MVP set. **Delivered** (`04-editor-ui-ux`, Slice 05): grouped Identity/Layout/Style sections, style presets, and a bulk-style mode for multi-selection.
- **Conflict detection** — detect concurrent edits between the editor and IDE updates instead of last-write-wins. Out of MVP. Needs a change/version marker shared by save and `diagram_update`.
- **Router dependency** — adopt `react-router-dom` (or similar) once a second view appears. MVP reads `pathname` + `diagramPath` via `window.location`. Tied to the `diagramPath` → `diagramId` change below.
- **More supported style fields** — grow the small MVP style subset (background, border, color) if richer styling is needed. Frontend + schema/mapping.
- **Faithful browser round-trip test (Playwright E2E)** — Slice 04 confirms the load → edit → save round-trip with a Vitest unit test against *simulated* React Flow output. A Playwright E2E that drives the real editor in a browser and saves through the API would close the residual gap (a runtime field React Flow emits that the unit test did not simulate). **Delivered** (Epic 2's `04-editor-ui-ux` group): a Chromium-only Playwright smoke suite (`frontend/e2e/`, `npm run e2e`) boots both servers and drives the real editor through load → edit → save, dark mode, undo, and the workspace browser. A broader cross-browser matrix remains optional.
- **New diagram from scratch (blank canvas)** — let the user start a brand-new, empty diagram (choosing a diagram type) directly in the browser, without first generating one via MCP/IDE or opening an existing `.gp.json`. Needs a "New diagram" entry point on the landing page, an in-memory empty canonical diagram, and a first Save / Save As to choose a location. The reverse adapter already supports canvas-authored (origin-less) nodes/edges (Epic 2 Slice 06), so this is mostly a new-document + save-new flow. Pairs with the next item and the *Robust editor* Tier A work below.
- **Build a diagram from basic shapes & blocks** — once a blank canvas exists, compose a diagram by dragging the palette's basic shapes/blocks onto it (drag-from-palette already works for editing existing diagrams). Remaining work is the empty-start flow above plus palette coverage for every common-tier shape (e.g. fork/join, value/constraint/enumeration). Relates to the *Robust editor* Tier A items.
- **Node text overflow: wrap / show overflow while editing** — on the React canvas a label longer than its node is currently clipped (`overflow: hidden` on the node box), so text can disappear. Wrap onto the next line and/or surface an overflow affordance (auto-grow the node, scroll, or expand-on-edit) so the label stays legible and fully editable. The SVG export already wraps/shrinks/ellipsizes via `_fit_text`; this brings the canvas to parity. Area: `frontend/src/editor/canvas/customNodes.tsx` + the inline label editor (`LabelInput`).
- **Narrow-window rail policy** — with both persisted rails expanded, a viewport below about 680px can collapse the React Flow pane to zero width and emit renderer warnings; users can recover by collapsing a rail, but the editor needs an explicit responsive policy (automatic collapse, overlays, or a guaranteed minimum canvas) before claiming narrow/mobile support. Found in Epic 2 connector/audit S03; desktop Chromium remains the supported automated target.
- **BDD in-shape feature editing — delivered by the semantic-model correction.** BDD definitions use typed `data.features` for properties/operations/receptions/constraints/literals; canvas and SVG derive their compartments from that source. Part/reference/value/constraint/flow are property kinds rather than standalone classifier boxes.
- **Freeform text element (annotation)** — a lightweight free-text box for annotations, distinct from the `note` sticky shape; the smallest bounded step toward generic shapes (`data.semanticType` already stays an open string, so this is mostly a `text` renderer + palette entry). Could stand in for a generic `part`/box when generic shapes land. The fuller freeform-canvas direction is the **Generic / informal diagrams — Framing B** theme below; keep this bounded entry aligned with that decision.
- **Additional stereotype applications — delivered by the semantic-model correction.** `data.appliedStereotypes[]` carries domain/profile applications without replacing the exact standard `semanticType`; standard BDD keywords remain derived from definition identity.
- **BDD association-end semantics — delivered by the semantic-model correction.** `sourceEnd`/`targetEnd` carry role, type, multiplicity, navigability, aggregation, qualifiers, ordering, uniqueness, and property paths; canvas/SVG derive end labels and exact diamond placement from them.

### Robust editor (draw.io / Lucidchart-style) — theme

> This is a deliberately fuller planning entry (the rest of the backlog is one-liners). It is a **theme**, not a single feature, and it subsumes several short items above: undo/redo, autosave, richer property panel, and more style fields. Treat those as parts of this theme when this work is scheduled.  **Promoted to Epic 2's `04-editor-ui-ux` group (Comprehensive Editor UI + UX)** — now scheduled as `docs/03-development-and-delivery/epics/02-react-editor-and-export/04-editor-ui-ux/` (6 slices: Tailwind design system → app shell → canvas polish → toolbar/interactions → inspector/save UX → workspace browser/export). The Tier A drag-from-palette and Tier C custom-renderer pieces remain promoted to Epic 2 Slices 05–06 (formerly Epic 2.5). Entries here are kept (annotated) for traceability rather than deleted.

#### Goal

Evolve the current display-first editor into a comfortable diagramming surface that *feels* like a lightweight draw.io/Lucidchart for the three MVP diagram types — without becoming a general-purpose drawing tool. GraphPilot JSON stays the source of truth; everything here is additive over the existing load → edit → save flow.

#### Non-goals

- Not a general freeform canvas (no arbitrary shapes/images/text boxes).
- No multi-page/multi-diagram canvases, real-time collaboration, or templates marketplace (collaboration is tracked separately below).
- No new diagram types beyond `activity_diagram`, `use_case_diagram`, `bdd_diagram`.

#### Capability tiers

Tiered so it can ship incrementally; each tier is independently useful.

- **Tier A — usable basics**
  - Node palette/sidebar to **drag in** new nodes (React Flow DnD: palette `onDragStart` → pane `onDrop` → `screenToFlowPosition`).
  - Reverse adapter handles **newly created nodes** (no original entry): the palette stamps `type` + `data.semanticType` onto the React Flow node and the adapter reads them for unknown ids (today it falls back to `type: 'default'` and would drop `semanticType`). **Promoted (basic form) to Epic 2, Slice 06** (formerly Epic 2.5 Slice 02, `epics/02-react-editor-and-export/02-renderers-and-samples/06-canvas-authoring.md`): the reverse-adapter change plus the *minimum* node creation needed to confirm the React Flow → GraphPilot direction is scheduled now to de-risk the architecture. The fuller palette/DnD polish below remains backlog.
  - Inline label editing (double-click), delete affordances, basic copy/paste.
  - Undo/redo (history stack over `nodes`/`edges`).

- **Tier B — quality-of-life**
  - Palette contents driven by backend type profiles (`node_type`, `allowed_node_semantic_types`) instead of hardcoding — likely via the optional `GET /api/diagram-types` / `GET /api/schema` routes.
  - Snapping/alignment guides, multi-select + bulk move/style, zoom-to-fit and zoom controls, a minimap.
  - Autosave (reusing the existing save API) and clearer inline validation feedback (surface save validation issues against the offending node/edge).

- **Tier C — polish (open-ended)**
  - Custom per-type node renderers (start/end ovals, decision diamonds, actors, BDD blocks, etc.) with type-aware connection handles. This is the largest, most design-heavy piece and replaces the current "everything renders as the React Flow `default` node" behavior. **Promoted to Epic 2, Slice 05** (formerly Epic 2.5 Slice 01, `epics/02-react-editor-and-export/02-renderers-and-samples/05-node-shapes.md`): the custom per-type renderers + `parentId` containment are scheduled now so samples can be authored against a faithful preview. Auto-layout / edge routing / theming below remain backlog.
  - Auto-layout, edge routing/orthogonal connectors, theming.

#### Architecture impact (what this touches)

- **Reverse adapter** (`frontend/src/adapters/reactFlow.ts`): currently pulls canonical fields (`type`, `semanticType`, …) from the *originally loaded* diagram by id. Node creation breaks that assumption and requires reading those fields from React Flow state for new ids.
- **Forward adapter / rendering**: forces `type: 'default'` so React Flow renders built-in nodes. Tier C custom renderers change this and must round-trip the real GraphPilot `node.type`.
- **Type/profile source**: the allowed node kinds already exist on the backend type profiles; Tier B exposes them to the frontend.
- **Schema**: stays the canonical contract; richer styling/handles may grow the supported subset (see schema/data-model items above).

#### Dependencies & sequencing

- Node creation changes the reverse-adapter assumptions the sample round-trip validates, so the reverse-adapter + basic-create confirmation is scheduled **before** the comprehensive sample authoring — see Epic 2 Slices 06 (reverse direction) and 08 (sample authoring). Tier C custom renderers are likewise brought forward as Epic 2 Slice 05.
- The remaining tiers (palette/DnD polish, undo/redo, autosave, Tier B/C polish) are large enough to justify their own epic if promoted (e.g. tiers A/B/C as slices) rather than extending the editor piecemeal.

#### Open questions (log in `decision-decisions.md` when scheduled)

- Hardcode the node palette per type, or fetch from the optional API routes?
- How far to take Tier C custom node visuals for an MVP-plus (which semantic types get bespoke shapes vs. a styled default)?
- Do richer styling/handles require schema changes, or stay within the current `additionalProperties` allowances?

### UI / product

- **AI agent inside the UI** — an in-editor assistant. Explicitly out of MVP scope.
- **UI styling / polish** — visual and color polish beyond what is needed to make the editor usable. Out of MVP scope. **Promoted to Epic 2's `04-editor-ui-ux` group** (Comprehensive Editor UI + UX): a Tailwind design system plus app-shell / canvas / inspector polish.

## Diagram types and notation

### Additional diagram types — formal (post-MVP, theme)

> Fuller planning entry (a **theme**, not one feature). The MVP is intentionally three types — `activity_diagram`, `use_case_diagram` (UML, *behavioral*) and `bdd_diagram` (SysML, *structural*). This entry plans which types to add **after** MVP, for two target users: **systems engineers** (aerospace/industrial control systems → MBSE/SysML) and **software engineers** building applications (UML). The "no new diagram types" non-goal under *Robust editor* above is **MVP-scoped**; this is its post-MVP successor. It covers **formal** notations only; generic, informal diagrams (flowcharts, org charts, mind maps) are planned separately in *Generic / informal diagrams (post-MVP)* below.

#### Diagram classes (how new types are organized)

- **Structural** — what the system *is* (things + relationships); UML + SysML. *(have: BDD.)*
- **Behavioral** — what the system *does* (flow, states, interactions); UML + SysML. *(have: Activity, Use Case.)*
- **Requirements** — text requirements + traceability; **SysML only.**
- **Parametrics** — constraints/equations on properties; **SysML only.**

#### Committed / near-term picks

1. **State Machine** — *Behavioral* (UML & SysML). Control modes / fault states (systems) **and** entity/UI lifecycles (software). Reuses the activity flow renderer + top-down layout.
2. **Class / ER (data model)** — *Structural* (UML / ER model). The highest-value artifact for app-building — entities/fields/relationships → schema; relationships carry crow's-foot/UML multiplicity. Reuses the BDD block renderer.
3. **Architecture (C4-based)** — *Structural.* The software system-architecture type — the simple boxes-and-lines "system architecture diagram" people draw informally, but given a small generatable/validatable vocabulary by basing it on the **C4 model** (Simon Brown) rather than a freeform icon canvas. *Likely the third addition ("probably next" per current planning).*
   - **C4 levels (zoom):** System Context (system + people + external systems) → **Container** (apps/services/datastores inside the system) → Component → Code. GraphPilot targets **Context + Container** (Levels 1–2); Component/Code are out of scope.
   - **Vocabulary:** nodes `person`, `softwareSystem` (in-focus), `externalSystem`, `container` (app / service / datastore); a `systemBoundary` groups the in-focus system's containers — **reusing the use-case `parentId` containment** already shipped. Edge: one directed, **labeled** `relationship` (intent + optional protocol/tech).
   - **Build fit:** reuses the BDD block renderer + the use-case boundary containment → **low–med** cost. A freeform icon diagram is explicitly *not* the target (it cannot be generated or scored).

#### Candidate order after those

4. **SysML Requirement** — *Requirements.* Traceability (derive/satisfy/verify); the MBSE / safety-critical differentiator.
5. **SysML IBD** (Internal Block) — *Structural.* Interconnect via ports; complements BDD (needs the deferred BDD `ports`).
6. **Sequence** — *Behavioral (Interaction).* API/control message flows over time; **high cost** — needs a time-axis/lifeline canvas GraphPilot does not have.
7. **Deployment** / **Parametric** — niche; later. (C4's own **Deployment** view maps containers → infrastructure; UML Deployment is the OMG equivalent.)

#### How a type is added (recipe — ties to the example-generation engine)

Per type: (1) author its notation spec in `docs/02-design-and-features/diagram-schemas/<type>-diagram-blueprints.md` (vocab + notation table + edge rules + layout + structure); (2) register the vocab in `backend/services/diagrams/catalog/diagram_types.py` + add the canvas renderer (`customNodes.tsx`) + SVG export (`diagram_render_service.py`) + palette + layout direction; (3) **craft its training + eval examples via the example-generation engine** (Epic 3 Slice 11 — `epics/03-mcp-generation-and-wrappers/03-eval-and-doe/11-answer-key-quality-and-review.md`); (4) wire `prompts.md` + few-shot. Step 3 is the gating capability: a solid example engine turns each new type into a repeatable recipe rather than a from-scratch effort.

### Generic / informal diagrams (post-MVP, theme)

> Fuller planning entry (a **theme**, not one feature). The section above adds **formal system-modeling** notations (UML/SysML/C4). This one is its sibling for **generic, informal diagrams** — plain **flowcharts**, boxes-and-arrows process maps, org charts, mind maps — the "just sketch a diagram, no formal notation" use case, for audiences (BAs, PMs, ops, and any user who does not want a strict methodology) beyond the systems/software engineers the formal types target. It broadens GraphPilot from *system modeling only* to *general diagramming*, so it must be reconciled against the deliberately **bounded, notation-aware** product stance (the editor's *draw.io-like, not freeform* north star — see `decision-decisions.md`).

#### The core tension (why "how hard" has two very different answers)

GraphPilot's differentiator over draw.io is that every type is **generatable, validatable, and scorable**: a constrained vocabulary (`diagram_types.py`), a deterministic structural critic (`services/diagrams/validation/structural_constraints.py`, run by validation Layer 4), and an answer-key-based eval/DOE harness. An "anything goes" diagram fights all three at once — with an open vocabulary the validation vocab checks and structural critic become near-no-ops, and the eval matcher/correctness-completeness metrics have no ground truth to score against. So cost depends entirely on how *bounded* the type is:

- **Framing A — bounded "flowchart" type (recommended): LOW–MEDIUM cost.** Treat a flowchart as a proper new type with a small, sensible vocabulary (`start`/`end`, `process`, `decision`, `subprocess`, `io`, `connector`) and light structural rules (single start, reachability, guarded decision branches). This is the **easiest possible new type** because it is essentially a relabelled `activity_diagram`: it reuses the `activityNode` canvas + SVG shapes, the top-down PyGraphviz layout, and the existing activity structural rules almost verbatim. It follows the "How a type is added" recipe above cleanly and stays fully generatable/scorable.
- **Framing B — truly freeform generic canvas: HIGH cost / product pivot.** Arbitrary shapes, free text, no vocabulary, no structural rules. This is not "one more type" — it removes the constraints the generate → validate → critic → eval pipeline is built on, overlaps the freeform tools GraphPilot deliberately is *not* (the editor's non-freeform north star), and needs new schema/renderer/palette work for open-ended shapes. Treat as a separate product decision, not a backlog type.

#### Recommended direction

Ship **Framing A** first (bounded flowchart, plus optionally a bounded **org chart** / **mind map**, both structural trees that reuse the BDD block renderer + a tree layout). It delivers most of the "informal diagram" value at near-activity-diagram cost while preserving generate/validate/score. Revisit **Framing B** only as an explicit product pivot if bounded types prove too limiting; if pursued, it likely lands as an editor *mode* (freeform, unscored) rather than a generated type.

#### Build fit (Framing A)

- **Reuse:** `activityNode` renderers (canvas `customNodes.tsx` + SVG `diagram_render_service.py`), top-down layout direction, and most of the activity structural rules — so steps (2) and (4) of the recipe are mostly configuration, not new rendering.
- **New:** a permissive-but-named vocabulary in `diagram_types.py`; a `prompts.md` + few-shot set authored via the example-generation engine (Epic 3 Slice 11 — the same gating capability as the formal types); optional flowchart-specific shape polish (e.g. a parallelogram `io` symbol) if the reused activity shapes are not enough.
- **Cost driver:** as with every type, the answer-key/eval examples (step 3), not the plumbing.

#### Open questions (log in `decision-decisions.md` when scheduled)

- Does "informal diagrams" mean the bounded **Framing A** (recommended) or the freeform **Framing B** product pivot?
- If freeform is wanted, is it a generated *type* or an unscored editor *mode* — and how does that square with the non-freeform editor north star?
- How permissive should the flowchart vocabulary be before validation/eval stop being meaningful?
- Which informal types are worth it (flowchart first; then org chart / mind map)?

## Schema, storage, and API

### Diagram schema / data model

- **`parentId` grouping** — support advanced grouping via React Flow-compatible `parentId`. **Delivered** — `parentId` containment is live (Epic 2 Slice 05 + Epic 2's `04-editor-ui-ux` group), without `extent:'parent'` so children can be dragged out; drag-stop re-parenting owns `parentId`.
- **Required edge handles** — make `sourceHandle`/`targetHandle` required if precise connection points become necessary. Optional for MVP.
- **Top-level `groups`** — reintroduce group containers and group-oriented validation. Excluded from the active MVP schema; revisit only if the schema changes.

### Backend / storage

- **Backup / versioned save** — keep previous versions or backups of `<name>.gp.json` on save/update. No backup or versioning in MVP.
- **`diagramId` lookup model** — replace raw `diagramPath` handling with a `diagramId` indirection. Raw `diagramPath` is acceptable for the local MVP; this also unblocks the editor router/URL change above.
- **File locking** — guard concurrent writes instead of last-write-wins. Acceptable to defer for the local single-user MVP.
- **Database persistence** — move diagram persistence off local files into a database if ever needed. MVP persistence is file-based local workspace storage.

### Backend / API surface

- **Optional UI API routes** — add `POST /api/diagrams/validate`, `GET /api/schema`, and `GET /api/diagram-types` for the frontend. Out of Epic 2 scope; save owns validation internally for MVP. **Partially delivered** — `POST /api/diagrams/validate` plus a path-free `POST /api/diagrams/render` and `GET /api/diagrams/list` were added (Epic 3 / Epic 2's `04-editor-ui-ux` group); `GET /api/schema` and `GET /api/diagram-types` remain MCP-only and deferred.

## Generation, validation, and quality

### Rendering quality

- **Parallel edges into one node completely overlap.** **Promoted** to the `H` package of
  [`07-generation-quality/plan.md`](07-generation-quality/plan.md), along with container
  layout sprawl, label collisions, and the missing rendered-geometry test class. Kept here
  for traceability: every edge terminates at the target's single centre anchor, so 21 of 36
  committed examples draw markers on top of one another.

### Blueprints & generation

- **Generation workflow usability refinements** — evaluate whether the unified `diagram_generation_workflow` needs
  additional bounded framing guidance after production use, without aliases or bypassing canonical requests.
- **More blueprint families / variants** — additional blueprints and per-type variants beyond the three MVP types' starter blueprints.
- **Companion prompt-guidance files** — move prompt guidance out of the blueprint JSON into a separate companion file. Open future consideration.
- **Example libraries outside blueprint JSON** — keep richer example content separate from the main blueprint files.
- **LLM-backed generation** — generate diagrams with an LLM instead of (or alongside) template-backed blueprints. An option but not required for MVP.

### Validation & quality

- **Eval framework** — automated quality evaluation of generated diagrams. Out of MVP runtime validation.
- **Repair / autofix** — automatically fix invalid diagrams (including LLM-based repair) rather than only returning errors. Not required for MVP.
- **LLM-based validation / evaluation / judge** — use an LLM for runtime validation, advisory review, or eval scoring. Out of scope for MVP save-blocking validation.
- **Regression reports** — track validation/eval regressions over time. Post-MVP.
- **Stronger render-readiness checks** — deepen Layer 5 checks after `DiagramRenderService` is fully designed. Kept basic for MVP.
- **Configurable strict blueprint validation** — allow blueprint conformance to block saves/updates when desired. MVP keeps blueprint checks advisory only.
- **~~Rebuild the eval + DOE framework~~ — no longer applicable.** It measured how well a *model* generated a diagram, and GraphPilot no longer calls one: the host authors the draft and the backend materializes it deterministically, so there is no model choice, few-shot count or temperature left to sweep. Its design document went with the pipeline. What replaced it as the quality question — is the drawn diagram legible, faithful to its draft, and right — is owned by [`04-reviewing-diagrams.md`](../04-development/04-reviewing-diagrams.md) and the review gallery.

### RAG / example library (Epic 5, optional)

> **Epic 5, optional / post-MVP**, tracked on the [board](01-current-state.md). It remains deferred and is **not** scheduled into slices; the entries below are kept for traceability. *(The epic folder that held its definition went in the restructure.)*

- **Example-assisted generation** — use a local example library to improve generation quality. Optional post-MVP extension.
- **`diagram_search_examples`** — MCP tool for example/RAG retrieval. Outside current MVP scope.
- **Local RAG examples** — local retrieval corpus backing the above. Explicitly out of MVP scope.

## Export, import, and interoperability

### Export & rendering

- **PNG export** — optional render/export format beyond SVG. SVG is the MVP target. **Delivered** (Epic 2's `04-editor-ui-ux` group): the Export menu rasterizes the server-rendered SVG to PNG client-side, so there is no native dependency.
- **PDF export** — optional render/export format beyond SVG. SVG is the MVP target.
- **Inline image preview in MCP clients** — show the generated/rendered diagram *inline* in the agent chat, not just a link. **Deferred:** MCP standardizes the payload, not the presentation, and the tested agent-loop clients (Cline, Copilot) don't render an MCP `ImageContent` block cleanly (the base64 leaks into the model / the attachment is dropped), so the tools return a Markdown summary + `editUrl` today. Design paths (detailed in `docs/03-design/04-rendering.md` → *Inline previews*): (A) an **HTTP-served preview URL** referenced as a Markdown image (`![](http://localhost:8000/api/diagrams/preview?path=…)`, rendered on demand) — most universal, but couples MCP output to the running Django API (`runserver`) and depends on the client's webview allowing localhost images; (B) keep an image block **only for direct-render clients** (Claude Desktop, MCP Inspector); rejected: `data:` base64 (Cline dumps it) and `file://` (CSP-blocked). Server-side PNG **file** save via `diagram_render format="png"` is already delivered; this item is only the *inline* display. Pairs with the *Single-process serve* / *Installer / launcher* items (which guarantee the API is running).

### Import / interoperability

- **Import from external diagram tools** — import diagrams from draw.io, Lucidchart, and Visio into GraphPilot JSON so existing diagrams can be edited and re-rendered. Out of MVP scope. Needs per-format parsing (e.g. draw.io/`.drawio` XML, Lucidchart export, Visio `.vsdx`) mapped onto the canonical schema, with validation after import; likely lossy and best handled as a backend conversion step.

## MCP tools

### MCP tools (deferred)

- **`diagram_apply_patch` / structured patch operations** — controlled, ordered edit operations instead of full-JSON replacement. MVP IDE edits use full JSON replacement through `diagram_update`; patch ops are a post-MVP option.
- **`diagram_export`** — a dedicated export MCP tool. Covered for MVP by `diagram_render` (SVG) and browser API routes; not needed for MVP.
- **`diagram_edit`** — a separate natural-language edit wrapper. Overlaps with the current `diagram_update` workflow; deferred.

## Collaboration

### Collaboration (theme)

> Fuller planning entry (a **theme**, not one feature). The **north-star** is Google-Docs-style **real-time multi-user editing** — several people in the same diagram at once with live cursors, presence, and instantly merged edits. That is a **large architectural departure** from today's local-first, file-based, no-auth MVP (each user runs GraphPilot on their own machine; diagrams are `<name>.gp.json` files; last-write-wins), so it is explicitly **later future functionality**, staged behind smaller stepping-stones that are useful on their own. This section is where the *Robust editor* non-goal ("real-time collaboration") and the deferred *conflict detection* / *file locking* items converge.

#### Goal

Let multiple people work on the same GraphPilot diagram together — ultimately in real time (live cursors + presence + conflict-free merges) — while keeping GraphPilot JSON the source of truth. The single-user, offline round-trip (load → edit → save) and the IDE/MCP flow must keep working unchanged.

#### Why this is a big change (architecture tension)

Real-time co-editing conflicts with three core MVP assumptions, so it depends on the **Local internal distribution** theme above first resolving how GraphPilot is hosted:

- **No server** — live co-editing needs a shared, always-on backend (a WebSocket/transport plus a merge engine, typically a **CRDT** such as Yjs/Automerge, or OT). The per-machine model has no shared point to sync through.
- **No database** — concurrent sessions need shared, authoritative state (documents + presence + edit history) rather than a file on one user's disk. Ties to the deferred **Database persistence** and **`diagramId` lookup model** items.
- **No auth** — multi-user means identity, access control, and per-diagram sharing/permissions, none of which exist today.

Files-next-to-code (the technical-user IDE workflow) and live web co-editing are somewhat opposed models; a realistic design reconciles them (e.g. treat the shared server as the collaborative surface and sync/export back to files) rather than assuming one replaces the other.

#### Phased path (stepping-stones → north-star)

Staged so each phase is independently useful and de-risks the next:

1. **Conflict detection (safety first)** — a shared change/version marker written by both `POST /api/diagrams/save` and the IDE `diagram_update`, so concurrent edits are *detected* (and surfaced) instead of silently last-write-wins. Already tracked under *Editor enhancements* and *Backend/storage*; smallest first step and needed regardless of the eventual model.
2. **Async / git-based collaboration** — lean into local-first: diagrams-as-files reviewed via git/PR, with merge-friendly (stable-ordered, diff-clean) JSON and clear conflict resolution. No new server; fits the technical-user audience and the distribution theme.
3. **Presence & comments (lightweight sharing)** — a shared workspace where users see who else has a diagram open and can leave comments/annotations, without full live co-editing. First piece that genuinely requires a shared backend + identity.
4. **Real-time co-editing (north-star)** — Google-Docs-style live editing: CRDT/OT-merged edits over a WebSocket, live cursors, presence, and shared undo semantics, layered on the React Flow editor. The largest, most design-heavy phase; assumes the server/DB/auth foundation from phases 2–3 and the distribution decision.

#### Dependencies & sequencing

- Gated by the **Local internal distribution** theme (single-process serve → a hosted option) — real-time needs a hosted, shared backend, which is the opposite of the pure per-machine model.
- Builds on **conflict detection**, **file locking**, the **`diagramId` lookup model**, and **database persistence** (all deferred above) — these are prerequisites, not parallel work.
- The React Flow editor state (`nodes`/`edges` + the `useUndoRedo` history) is the integration point for a CRDT/OT layer; the reverse adapter must keep GraphPilot JSON as the merge/export target.

#### Open questions (log in `decision-decisions.md` when scheduled)

- Which merge model — **CRDT** (Yjs/Automerge) vs. **OT** — and does it operate on GraphPilot JSON directly or on a React Flow projection?
- Does real-time collaboration require abandoning (or dual-writing with) the files-next-to-code model, given the distribution theme?
- Auth/identity source and the per-diagram sharing/permission model (none exists today).
- How far to go before real-time — is async/git + presence/comments enough for the internal audience, deferring full live co-editing indefinitely?

## Testing, CI/CD, and delivery tooling

### Testing

- **Test the real React Flow output (round-trip)** — assert the saved diagram against React Flow's *actual* serialized state (`useReactFlow().toObject()` / the runtime `nodes`/`edges`), not the *simulated* React Flow state the Slice 04 Vitest unit test uses. Goal: confirm the reverse adapter's whitelist strips the runtime-only fields React Flow really emits (e.g. `measured`, `selected`, `dragging`, `width`/`height`) — the residual gap a simulated fixture can miss. Approach options: a jsdom component test rendering `<ReactFlow>` (needs `ResizeObserver` / `DOMMatrixReadOnly` / `getBoundingClientRect` mocks) that reads `toObject()`, or a real-browser run via Vitest browser mode (Playwright provider) for genuine drag gestures. Overlaps with the "Faithful browser round-trip test (Playwright E2E)" item under *Editor enhancements*; deferred as heavier tooling, best after Slice 04 confirms the schema round-trip. **Delivered** (Epic 2's `04-editor-ui-ux` group) — a Chromium Playwright e2e suite (`frontend/e2e/`) now drives the real editor in a browser through load → edit → save (and more).

### Measurement apparatus

**All resolved by deletion — nothing here is outstanding.** This section proposed work on
`live_anchor_service.py`, `live_anchor_artifact_store.py`, `run_service.py`,
`artifact_store.py`, `benchmark_readiness_effort` and `list_deployments`. **None of those
files exists.** They went with the provider pipeline, which is the rule working as
intended — a rig dies with the program it served. The backlog was the last place still
describing them, and it asked for a human decision on a command that had already been
deleted.

Two management commands remain, both product-facing and both documented in
[`05-command-reference.md`](../04-development/05-command-reference.md):
`render_example_gallery` and `review_gallery`.

### CI/CD

- **Automated CI pipeline** — run the checks (backend `manage.py test`, frontend lint/build/unit tests, Playwright e2e) automatically on every push/PR. **Out of MVP scope**: for now all tests are run **locally before pushing** (`frontend: npm run verify` + `backend: manage.py test`). GraphPilot's Bitbucket is **self-hosted (Server/Data Center)**, which has no built-in runner — real CI would need an external build server (Bamboo or Jenkins) provisioned by IT with Node, Python, and a headless browser available. A GitHub Actions starter file was drafted during the `04-editor-ui-ux` group (Epic 2) and then removed (wrong system for the on-prem Bitbucket). When a build agent exists, add the matching config (`Jenkinsfile` / Bamboo spec) reusing the same three jobs.
- **Continuous deployment** — not applicable to the local-first MVP (nothing is server-deployed); revisit only alongside the distribution theme above.

## Notes

- Keep entries short: what it is, why it is deferred, and a rough area/approach.
- When an item is picked up, promote it into the relevant epic/slice plan and remove it here.
- Decision rationale and status for items that are also tracked as decisions live in [`04-decisions.md`](04-decisions.md); live delivery status lives in [`01-current-state.md`](01-current-state.md).
- Older historical ideas not part of the active set (e.g. Mermaid/PlantUML/draw.io conversion targets, backend Playwright renderers) are in [`docs/07-history/`](../07-history/README.md) and git history.
