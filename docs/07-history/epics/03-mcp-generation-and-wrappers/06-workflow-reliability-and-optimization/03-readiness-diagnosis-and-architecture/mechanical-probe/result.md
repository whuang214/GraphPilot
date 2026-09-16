# E0 Offline Readiness Diagnosis

- Machine authority: [`result.json`](result.json)
- Digest: `sha256:da39b40e7caf23e3b6ebfa7e61d47c339cc4d79ad57d52c05d35f68fd1f73076`
- Source commit: `864ae30a8c1261234df9ed61fc413fad78ffd16a`
- Provider mode: `provider_free`; Azure calls: **0**

## Scope

This is mechanical/provider/performance diagnosis only. It is not human review, calibration, certification, promotion, or semantic-quality approval.

## Bound Case

- Case: `case-readiness-diagnostic-block3-mechanical-return-authorization-01`
- Scenario: `scenario-workflow-audit-activity-basic`
- Fixture: `backend/assets/blueprints/activity_diagram/context-examples/training/return-authorization`
- Scenario set: `sha256:f31a02716885dd2b7a51e4a17c016bf0bcda1d5274dc374659f172d7807484c2`
- Evidence: `sha256:ebf789e449a50c24ee2688101c80d7d29fdc47b6a93a19a0fe3b4d86ec5d6da2`
- Request: `sha256:629632f0855575187e8305a650705a54eef192f8106560f72b6dc458ae32b867`
- Projection: `sha256:80eefe74df7ce2c10b3b804a0e701982c48b7fd1faf4902d7f663d0f52d9c9e8`

## Local Wall-Time Evidence

One hundred provider-free iterations show all local readiness stages are millisecond-scale:

| Stage | Median ms | P95 ms | Maximum ms |
| --- | ---: | ---: | ---: |
| Preflight | 0.0047 | 0.0052 | 0.0092 |
| Projection build | 0.0511 | 0.0538 | 0.0603 |
| Forbidden scan | 0.9293 | 1.0208 | 1.3908 |
| Projection finalize | 0.4086 | 0.5017 | 0.7223 |
| Complete preparation | 1.3004 | 1.4900 | 2.4241 |
| Strict-schema projection | 0.1299 | 0.1330 | 0.1669 |
| Backend validation | 1.0134 | 1.1982 | 1.4961 |
| Result assembly | 1.1297 | 1.3491 | 1.5665 |

A cold immutable manifest/checkpoint/observation/terminal write set took 7.6261 ms. These stages cannot explain the historical provider latency; local contract or validation logic remains a plausible invalidity cause.

## Schema Projection Discriminator

The full backend review schema retains bounds, patterns, uniqueness, and array limits. `project_strict_output_schema` intentionally projects only Azure-supported structure and omits those constraints.

| Witness | Provider schema | Full schema | Backend | Exact backend issue |
| --- | --- | --- | --- | --- |
| Valid review | pass | pass | pass | — |
| Wrong kind | fail | fail | fail | `schema_const @ $.kind` |
| Missing coverage | fail | fail | fail | `schema_required @ $` |
| Extra top-level field | fail | fail | fail | `schema_additionalProperties @ $` |
| Rating `5` | **pass** | fail | fail | `schema_oneOf @ $.coverage[0].rating` |
| Empty rationale | **pass** | fail | fail | `schema_minLength`, `schema_pattern @ $.coverage[0].rationale` |
| Duplicate claim ref | **pass** | fail | fail | `schema_uniqueItems @ $.coverage[0].supportingClaimRefs` |
| Ten coverage rows | **pass** | fail | fail | `schema_maxItems @ $.coverage` |
| Rating 4 without support | pass | pass | fail | `invalid_strong_support @ $.coverage[0]` |

This proves a concrete response-validation boundary: provider-constrained output can still be mechanically invalid under backend authority. It does not prove which witness occurred historically because prior exact validation events were not retained.

## Repair Duplication

- Complete projection: 22,911 bytes.
- Projected provider schema: 7,519 bytes.
- First wire: 32,727 bytes.
- Repair user payload: 23,001 bytes.
- Repair wire: 32,252 bytes.
- Minimum repeated logical content: 30,430 bytes, or 94.35% of the repair wire.

Natural repair resends the complete projection and the same response schema. This confirms repair payload duplication as a cost amplifier, not yet the first-response trigger.

## E0 Conclusions

1. Local deterministic wall time is not the primary historical latency source; local contract/validation logic remains a plausible invalidity cause.
2. Provider-schema/backend-validation mismatch is mechanically reproducible and can cause natural repair.
3. Complete-projection repair repeats nearly the entire logical wire and amplifies latency.
4. Prompt instruction, deterministic-semantic validation, input size, and provider/control causes remain plausible.
5. The actual historical/live trigger remains unknown.

## Next Discriminator

Freeze and independently audit one high-effort manifest for the same case. This is the smallest live discriminator that can identify the actual trigger among schema projection, prompt, deterministic validation, size, and provider/control alternatives. Execute exactly one `readiness` call and only the naturally reached `readiness_response_repair`, if any; do not treat the experiment as confirmation of a favored root.
