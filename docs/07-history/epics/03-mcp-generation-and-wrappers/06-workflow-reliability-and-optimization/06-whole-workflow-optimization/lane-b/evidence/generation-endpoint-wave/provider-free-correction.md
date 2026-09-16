# Generation Endpoint Provider-Free Correction

- Machine authority: [`provider-free-correction.json`](provider-free-correction.json)
- Machine self-digest: `sha256:bd00b7a6993e197e8be2261bf1bac78030dd4e0e2d63aeb2a3c4f21453f80a35`
- Clean starting HEAD: `ef2361d3ffcab4be31e174742b4ad3c603e8811b` on `lane-b-optimization`
- S05 root: `generation_prompt_projection_schema_validator_contract` / `semantic_blind_bdd_structural_endpoint_scope`
- Result: **PASS** for the authorized provider-free correction
- Provider calls: **0**

## Correction

The private current-V1 BDD `diagramModel` now gives direct/context initial and repair calls one coherent endpoint scope:

- `association`, `composition`, `generalization`, and `dependency` each require two existing Block endpoints;
- their existing relationship direction/end checks remain unchanged;
- note attachments use `commentLink`; and
- `commentLink` is excluded from the structural Block-endpoint and connectivity predicates.

Deterministic validation applies the Block-only predicate only to those four structural semantics. It adds no converse
`commentLink` endpoint policy, so the characterized Block-to-Block compatibility shape remains accepted. The stable
`bdd_relationship_endpoints_invalid` code, message, deterministic ordering, `validationIssues` repair bucket, candidate
authority, and bounded generation repair remain unchanged.

## Test-First Evidence

The exact four S05 regressions were added before either production file changed. With Azure variables blank and
`graphpilot.live_anchor_settings`, the command found four tests and failed as expected in 4.534 seconds with exit 1,
`7 failures / 2 subtest errors`:

1. `test_bdd_generation_packets_expose_structural_endpoint_and_note_attachment_rules_in_both_modes` saw the incomplete
   four-rule BDD packet projection.
2. `test_bdd_note_comment_link_is_excluded_from_structural_block_endpoint_rule_in_both_directions_and_modes` saw
   `bdd_relationship_endpoints_invalid @ $.edges[3]` in all four direction/mode cells.
3. `test_bdd_endpoint_scope_repair_packet_repeats_provider_visible_rules` saw both repair packets repeat the incomplete
   projection.
4. `test_bdd_note_comment_link_reaches_pre_layout_acceptance_without_generation_repair_in_both_modes` raised
   `DeterministicGenerationFailure` in both modes after the fake client repeated the rejected candidate.

Exact failing-before command:

```powershell
$env:AZURE_OPENAI_ENDPOINT=""; $env:AZURE_OPENAI_API_KEY=""; $env:AZURE_OPENAI_DEPLOYMENT=""; cd "C:\Users\w105098\GP-LB\backend"; uv run --with-requirements "..\requirements.txt" python manage.py test --settings graphpilot.live_anchor_settings tests.generation.test_generation_packet_builder.GenerationPacketBuilderTests.test_bdd_generation_packets_expose_structural_endpoint_and_note_attachment_rules_in_both_modes tests.generation.test_pre_layout_generation_service.PreLayoutGenerationServiceTests.test_bdd_note_comment_link_is_excluded_from_structural_block_endpoint_rule_in_both_directions_and_modes tests.generation.test_pre_layout_generation_service.PreLayoutGenerationServiceTests.test_bdd_endpoint_scope_repair_packet_repeats_provider_visible_rules tests.generation.test_pre_layout_generation_service.PreLayoutGenerationServiceTests.test_bdd_note_comment_link_reaches_pre_layout_acceptance_without_generation_repair_in_both_modes
```

Before implementation, the five preserving regressions already passed in 6.391 seconds. After implementation, the same
four correction regressions passed in 3.745 seconds and the five preserving regressions passed in 6.036 seconds.

## Preserved Controls

Provider-free regressions prove:

- all `4 structural semantics × 2 modes = 8` Note-endpoint witnesses pass provider projection and full logical schema,
  then retain the exact stable deterministic endpoint rejection;
