# Slice 09: Validation Contract Hygiene

## Purpose

Tighten the validation *contract* so it matches the implementation and can't silently drift:
remove the dead `ValidationLayer` values, make the issue `code` vocabulary a single registry, and
correct the validation design doc. A hardening follow-on from the Epic 1 validation review.

## Background

An architecture review of the validation subsystem surfaced three small contract-level issues:

- `ValidationLayer` carried `request` and `operation` values that **nothing emits** — Layers 1
  (request/file safety) and 6 (operation-specific) live in the entry points / operation callers
  and surface through `DiagramErrorResponse`, not as `ValidationIssue` objects.
- Issue `code` strings were inline literals scattered across `DiagramValidationService`, with no
  registry or stability note — a growing consumed vocabulary (Epic 1's `04-universal-vocabulary` group added stereotype codes).
- `02-validation-design.md` listed all six layers as `layer` values and framed the layers as a
  strict pipeline, when Layers 2–5 actually run and **aggregate** with no short-circuit.

## Design

- **Prune the enum.** `ValidationLayer` keeps only the four emitting layers (`schema`, `structure`,
  `blueprint`, `render_readiness`). Safe: no code emits or consumes `request`/`operation`, and the
  frontend `ValidationErrorDetail` has no `layer` field, so serialized output is unchanged.
- **Registry.** A new `ValidationCode(str, Enum)` in `validation_contract.py` is the single source
  of truth for every static code; the schema layer keeps a documented dynamic family via
  `SCHEMA_CODE_PREFIX` (`schema_<jsonschema-keyword>`). `DiagramValidationService` emits
  `ValidationCode.*.value` (or the prefix), so `code` stays a plain string. `is_registered()` backs
  the tests.
- **Docs.** The design doc's layer list is corrected, an **issue-code table** (code → layer →
  severity) + a stability note are added, and the pipeline wording notes the no-short-circuit
  aggregation.

## Included Work

- `backend/services/diagrams/validation/validation_contract.py` — drop `REQUEST`/`OPERATION`; add `SCHEMA_CODE_PREFIX`,
  `ValidationCode`, and `ValidationCode.is_registered()`.
- `backend/services/diagrams/validation/diagram_validation_service.py` — emit codes via the registry / prefix; fix the
  stale `03-validation-design.md` docstring reference to `02-`.
- `backend/tests/core/test_validation_service.py` — every emitted code is registered + a source guard
  that no raw `code="..."` literal remains.
- `backend/tests/contracts/test_contracts.py` — `ValidationCode` uniqueness, `is_registered`, and the
  emitting-layer set.
- `docs/02-design-and-features/02-validation-design.md` — layer list, issue-code table + stability
  note, aggregation wording.

## Not In Scope

- Emitting `request`/`operation` issues from the entry points (they keep their own error contract).
- Any change to which conditions are errors vs. warnings (severities are unchanged).
- Frontend changes (`ValidationErrorDetail` is unaffected).

## Target Areas

- `backend/services/diagrams/validation/validation_contract.py`, `backend/services/diagrams/validation/diagram_validation_service.py`
- `backend/tests/core/test_validation_service.py`, `backend/tests/contracts/test_contracts.py`
- `docs/02-design-and-features/02-validation-design.md`

## Exit Criteria

- `ValidationLayer` lists only the four emitting layers; nothing references the removed values.
- Every emitted code is a plain string from `ValidationCode` (or the `schema_` family); the source
  guard passes.
- The design doc's layer list + issue-code table match the registry.
- Backend test suite green.

## Previous Slice

- `../02-notation-vocabulary/08-comprehensive-notation-vocabulary.md`

## Next Slice

- `10-validated-write-enforcement.md` — make "validate before write" structural.

## Outcome

✅ Completed as planned. `ValidationLayer` pruned to the four emitting layers; issue codes
centralized in a `ValidationCode` registry (+ `schema_` dynamic family) with a stability note and
doc table; the design doc's layer list and pipeline wording corrected. No behavior/severity
changes; serialized output unchanged.

**Verification.** `python manage.py test tests.core.test_validation_service tests.contracts.test_contracts` → 51
passed (includes the new registry, code-registration, and source-guard tests). Full-suite +
frontend verification run with the S09–S11 batch.

**Follow-up.** None.
