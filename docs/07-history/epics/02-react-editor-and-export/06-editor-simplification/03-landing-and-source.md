# Slice 03: Landing and Source

## Purpose

Give standalone and IDE-driven openings one quiet document editor while making standalone creation/opening explicit on a simple landing page.

## Design

- No `diagramPath` displays the landing page rather than an empty editor or inferred project.
- The landing page offers type-first New blank, Open file, drag-to-open, reopenable Recents, and Clear recents; it has no project/workspace list.
- New blank supports Activity, Use Case, BDD, and an advanced Custom option; it creates valid client-side canonical JSON with no generation call.
- A blank diagram is unsaved and always uses Save As first.
- A valid IDE `diagramPath` opens directly. Failure remains visible with Retry, Open file, and Home recovery.
- The editor header never displays workspace, MCP, URL, external-file, or read-only origin labels.
- One information popover exposes only available filename/path, writable/read-only/unsaved state, revision conflict state, and copy path.
- Persistent Recents contain only backend paths GraphPilot can reopen. Picker/drop files may remain available in-session but are not persisted across restart. Clear recents removes history only.

## Included Work

- Add a valid blank-diagram factory and type-first landing interaction.
- Remove WorkspaceBrowser/Browse from the reachable product surface and source-chip presentation from the header.
- Add source-information popover behavior and clean recovery/Home navigation.
- Add clearable reopenable-only recents and protect dirty/unsaved navigation.
- Preserve workspace-path stale-write checks, external handle validation, save normalization, autosave boundaries, and direct IDE loading internally.
- Update unit/E2E coverage, navigation docs, and current delivery status.

## Not In Scope

- Project selection or workspace browsing.
- Persisting File System Access handles in IndexedDB.
- Backend generation or context-authoring UI.
- A routing library or multi-page router dependency.

## Target Areas

- `frontend/src/editor/components/Home.tsx` and component tests.
- `frontend/src/editor/shell/TopBar.tsx` and shell tests.
- `frontend/src/editor/EditorPage.tsx`.
- `frontend/src/editor/lib/recents.ts`, file-system helpers, and focused tests.
- WorkspaceBrowser reachability/removal and frontend E2E coverage.
- Frontend README, architecture, editor design, decisions, Epic 2 plan, and live status.

## Exit Criteria

- Standalone entry shows the approved landing actions and no workspace/project list.
- Each blank type opens as valid empty canonical JSON, stays unsaved, and routes first Save through Save As.
- Valid IDE links bypass the landing page; failed links provide explicit recovery.
- The editor header is transport-neutral and source details appear only in the information popover.
- Persistent recents contain only reopenable paths, can be cleared without deleting files, and do not claim picker/drop handles survive restart.
- Dirty/unsaved navigation and existing stale-source protections remain safe.
- Full frontend verification and relevant backend checks pass.

## Previous Slice

- [`02-boundary-connections.md`](02-boundary-connections.md)

## Next Slice

- End of Epic 2's `06-editor-simplification/` group.

## Outcome

**Completed.** Standalone `/editor` now shows a type-first landing page with valid client-side Activity, Use Case, BDD, and advanced Custom blanks, Open file, drag-to-open, reopenable path Recents, and Clear recents. Blank/read-only documents route first Save through Save As. Valid IDE `diagramPath` links still open directly, while picker/drop files remain session-owned and never enter persistent Recents.

**Source UI.** Workspace/project browsing and every persistent source-origin chip are removed from the reachable editor. Home is the single document switcher, with dirty-change confirmation. One `ⓘ` popover reveals only available filename/path, writable/read-only/unsaved state, revision, and Copy path; internal path/file ownership still enforces focus refresh, stale-write protection, and stale-completion isolation.

**Deviation.** The existing `WorkspaceBrowser` module and read-only list API remain compatible but unreachable rather than being deleted as a separate public-interface cleanup. Browser file handles remain session-only by design.

**Verification.** The post-implementation audit found no blockers. `cd frontend; npm run verify` passes lint, production build/typecheck, 400 unit tests, and 27 Playwright tests. `cd backend; uv run python manage.py test` passes 617 tests (3 skipped). `git diff --check` is clean.
