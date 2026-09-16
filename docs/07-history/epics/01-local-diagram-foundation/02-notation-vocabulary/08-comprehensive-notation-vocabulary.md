# Slice 08: Comprehensive Notation Vocabulary

## Purpose

Expand the per-type vocabulary (the Epic 1-owned type profile + schema/blueprint docs +
structural critic) to the *commonly used* UML/SysML notation, anchored to **UML 2.5.1**
(activity, use case) and **SysML 1.6** (BDD). This is the foundation the Epic 2 renderer
slice (`02-…/09-comprehensive-node-and-edge-shapes.md`) builds on.

## Background

The MVP shipped a deliberately minimal shape set. Research against the OMG specs and
uml-diagrams.org / sysml.org (verified live: `omg.org/spec/UML/2.5.1`,
`omg.org/spec/SysML/1.6`) confirmed the common elements missing. Vocabulary lives in the
type profile (`backend/services/diagrams/catalog/diagram_types.py`); it auto-feeds the generation prompt,
advisory validation, and `diagram_get_schema` / `diagram_list_types`.

## Design

Additive only — `data.semanticType` stays a **free string** in `diagram.json`, so freeform
`custom` saves are never blocked; the type profile is the enforced allow-list for
`generated` diagrams. New common-tier vocabulary:

- **activity**: nodes + `fork`, `join` (and `start`/`end` adopt the canonical initial /
  activity-final symbols — a rendering change owned by the Epic 2 slice).
- **use case**: edges + `generalization`; include/extend direction corrected in guidance.
- **bdd**: nodes + `enumeration`; edges + `aggregation`, `association`.

## Included Work

- `backend/services/diagrams/catalog/diagram_types.py` — extend the three allowed-set frozensets.
- `backend/assets/blueprints/<type>/prompts.md` — new vocabulary + when-to-use guidance.
- `backend/services/diagrams/validation/structural_constraints.py` — fork (≥2 out) / join (≥2 in) rules; use-case
  `generalization` same-kind rule; relax the BDD generalization rule to **same kind** (so the
  new node types don't false-positive); description text updated.
- Design docs: `docs/02-design-and-features/diagram-schemas/<type>-diagram-blueprints.md`,
  `00-diagram-json-schema.md` recommended types, and `decision-decisions.md`.
- `backend/tests/contracts/test_contracts.py` — updated exact-set assertions.

## Not In Scope

- Renderers / canvas / palette / SVG markers (Epic 2 slice 09).
- Advanced elements (swimlanes, pins, object/datastore, signal/event/time nodes,
  interfaceBlock, ports, packages, dependency) — deferred.
- Re-curating the training/eval example library to exercise the new shapes (a later slice).

## Target Areas

- `backend/services/diagrams/catalog/diagram_types.py`, `backend/services/diagrams/validation/structural_constraints.py`
- `backend/assets/blueprints/<type>/prompts.md`
- `docs/02-design-and-features/diagram-schemas/`, `00-diagram-json-schema.md`, `decision-decisions.md`

## Exit Criteria

- New semantic types accepted by the type profile, validation, and the schema MCP tools.
- Structural critic enforces the new rules without false-positives on existing diagrams.
- Backend test suite green.

## Previous Slice

- `../01-backend-mcp-foundation/07-smoke-test-and-readmes.md`

## Next Slice

- `../../02-react-editor-and-export/03-comprehensive-shapes/09-comprehensive-node-and-edge-shapes.md` — the renderer/canvas
  side that draws the new vocabulary.

## Outcome

✅ Completed as planned. Vocabulary expanded to the common UML 2.5.1 / SysML 1.6 tier and
the structural critic updated; `semanticType` stays open so `custom` saves are unaffected.
No deviations; all exit criteria met.

**Verification.** `python manage.py test` → 333 passed (includes new fork/join, use-case
`generalization` same-kind, and BDD same-kind structural-rule tests).

**Follow-up.** The example/eval re-baseline (training + eval answer keys that exercise the new
shapes, re-seed, DOE) is intentionally deferred to a separate slice/chat.