- `commentLink` accepts Note-to-Block and Block-to-Note in both modes (`4` cells) without generation repair;
- Block-to-Block `commentLink` remains accepted in both modes (`2` compatibility cells);
- repair retains the exact rejected candidate, input digest, diagram model, issue code/path/element, and corrected candidate;
- all twelve checked-in training fixtures remain accepted with zero deterministic repair rounds; and
- a four-node/three-edge structural-class control remains accepted without reconstructing the intentionally unretained
  Block 5 provider candidate. The immutable Block 5 result remains the authority for that actual repaired candidate.

## Verification

Every command below blanked Azure settings and used no-dotenv live-anchor settings:

| Check | Result |
| --- | --- |
| Exact four corrected regressions | `4 passed in 3.745s` |
| Five preserving regressions | `5 passed in 6.036s` |
| Changed packet/pre-layout modules | `37 passed in 17.983s` |
| S05 focused strict-schema/generation/repair/review/live-harness guard set | `105 passed in 144.850s` |
| Broader provider-free `tests.generation` suite | `202 passed in 164.897s` |
| Readiness + frozen-history guards | `110 tests run, 1 skipped in 304.843s` |
| Full backend | `1,069 passed, 5 skipped in 600.715s` |
| Frontend lint/build/unit | `0 warnings/errors; build pass; 419 passed` |
| Frontend E2E | `43 passed in 2.0m` |
| Independent implementation audit | `PASS; 0 critical/high/medium` |

Focused S05 guard command:

```powershell
$env:AZURE_OPENAI_ENDPOINT=""; $env:AZURE_OPENAI_API_KEY=""; $env:AZURE_OPENAI_DEPLOYMENT=""; cd "C:\Users\w105098\GP-LB\backend"; uv run --with-requirements "..\requirements.txt" python manage.py test --settings graphpilot.live_anchor_settings tests.llm.test_llm_client.ProviderStrictSchemaTests tests.generation.test_generation_packet_builder tests.generation.test_pre_layout_generation_service tests.generation.test_semantic_review_service tests.generation.test_diagram_generation_service tests.generation.test_diagram_generation_context_service tests.evaluation.workflow_audit.test_client tests.evaluation.workflow_audit.test_live_anchor_service
```

Broader commands:

```powershell
$env:AZURE_OPENAI_ENDPOINT=""; $env:AZURE_OPENAI_API_KEY=""; $env:AZURE_OPENAI_DEPLOYMENT=""; cd "C:\Users\w105098\GP-LB\backend"; uv run --with-requirements "..\requirements.txt" python manage.py test --settings graphpilot.live_anchor_settings tests.generation
$env:AZURE_OPENAI_ENDPOINT=""; $env:AZURE_OPENAI_API_KEY=""; $env:AZURE_OPENAI_DEPLOYMENT=""; cd "C:\Users\w105098\GP-LB\backend"; uv run --with-requirements "..\requirements.txt" python manage.py test --settings graphpilot.live_anchor_settings tests.readiness tests.evaluation.historical.full_effort
```

The machine evidence contains every exact command, exit code, test count, duration, contract control, and changed-file
path. Its self-digest was recomputed over canonical compact JSON after removing only the top-level `digest` member:

```powershell
uv run python -c "import hashlib,json,pathlib; p=pathlib.Path(r'C:\Users\w105098\GP-LB\docs\03-development-and-delivery\epics\03-mcp-generation-and-wrappers\06-workflow-reliability-and-optimization\06-whole-workflow-optimization\evidence\generation-endpoint-wave\provider-free-correction.json'); value=json.loads(p.read_text(encoding='utf-8')); value.pop('digest'); raw=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8'); print('sha256:'+hashlib.sha256(raw).hexdigest())"
```

Result: `sha256:bd00b7a6993e197e8be2261bf1bac78030dd4e0e2d63aeb2a3c4f21453f80a35`.

## Scope and Deviations

Writes are confined to the two S05 production owners, two named generation test modules, canonical generation design,
S06 Outcome, provider-free proof files, and the independent implementation audit. No prompt, schema, registry, MCP, semantic-review, readiness, host, Lane A,
B0, shared status/group/decision/ledger/backlog, `.env`, provider, browser, port, live identity, calibration,
certification, promotion, deployment, or push changed.

The full backend/frontend gates and independent implementation audit passed. The first isolated frontend verify could not
start E2E because the worktree had no repo-relative `.venv`; E2E then passed using the existing project interpreter on PATH,
without tracked changes. No S07 live claim or performance claim is made.
