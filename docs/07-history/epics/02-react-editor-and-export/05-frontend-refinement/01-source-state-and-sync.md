# Slice 01: Source State and Sync

## Purpose

Give workspace paths and external files one source-session model so open, edit, validate, save, reload, and repository context stay synchronized without redirecting a write to the wrong source.

## Design

- A source session records the persistence owner, source identity, write capability, repository match, canonical baseline, and current open generation.
- Workspace paths and external file handles use source-specific I/O behind the same session transitions and save-state rules.
- Repository matching resolves to **matched**, **unmatched**, or **ambiguous**. One unambiguous ID/filename match is adopted automatically as the current workspace path; the editor never guesses among candidates.
- URL, Browse, recent, and picker-resolved repository opens all produce the same workspace-owned session. An unmatched picker file remains external and saves through its browser handle.
- The URL, ownership-oriented source chip, Browse availability, recents, Save/Save As actions, dirty state, revision, and last successful baseline derive from the active session rather than parallel booleans.
- Open and save completions carry the session generation that started them, so stale asynchronous work cannot overwrite a newer session.

## Included Work

- Introduce the unified source-session state and source-specific load/save adapters.
- Add automatic repository matching with explicit unmatched and ambiguous fallbacks.
- Synchronize workspace query parameters, external handles, repository context, recents, source presentation, and save capabilities.
- Adopt validated/normalized save results and opaque revisions as the session baseline while preserving edits made during an in-flight save.
- Refresh workspace sources on focus/visibility when clean; surface Review/Reload/Keep editing when the disk revision changed under local edits; reject stale expected revisions before overwrite.
- Cover workspace open, picker open, dropped read-only files, Save As, automatic repository matching, broken links, rapid source switching, external changes, and stale completion handling.

## Not In Scope

- Continuous filesystem watching, automatic merge/conflict resolution, or silent replacement of a dirty canvas; focus-based clean reload and explicit conflict handling are included.
- Persisting browser file-handle permission across restarts.
- Changing canonical diagram semantics, route geometry, or rendering.
- Treating an ambiguous repository candidate as a match.

## Target Areas

- `frontend/src/editor/EditorPage.tsx`.
- Source-session, file-system, and recents helpers under `frontend/src/editor/lib/`.
- `frontend/src/editor/shell/TopBar.tsx` and `frontend/src/editor/components/WorkspaceBrowser.tsx`.
- `frontend/src/api/diagrams.ts` and repository-match API coverage where backend path authority is required.
- Frontend unit and end-to-end source-flow tests; supporting backend API tests.

## Exit Criteria

- Every successful open produces exactly one active source session and canonical baseline.
- Workspace and external sessions share open/save state transitions while retaining their correct persistence owner.
- One valid repository match switches automatically to the workspace path; no match or multiple matches leave the source external and make no workspace write possible by accident.
- URL state, ownership source chip, Browse, recents, Save, Save As, and revision checks always reflect the active session.
- A clean workspace session refreshes after an external change; a dirty session is never replaced or overwritten without explicit resolution.
- Late open/save responses cannot mutate a newer session, and in-flight local edits survive baseline adoption.
- Source-flow tests and the relevant frontend/backend checks pass.

## Previous Slice

- [`../04-editor-ui-ux/15-deferred-editor-polish.md`](../04-editor-ui-ux/15-deferred-editor-polish.md)

## Next Slice

- [`02-bdd-marker-correctness.md`](02-bdd-marker-correctness.md)

## Outcome

**Completed.** `EditorPage` now owns one `DiagramSession` whose source is workspace, external writable file, or read-only file. Picker opens resolve ID/filename/content revision only inside the active/recent workspace, matched files reopen through the authoritative backend path, and Save As updates the parent-owned source without state drift. Workspace and external sources refresh on focus, dirty changes expose Review/Reload/Keep editing, and stale writes are blocked unless explicitly overwritten.

**Deviation.** Browser security still prevents discovering an arbitrary picker path; no/ambiguous matches remain external. File handles are session-only, as designed.

**Verification.** API/file-system unit tests, backend load/save/resolve tests, and Playwright coverage exercise matched picker adoption, clean refresh, dropped read-only state, and stale-save conflict review. Final aggregate gate evidence is recorded in Slice 08.
