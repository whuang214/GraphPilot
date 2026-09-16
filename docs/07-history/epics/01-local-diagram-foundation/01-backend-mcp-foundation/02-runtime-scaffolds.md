# Slice 02: Runtime Scaffolds

## Purpose

Create the runnable local skeletons for the backend, frontend, and MCP package layout so development can proceed against a working environment instead of placeholder folders.

## Included Work

- add the root `requirements.txt` if it is still missing
- scaffold the Django and Django REST Framework baseline under `backend/`
- establish the backend folder layout for API, MCP, shared services, and tests
- scaffold the frontend with Vite, React, and TypeScript under `frontend/`
- add the MCP server package structure under `backend/`
- add initial config and environment placeholders aligned with the active docs
- update setup docs if the scaffold shape differs from the documented baseline

## Not In Scope

- full validation behavior
- rendering implementation
- diagram generation or update workflows
- completed API and MCP handlers beyond what is required to prove the skeleton starts

## Target Areas

- `backend/`
- `backend/README.md`
- `frontend/`
- `frontend/README.md`
- `docs/03-development-and-delivery/00-development-environment.md`
- `docs/03-development-and-delivery/epics/00-current-state.md`

## Exit Criteria

- Django starts locally on the documented port
- the frontend starts locally on the documented port
- the backend structure exists for API, MCP, services, and tests
- the MCP package structure exists in the documented backend area
- documentation reflects the scaffold that was actually created

## Next Slice

- `03-contracts-schema-and-blueprints.md`

## Outcome

✅ Completed as planned. Django backend scaffolded with flat layout and GET /api/health; Vite/React-TS frontend scaffolded with @xyflow/react; MCP server skeleton boots and responds to client calls. All exit criteria verified (Django boots, /api/health 200, MCP server tools respond, frontend builds/dev passes). Documentation updated to match actual scaffold shape. No deviations; committed as 79286d5. Follow-up: none.