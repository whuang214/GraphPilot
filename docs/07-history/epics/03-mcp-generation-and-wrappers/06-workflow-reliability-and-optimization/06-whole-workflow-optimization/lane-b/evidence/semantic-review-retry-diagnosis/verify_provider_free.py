"""Durable provider-free proof for Block 6 S09 semantic-review retry diagnosis.

Run with Azure settings blank. The proof uses current committed source, training fixtures,
``FakeLLMClient``, and in-memory validators. It reads the sibling proof/root JSON and the
retained tracked g2 summary, writes no files, and constructs no provider client.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import os
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("Repository root not found.")


REPO_ROOT = _repo_root()
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "graphpilot.live_anchor_settings")

import django

django.setup()

from jsonschema import Draft202012Validator

from services.contracts.diagram_request_contract import DiagramRequestMode
from services.contracts.generation_contracts import PROMPT_VERSIONS
from services.generation.semantic_review_rubric import FACET_FINDING_CODES
from services.generation.semantic_review_service import SemanticReviewService
from services.llm.llm_client import FakeLLMClient, project_strict_output_schema
from services.support.canonical_json import canonical_json_digest
from tests.generation.test_semantic_review_service import SemanticReviewServiceTests


DIAGRAM_TYPES = ("activity_diagram", "use_case_diagram", "bdd_diagram")
EXPECTED_RUNTIME = "finding_invalid @ $"
V1_PROMPTS = (
    "backend/graphpilot/prompts/direct-semantic-review-v1.md",
    "backend/graphpilot/prompts/context-semantic-review-v1.md",
    "backend/graphpilot/prompts/direct-semantic-review-response-repair-v1.md",
    "backend/graphpilot/prompts/context-semantic-review-response-repair-v1.md",
)
V2_PROMPTS = tuple(path.replace("-v1.md", "-v2.md") for path in V1_PROMPTS)
TRACE_FILES = V1_PROMPTS + (
    "backend/graphpilot/schemas/direct-semantic-review-input.json",
    "backend/graphpilot/schemas/context-semantic-review-input.json",
    "backend/graphpilot/schemas/direct-semantic-review-response.json",
    "backend/graphpilot/schemas/context-semantic-review-response.json",
    "backend/graphpilot/schemas/direct-semantic-review-repair-input.json",
    "backend/graphpilot/schemas/context-semantic-review-repair-input.json",
    "backend/services/contracts/generation_contracts.py",
    "backend/services/generation/semantic_review_rubric.py",
    "backend/services/generation/semantic_review_service.py",
    "backend/services/llm/llm_client.py",
    "backend/tests/generation/test_semantic_review_service.py",
)
G2_RESULT = (
    REPO_ROOT
    / "docs/03-development-and-delivery/epics/03-mcp-generation-and-wrappers"
    / "06-workflow-reliability-and-optimization/06-whole-workflow-optimization"
    / "evidence/generation-endpoint-wave/live-result.json"
)


def _sha256_file(relative_path: str) -> str:
    return "sha256:" + hashlib.sha256((REPO_ROOT / relative_path).read_bytes()).hexdigest()


def _head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _fixture_test() -> SemanticReviewServiceTests:
    fixture = SemanticReviewServiceTests(methodName="runTest")
    fixture.setUp()
    return fixture


def _schema_layers(fixture, packet, response):
    key = f"{packet.mode.value}_semantic_review_response"
    schema = fixture.service._schemas.get_schema(key)
    provider_errors = list(
        Draft202012Validator(project_strict_output_schema(schema)).iter_errors(response)
    )
    full_errors = list(
        Draft202012Validator(
            schema,
            registry=fixture.service._references,
        ).iter_errors(response)
    )
    return len(provider_errors), len(full_errors)


def _ask_user_finding(fixture, packet, candidate):
    return fixture._finding(
        packet,
        candidate,
        {"kind": "ask_user", "question": "Which authority should control this gap?"},
    )


def _facet_code_witness(fixture, packet, candidate):
    response = fixture._response(packet, candidate)
    finding = _ask_user_finding(fixture, packet, candidate)
    response["facets"][0]["rating"] = 1
    response["facets"][0]["findings"] = [
        {**copy.deepcopy(finding), "code": "scope_violation"}
    ]
    return response


def _three_witnesses(fixture):
    packet, candidate = fixture._packet_candidate(
        DiagramRequestMode.CONTEXT,
        "bdd_diagram",
    )
    clean = fixture._response(packet, candidate)
    finding = _ask_user_finding(fixture, packet, candidate)

    facet_code = _facet_code_witness(fixture, packet, candidate)

    without_gap = copy.deepcopy(clean)
    without_gap["facets"][0]["findings"] = [copy.deepcopy(finding)]

    facet_mismatch = copy.deepcopy(clean)
    facet_mismatch["facets"][0]["rating"] = 1
    facet_mismatch["facets"][0]["findings"] = [
        {
            **copy.deepcopy(finding),
            "facet": "scopeCompliance",
            "code": "scope_violation",
        }
    ]

    definitions = (
        (
            "witness-facet-code-mismatch",
            facet_code,
            {
                "containingFacet": "goalFidelity",
                "rating": 1,
                "findingFacet": "goalFidelity",
                "findingCode": "scope_violation",
            },
        ),
        (
            "witness-finding-without-gap",
            without_gap,
            {
                "containingFacet": "goalFidelity",
                "rating": 4,
                "findingFacet": "goalFidelity",
                "findingCode": "goal_mismatch",
            },
        ),
        (
            "witness-finding-facet-mismatch",
            facet_mismatch,
            {
                "containingFacet": "goalFidelity",
                "rating": 1,
                "findingFacet": "scopeCompliance",
                "findingCode": "scope_violation",
            },
        ),
    )

    rows = []
    repair_binding = None
    for witness_id, response, mutation in definitions:
        provider_count, full_count = _schema_layers(fixture, packet, response)
        review_input = fixture.service._review_input(
            packet,
            candidate,
            fixture.rubrics.get_rubric(packet.mode, packet.diagram_type),
        )
        try:
            fixture.service._assemble_result(
                packet,
                candidate,
                fixture.rubrics.get_rubric(packet.mode, packet.diagram_type),
                response,
                review_input,
            )
        except ValueError as exc:
            backend_message = str(exc)
        else:
            backend_message = "accepted"

        client = FakeLLMClient([response, clean])
        result = fixture.service.review(
            packet,
            candidate,
            client,
            max_repair_rounds=0,
        )
        initial_input = json.loads(client.calls[0]["user"])
        repair_input = json.loads(client.calls[1]["user"])
        runtime = (
            EXPECTED_RUNTIME
            if len(client.calls) == 2
            and repair_input["validationIssues"][0]["code"] == "finding_invalid"
            and repair_input["validationIssues"][0]["path"] == "$"
            else "unexpected"
        )
        rows.append(
            {
                "id": witness_id,
                "mode": "context",
                "diagramType": "bdd_diagram",
                "digest": canonical_json_digest(response),
                "mutation": mutation,
                "providerProjection": "pass" if provider_count == 0 else "fail",
                "fullResponseSchema": "pass" if full_count == 0 else "fail",
                "backendValidatorMessage": backend_message,
                "backendRuntime": runtime,
                "fakeCalls": len(client.calls),
                "postRepairResult": result.status,
            }
        )
        if witness_id == "witness-facet-code-mismatch":
            repair_binding = {
                "initialResponseDigest": canonical_json_digest(response),
                "initialInputDigest": canonical_json_digest(initial_input),
                "repairKind": repair_input["kind"],
                "repairInputCarriesIdenticalSemanticReviewInput": (
                    repair_input["semanticReviewInput"] == initial_input
                ),
                "rejectedResponseDigest": canonical_json_digest(
                    json.loads(repair_input["rejectedResponse"])
                ),
                "validationIssue": {
                    "code": repair_input["validationIssues"][0]["code"],
                    "path": repair_input["validationIssues"][0]["path"],
                },
                "repairAttempt": repair_input["repairAttempt"],
                "repairPromptVersion": repair_input["versions"]["repairPromptVersion"],
                "responseSchemaVersion": repair_input["versions"]["responseSchemaVersion"],
                "findingCodesByFacetPresent": (
                    "findingCodesByFacet" in initial_input["allowlists"]
                ),
                "initialPromptIsCurrentV1": client.calls[0]["system"]
                == (REPO_ROOT / "backend/graphpilot/prompts/context-semantic-review-v1.md")
                .read_text(encoding="utf-8"),
                "repairPromptIsCurrentV1": client.calls[1]["system"]
                == (
                    REPO_ROOT
                    / "backend/graphpilot/prompts/context-semantic-review-response-repair-v1.md"
                )
                .read_text(encoding="utf-8"),
            }

    return rows, repair_binding


def _six_cell_matrix(fixture):
    rows = []
    for mode in DiagramRequestMode:
        for diagram_type in DIAGRAM_TYPES:
            packet, candidate = fixture._packet_candidate(mode, diagram_type)
            response = _facet_code_witness(fixture, packet, candidate)
            clean = fixture._response(packet, candidate)
            provider_count, full_count = _schema_layers(fixture, packet, response)
            client = FakeLLMClient([response, clean])
            result = fixture.service.review(
                packet,
                candidate,
                client,
                max_repair_rounds=0,
            )
            repair_input = json.loads(client.calls[1]["user"])
            rows.append(
                {
                    "mode": mode.value,
                    "diagramType": diagram_type,
                    "digest": canonical_json_digest(response),
                    "providerProjection": "pass" if provider_count == 0 else "fail",
                    "fullResponseSchema": "pass" if full_count == 0 else "fail",
                    "backendRuntime": (
                        EXPECTED_RUNTIME
                        if repair_input["validationIssues"][0]["code"] == "finding_invalid"
                        and repair_input["validationIssues"][0]["path"] == "$"
                        else "unexpected"
                    ),
                    "fakeCalls": len(client.calls),
                    "postRepairResult": result.status,
                }
            )
    return rows


def _corrected_witness(fixture):
    packet, candidate = fixture._packet_candidate(
        DiagramRequestMode.CONTEXT,
        "bdd_diagram",
    )
    response = fixture._response(packet, candidate, rating=1)
    response["facets"][0]["findings"] = [
        fixture._finding(
            packet,
            candidate,
            {"kind": "ask_user", "question": "Clarify the requested goal?"},
        )
    ]
    provider_count, full_count = _schema_layers(fixture, packet, response)
    client = FakeLLMClient(response)
    result = fixture.service.review(
        packet,
        candidate,
        client,
        max_repair_rounds=0,
    )
    return {
        "mode": "context",
        "diagramType": "bdd_diagram",
        "digest": canonical_json_digest(response),
        "containingFacet": "goalFidelity",
        "rating": 1,
        "findingFacet": "goalFidelity",
        "findingCode": "goal_mismatch",
        "providerProjection": "pass" if provider_count == 0 else "fail",
        "fullResponseSchema": "pass" if full_count == 0 else "fail",
        "backendAssembly": "pass" if result.status == "blocked" else "fail",
        "responseRepairTriggered": len(client.calls) != 1,
        "fakeCalls": len(client.calls),
        "result": result.status,
    }


def _current_trace(fixture):
    packet, candidate = fixture._packet_candidate(
        DiagramRequestMode.CONTEXT,
        "bdd_diagram",
    )
    rubric = fixture.rubrics.get_rubric(packet.mode, packet.diagram_type)
    review_input = fixture.service._review_input(packet, candidate, rubric)
    response_schema = fixture.service._schemas.get_schema("context_semantic_review_response")
    provider_schema = project_strict_output_schema(response_schema)
    initial_prompts = [
        (REPO_ROOT / path).read_text(encoding="utf-8") for path in V1_PROMPTS[:2]
    ]
    repair_prompts = [
        (REPO_ROOT / path).read_text(encoding="utf-8") for path in V1_PROMPTS[2:]
    ]
    assemble_source = inspect.getsource(SemanticReviewService._assemble_result)

    return {
        "promptVersions": {
            key: PROMPT_VERSIONS[key]
            for key in (
                "direct.semantic_review",
                "context.semantic_review",
                "direct.semantic_review_response_repair",
                "context.semantic_review_response_repair",
            )
        },
        "v1PromptAssetsPresent": all((REPO_ROOT / path).is_file() for path in V1_PROMPTS),
        "v2PromptAssetsPresent": any((REPO_ROOT / path).exists() for path in V2_PROMPTS),
        "initialPrompts": {
            "sayAllowlistedFindings": all(
                "allowlisted findings" in prompt for prompt in initial_prompts
            ),
            "explicitFindingCodesByFacet": any(
                "findingCodesByFacet" in prompt for prompt in initial_prompts
            ),
            "explicitContainingFacetEquality": any(
                "containing rubric facet" in prompt for prompt in initial_prompts
            ),
            "explicitBelowMinimumOnly": any(
                "below" in prompt and "minimumRating" in prompt
                for prompt in initial_prompts
            ),
        },
        "repairPrompts": {
            "preserveAttemptedAssessment": all(
                "Preserve the attempted assessment" in prompt for prompt in repair_prompts
            ),
            "explicitFindingCodesByFacet": any(
                "findingCodesByFacet" in prompt for prompt in repair_prompts
            ),
            "explicitContainingFacetEquality": any(
                "containing rubric facet" in prompt for prompt in repair_prompts
            ),
            "explicitBelowMinimumOnly": any(
                "below" in prompt and "minimumRating" in prompt
                for prompt in repair_prompts
            ),
        },
        "reviewInput": {
            "rubricFacetIdsPresent": [item["id"] for item in review_input["rubric"]["facets"]]
            == [facet.id for facet in rubric.facets],
            "rubricMinimumRatingsPresent": all(
                item["minimumRating"] == 3 for item in review_input["rubric"]["facets"]
            ),
            "referenceAllowlistsPresent": all(
                key in review_input["allowlists"]
                for key in ("elementIds", "claimRefs", "assumptionRefs", "schemaRules")
            ),
            "findingCodesByFacetPresent": (
                "findingCodesByFacet" in review_input["allowlists"]
            ),
            "backendFacetRegistryCompleteForRubric": all(
                facet.id in FACET_FINDING_CODES for facet in rubric.facets
            ),
        },
        "responseSchema": {
            "globalFindingCodeEnumCount": len(
                response_schema["$defs"]["findingCode"]["enum"]
            ),
            "findingCodesByFacetPresent": "findingCodesByFacet"
            in json.dumps(response_schema, sort_keys=True),
            "fullSchemaApplicabilityConditionalPresent": "allOf"
            in response_schema["$defs"]["facetReview"],
        },
        "providerProjection": {
            "globalFindingCodeEnumCount": len(
                provider_schema["$defs"]["findingCode"]["enum"]
            ),
            "findingCodesByFacetPresent": "findingCodesByFacet"
            in json.dumps(provider_schema, sort_keys=True),
            "applicabilityConditionalPresent": "allOf"
            in provider_schema["$defs"]["facetReview"],
        },
        "backendValidator": {
            "requiresContainingFacetEquality": (
                "Proposed finding facet must match its containing facet." in assemble_source
            ),
            "usesFacetFindingCodeRegistry": "validate_finding_code" in assemble_source,
            "requiresBelowMinimumOutcome": (
                "A sufficient/N/A facet cannot emit a finding." in assemble_source
            ),
            "findingRegistryEntries": len(FACET_FINDING_CODES),
        },
        "fileDigests": {path: _sha256_file(path) for path in TRACE_FILES},
    }


def _g2_control():
    value = json.loads(G2_RESULT.read_text(encoding="utf-8"))
    digest = canonical_json_digest({key: item for key, item in value.items() if key != "digest"})
    return {
        "packageId": value["candidate"]["packageId"],
        "runId": value["candidate"]["runId"],
        "observationId": value["candidate"]["observationId"],
        "diagnosticsRunId": value["candidate"]["diagnosticsRunId"],
        "resultDigest": value["candidate"]["resultDigest"],
        "observationDigest": value["candidate"]["observationDigest"],
        "terminalDigest": value["candidate"]["terminalDigest"],
        "diagnosticsDigest": value["artifacts"]["diagnosticsDigest"],
        "diagnosticsFiles": value["artifacts"]["diagnosticsFiles"],
        "diagnosticsBytes": value["artifacts"]["diagnosticsBytes"],
        "correctionCommit": value["correctionCommit"],
        "roles": value["provider"]["roles"],
        "completedCalls": value["provider"]["completed"],
        "semanticReviewFirstResponseValid": value["provider"][
            "semanticReviewFirstResponseValid"
        ],
        "semanticReviewResponseRepairCalls": value["provider"][
            "semanticReviewResponseRepairCalls"
        ],
        "semanticRepairCalls": value["provider"]["semanticRepairCalls"],
        "review": value["quality"]["review"],
        "reviewScore": value["quality"]["reviewScore"],
        "sourceDigestValid": value["digest"] == digest,
        "sourceDigest": value["digest"],
        "interpretation": (
            "unchanged semantic V1 produced one valid sample; this does not remove shapes "
            "permitted by the provider-visible contract and rejected by backend policy"
        ),
        "currentRepairCallSavingBaseline": False,
    }


def _observed():
    fixture = _fixture_test()
    witnesses, repair_binding = _three_witnesses(fixture)
    return {
        "sourceCommit": _head(),
        "scope": {
            "providerCalls": 0,
            "productionChangedByProof": False,
            "testSourceChangedByProof": False,
            "rawProviderResponseAccessed": False,
            "hiddenReasoningAccessed": False,
        },
        "boundedWitnesses": witnesses,
        "sixCellFacetCodeMatrix": _six_cell_matrix(fixture),
        "correctedWitness": _corrected_witness(fixture),
        "responseRepairBinding": repair_binding,
        "currentContractTrace": _current_trace(fixture),
        "g2Control": _g2_control(),
    }


def _assert_observed(observed):
    assert len(observed["boundedWitnesses"]) == 3
    assert all(
        row["providerProjection"] == "pass"
        and row["fullResponseSchema"] == "pass"
        and row["backendRuntime"] == EXPECTED_RUNTIME
        and row["fakeCalls"] == 2
        for row in observed["boundedWitnesses"]
    )
    assert len(observed["sixCellFacetCodeMatrix"]) == 6
    assert all(
        row["providerProjection"] == "pass"
        and row["fullResponseSchema"] == "pass"
        and row["backendRuntime"] == EXPECTED_RUNTIME
        and row["fakeCalls"] == 2
        for row in observed["sixCellFacetCodeMatrix"]
    )
    assert observed["correctedWitness"]["backendAssembly"] == "pass"
    assert observed["correctedWitness"]["responseRepairTriggered"] is False
    assert observed["correctedWitness"]["fakeCalls"] == 1
    binding = observed["responseRepairBinding"]
    assert binding["initialResponseDigest"] == binding["rejectedResponseDigest"]
    assert binding["repairInputCarriesIdenticalSemanticReviewInput"] is True
    assert binding["validationIssue"] == {"code": "finding_invalid", "path": "$"}
    assert binding["repairAttempt"] == 1
    assert binding["findingCodesByFacetPresent"] is False
    assert binding["initialPromptIsCurrentV1"] is True
    assert binding["repairPromptIsCurrentV1"] is True
    trace = observed["currentContractTrace"]
    assert trace["v1PromptAssetsPresent"] is True
    assert trace["v2PromptAssetsPresent"] is False
    assert trace["initialPrompts"]["sayAllowlistedFindings"] is True
    assert trace["initialPrompts"]["explicitFindingCodesByFacet"] is False
    assert trace["initialPrompts"]["explicitContainingFacetEquality"] is False
    assert trace["initialPrompts"]["explicitBelowMinimumOnly"] is False
    assert trace["repairPrompts"]["preserveAttemptedAssessment"] is True
    assert trace["repairPrompts"]["explicitFindingCodesByFacet"] is False
    assert trace["repairPrompts"]["explicitContainingFacetEquality"] is False
    assert trace["repairPrompts"]["explicitBelowMinimumOnly"] is False
    assert trace["reviewInput"]["findingCodesByFacetPresent"] is False
    assert trace["responseSchema"]["globalFindingCodeEnumCount"] == 15
    assert trace["responseSchema"]["findingCodesByFacetPresent"] is False
    assert trace["providerProjection"]["globalFindingCodeEnumCount"] == 15
    assert trace["providerProjection"]["findingCodesByFacetPresent"] is False
    assert trace["providerProjection"]["applicabilityConditionalPresent"] is False
    assert all(trace["backendValidator"].values())
    g2 = observed["g2Control"]
    assert g2["packageId"] == "g2"
    assert g2["correctionCommit"].startswith("a17bc40")
    assert g2["roles"] == ["readiness", "generation", "semantic_review"]
    assert g2["completedCalls"] == 3
    assert g2["semanticReviewFirstResponseValid"] is True
    assert g2["semanticReviewResponseRepairCalls"] == 0
    assert g2["semanticRepairCalls"] == 0
    assert g2["review"] == "pass" and g2["reviewScore"] == 100
    assert g2["diagnosticsRunId"] == "run-g"
    assert g2["diagnosticsFiles"] == 26
    assert g2["sourceDigestValid"] is True
    assert g2["currentRepairCallSavingBaseline"] is False


def _verify_evidence(observed):
    proof_path = Path(__file__).with_name("provider-free-proof.json")
    root_path = Path(__file__).with_name("root-decision.json")
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    root = json.loads(root_path.read_text(encoding="utf-8"))
    proof_digest = canonical_json_digest(
        {key: value for key, value in proof.items() if key != "digest"}
    )
    root_digest = canonical_json_digest(
        {key: value for key, value in root.items() if key != "digest"}
    )
    assert proof["digest"] == proof_digest
    assert root["digest"] == root_digest
    assert proof["executableObservation"] == observed
    assert proof["witnessMethod"]["executableProofDigest"] == _sha256_file(
        str(Path(__file__).relative_to(REPO_ROOT)).replace("\\", "/")
    )
    assert root["evidence"]["providerFreeProofDigest"] == proof_digest
    assert root["sourceCommit"] == observed["sourceCommit"]
    return proof_digest, root_digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--observed",
        action="store_true",
        help="Print the reconstructed observation before sibling evidence exists.",
    )
    args = parser.parse_args()
    observed = _observed()
    _assert_observed(observed)
    if args.observed:
        print(json.dumps(observed, indent=2, sort_keys=True))
        return
    proof_digest, root_digest = _verify_evidence(observed)
    print(
        json.dumps(
            {
                "status": "pass",
                "providerCalls": 0,
                "fakeCalls": 19,
                "findingWitnesses": 3,
                "sixCellMatrix": 6,
                "correctedWitness": "pass_no_response_repair",
                "responseRepairBinding": "pass",
                "g2Control": "valid_sample_not_disconfirmation_no_current_saving_baseline",
                "proofDigest": proof_digest,
                "rootDigest": root_digest,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
