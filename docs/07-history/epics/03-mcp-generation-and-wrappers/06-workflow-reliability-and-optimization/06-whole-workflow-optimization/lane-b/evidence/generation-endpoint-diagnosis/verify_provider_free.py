"""Provider-free executable proof for Block 6 S05 generation endpoint diagnosis.

Run from backend/ with graphpilot.live_anchor_settings and Azure settings blank. This
script reads committed source/fixtures plus the sibling proof JSON and writes no files.
"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "graphpilot.live_anchor_settings")

import django

django.setup()

from jsonschema import Draft202012Validator

from services.contracts.diagram_request_contract import DiagramRequestMode
from services.core.diagram_validation_service import DiagramValidationService
from services.generation.diagram_generation_service import DiagramGenerationService
from services.generation.diagram_layout_service import DiagramLayoutService, PyGraphvizLayoutEngine
from services.generation.generation_pipeline import assemble_canonical
from services.generation.semantic_review_service import SemanticReviewService
from services.llm.llm_client import FakeLLMClient, project_strict_output_schema
from services.support.canonical_json import canonical_json_digest
from tests.generation.test_pre_layout_generation_service import PreLayoutGenerationServiceTests


SEMANTICS = ("association", "composition", "generalization", "dependency", "commentLink")
EXPECTED_SIGNATURE = [{"code": "bdd_relationship_endpoints_invalid", "path": "$.edges[3]"}]


def _fixture_runtime():
    fixture_test = PreLayoutGenerationServiceTests(methodName="runTest")
    fixture_test.setUp()
    context_packet, context_base = fixture_test._packet_and_logical(
        DiagramRequestMode.CONTEXT,
        "bdd_diagram",
        0,
    )
    direct_packet, _ = fixture_test._packet_and_logical(
        DiagramRequestMode.DIRECT,
        "bdd_diagram",
        0,
    )
    return fixture_test, direct_packet, context_packet, context_base


def _base_for(context_base, mode):
    value = copy.deepcopy(context_base)
    if mode is DiagramRequestMode.DIRECT:
        value["schemaVersion"] = "graphpilot.direct.logical-diagram.bdd.v1"
        value["kind"] = "directLogicalDiagram"
        for item in value["nodes"] + value["edges"]:
            item.pop("origin", None)
    return value


def _add_note(value, mode):
    note = copy.deepcopy(value["nodes"][0])
    note.update(
        id="diagnosis-note",
        semanticType="note",
        label="Bounded annotation",
        stereotype=None,
        features={
            "properties": [],
            "operations": [],
            "receptions": [],
            "constraints": [],
            "literals": [],
        },
        isAbstract=None,
        unit=None,
        quantityKind=None,
        constraintExpression=None,
        constraintParameters=[],
    )
    if mode is DiagramRequestMode.CONTEXT:
        note["origin"] = copy.deepcopy(value["nodes"][0]["origin"])
    value["nodes"].append(note)


def _witness(context_base, mode, semantic_type, *, note_endpoint=True):
    value = _base_for(context_base, mode)
    _add_note(value, mode)
    template = value["edges"][0] if semantic_type == "composition" else value["edges"][2]
    edge = copy.deepcopy(template)
    edge["id"] = f"diagnosis-edge-{semantic_type.lower()}"
    edge["semanticType"] = semantic_type
    edge["source"] = "diagnosis-note" if note_endpoint else value["nodes"][0]["id"]
    edge["target"] = value["nodes"][0]["id"] if note_endpoint else value["nodes"][1]["id"]
    if semantic_type != "composition":
        edge["sourceEnd"] = None
        edge["targetEnd"] = None
    value["edges"].append(edge)
    return value


def _schema_error_counts(fixture_test, packet, value):
    provider_errors = list(
        Draft202012Validator(project_strict_output_schema(packet.response_schema)).iter_errors(value)
    )
    full_errors = list(
        Draft202012Validator(
            dict(packet.response_schema),
            registry=fixture_test.validator._references,
        ).iter_errors(value)
    )
    return len(provider_errors), len(full_errors)


def _issue_signature(result):
    return [{"code": item.code, "path": item.path} for item in result.issues]


def main():
    fixture_test, direct_packet, context_packet, context_base = _fixture_runtime()
    packets = {
        DiagramRequestMode.DIRECT: direct_packet,
        DiagramRequestMode.CONTEXT: context_packet,
    }
    matrix = []
    controls = []

    for mode in (DiagramRequestMode.DIRECT, DiagramRequestMode.CONTEXT):
        packet = packets[mode]
        for semantic_type in SEMANTICS:
            value = _witness(context_base, mode, semantic_type)
            provider_count, full_count = _schema_error_counts(fixture_test, packet, value)
            result = fixture_test.validator.validate(packet, value)
            row = {
                "mode": mode.value,
                "semanticType": semantic_type,
                "digest": canonical_json_digest(value),
                "providerProjection": "pass" if provider_count == 0 else "fail",
                "fullSchema": "pass" if full_count == 0 else "fail",
                "backendRuntime": (
                    "bdd_relationship_endpoints_invalid @ $.edges[3]"
                    if _issue_signature(result) == EXPECTED_SIGNATURE
                    and not result.provenance_issues
                    else "unexpected"
                ),
            }
            matrix.append(row)

        corrected = _witness(context_base, mode, "commentLink")
        corrected["edges"].pop()
        provider_count, full_count = _schema_error_counts(fixture_test, packet, corrected)
        corrected_result = fixture_test.validator.validate(packet, corrected)

        block_comment = _witness(context_base, mode, "commentLink", note_endpoint=False)
        block_provider_count, block_full_count = _schema_error_counts(
            fixture_test,
            packet,
            block_comment,
        )
        block_result = fixture_test.validator.validate(packet, block_comment)
        controls.append(
            {
                "mode": mode.value,
                "corrected": {
                    "digest": canonical_json_digest(corrected),
                    "providerProjection": "pass" if provider_count == 0 else "fail",
                    "fullSchema": "pass" if full_count == 0 else "fail",
                    "backendRuntime": "pass" if corrected_result.valid else "fail",
                },
                "blockCommentLinkCompatibility": {
                    "digest": canonical_json_digest(block_comment),
                    "providerProjection": "pass" if block_provider_count == 0 else "fail",
                    "fullSchema": "pass" if block_full_count == 0 else "fail",
                    "backendRuntime": "pass" if block_result.valid else "fail",
                },
            }
        )

    invalid = _witness(context_base, DiagramRequestMode.CONTEXT, "commentLink")
    corrected = copy.deepcopy(invalid)
    corrected["edges"].pop()
    fake = FakeLLMClient([invalid, corrected])
    accepted = fixture_test.service.generate(
        context_packet,
        fake,
        max_repair_rounds=1,
    )
    repair = json.loads(fake.calls[1]["user"])

    semantic = SemanticReviewService(packet_builder=fixture_test.builder).review(
        context_packet,
        accepted,
        FakeLLMClient({}),
        quality_mode="standard",
    )
    canonical, engine = assemble_canonical(
        DiagramGenerationService._assembly_logical(semantic.document),
        "bdd_diagram",
        "diagnosis-witness",
        "fake-model",
        DiagramLayoutService(engine=PyGraphvizLayoutEngine()),
    )
    canonical["metadata"].pop("generatedBy", None)
    for edge, logical_edge in zip(canonical["edges"], semantic.document["edges"], strict=True):
        edge["id"] = logical_edge["id"]
    canonical_result = DiagramValidationService().validate(canonical)

    proof_path = Path(__file__).with_name("provider-free-proof.json")
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    proof_digest = canonical_json_digest({key: value for key, value in proof.items() if key != "digest"})

    assert matrix == proof["boundedWitnessMatrix"]
    assert all(
        control["corrected"]["backendRuntime"] == "pass"
        and control["blockCommentLinkCompatibility"]["backendRuntime"] == "pass"
        for control in controls
    )
    assert repair["kind"] == "contextGenerationRepairInput"
    assert repair["validationIssues"] == [
        {
            "code": "bdd_relationship_endpoints_invalid",
            "path": "$.edges[3]",
            "elementId": "diagnosis-edge-commentlink",
            "message": "BDD relationships require block endpoints.",
            "details": {},
        }
    ]
    assert repair["structuralIssues"] == []
    assert repair["provenanceIssues"] == []
    assert accepted.candidate_digest == canonical_json_digest(corrected)
    assert accepted.repair_rounds_used == 1
    assert canonical_result.valid
    assert engine == "pygraphviz-dot"
    assert proof["digest"] == proof_digest

    print(
        json.dumps(
            {
                "status": "pass",
                "providerCalls": 0,
                "fakeCalls": len(fake.calls),
                "witnessCells": len(matrix),
                "controls": sum(len(item) - 1 for item in controls),
                "repairRoundsUsed": accepted.repair_rounds_used,
                "assembly": {
                    "engine": engine,
                    "nodes": len(canonical["nodes"]),
                    "edges": len(canonical["edges"]),
                    "canonicalValid": canonical_result.valid,
                },
                "proofDigest": proof_digest,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
