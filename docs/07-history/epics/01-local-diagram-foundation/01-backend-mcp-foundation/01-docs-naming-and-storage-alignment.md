# Slice 01: Docs, Naming, and Storage Alignment

## Purpose

Remove documentation ambiguity before implementation begins so Epic 1 work can follow one storage convention, one slice sequence, and one active navigation path.

## Included Work

- confirm the active Epic 1 slice structure and sequencing
- align active docs on the `.graphpilot/<number>/diagram.gp.json` storage convention
- remove or flag legacy `.wwd-diagrams/diagram.wwd.json` references from active delivery planning where they still create confusion
- keep `README.md`, `docs/README.md`, and delivery-planning navigation aligned with the active epic-folder structure
- update `epics/00-current-state.md` so the active slice and next slice match the revised plan
- record the Epic 1 planning decision in `decision-decisions.md`

## Not In Scope

- backend code implementation
- frontend code implementation
- MCP tool implementation
- runtime validation or smoke-test execution

## Primary Files

- `README.md`
- `docs/README.md`
- `docs/03-development-and-delivery/README.md`
- `docs/03-development-and-delivery/epics/README.md`
- `docs/03-development-and-delivery/epics/00-current-state.md`
- `docs/03-development-and-delivery/epics/01-local-diagram-foundation/00-epic.md`
- `docs/02-design-and-features/decision-decisions.md`

## Exit Criteria

- active docs no longer conflict on the Epic 1 storage convention
- Epic 1 uses the revised slice sequence and file names
- active README navigation still points to the right Epic 1 entry points
- current-state tracking identifies the correct active slice and next recommended slice
- any open planning questions are explicitly tracked instead of being implied by conflicting docs

## Next Slice

- `02-runtime-scaffolds.md`

## Outcome

✅ Completed as planned. All active docs now use the `.graphpilot/<number>/diagram.gp.json` storage convention; legacy `.wwd-diagrams/diagram.wwd.json` references removed from 7 active documentation files. Epic 1 slice structure and navigation updated and aligned. No deviations; all exit criteria met. Follow-up: none.