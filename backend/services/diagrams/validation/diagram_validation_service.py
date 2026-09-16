"""Shared, deterministic validation for canonical GraphPilot diagram JSON.

``DiagramValidationService`` validates an in-memory diagram dict and returns a
structured :class:`~services.diagrams.validation.validation_contract.ValidationResult`. It is reused
by both the Django API and the MCP ``diagram_validate`` tool so both entry points
share the same validation decisions while adapting their client-specific envelopes.

Boundaries (see ``docs/02-design-and-features/02-validation-design.md``):

- this service does not read or write files; callers load the diagram (via
  ``WorkspaceStorageService``) and pass the parsed dict in
- path safety belongs to ``WorkspaceStorageService``, not here
- blueprint/type drift produces advisory warnings and never blocks validation;
  only an unsupported ``diagramType`` is blocking in the advisory layer

Validation layers run in order (request/file safety is Layer 1 and lives in the
entry points, not here):

- Layer 2: canonical JSON schema validation (``jsonschema``)
- Layer 3: structural graph validation
- Layer 4: advisory blueprint/type-profile checks
- Layer 5: basic render-readiness checks
"""

import math
from typing import Any, Dict, List, Optional

from jsonschema import Draft202012Validator

from services.shared.schema_registry import SchemaRegistry
from services.shared.diagram_type_service import DiagramTypeService
from services.diagrams.validation.structural_constraints import check_structural_constraints
from services.diagrams.validation.validation_contract import (
    SCHEMA_CODE_PREFIX,
    Severity,
    ValidationCode,
    ValidationIssue,
    ValidationLayer,
    ValidationResult,
    ValidationStats,
)

# Thresholds for non-blocking structural warnings (centralized in services/catalog/constants.py).
from services.diagrams.catalog.constants import HIGH_EDGE_COUNT, HIGH_NODE_COUNT, LONG_LABEL_LENGTH  # noqa: E402

# Render text-fitting constants, shared with the renderer, so the render-readiness
# truncation check mirrors what DiagramRenderService actually does (see _label_capacity).
from services.diagrams.catalog.constants import (  # noqa: E402
    CHAR_WIDTH_RATIO,
    DEFAULT_NODE_SIZES,
    FALLBACK_SIZE,
    LINE_HEIGHT,
    MIN_FONT_SIZE,
    TEXT_PADDING,
)


def _is_finite_number(value: Any) -> bool:
    """Return whether *value* is a finite real number (and not a bool).

    JSON numbers decode to ``int`` or ``float``; booleans are excluded because
    ``bool`` is a subclass of ``int`` but is never a valid coordinate or size.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(value)


def _json_path(path_parts) -> str:
    """Render a jsonschema error path deque as a ``$``-rooted JSON path."""
    out = "$"
    for part in path_parts:
        if isinstance(part, int):
            out += f"[{part}]"
        else:
            out += f".{part}"
    return out


def _non_finite_number_issues(value: Any, path_parts=()) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if isinstance(value, float) and not math.isfinite(value):
        issues.append(
            ValidationIssue(
                severity=Severity.ERROR,
                layer=ValidationLayer.SCHEMA,
                code=ValidationCode.NON_FINITE_NUMBER.value,
                message="JSON numbers must be finite.",
                path=_json_path(path_parts),
            )
        )
    elif isinstance(value, dict):
        for key, child in value.items():
            issues.extend(_non_finite_number_issues(child, (*path_parts, key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            issues.extend(_non_finite_number_issues(child, (*path_parts, index)))
    return issues


def _multiplicity_issue(value: Any, path: str) -> Optional[ValidationIssue]:
    if not isinstance(value, dict):
        return None
    lower, upper = value.get("lower"), value.get("upper")
    if (
        isinstance(lower, int)
        and not isinstance(lower, bool)
        and isinstance(upper, int)
        and not isinstance(upper, bool)
        and upper < lower
    ):
        return ValidationIssue(
            severity=Severity.ERROR,
            layer=ValidationLayer.SCHEMA,
            code=ValidationCode.INVALID_MULTIPLICITY.value,
            message="Multiplicity upper must be greater than or equal to lower.",
            path=path,
        )
    return None


def _multiplicity_issues(diagram: Dict[str, Any]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    def check(value: Any, path: str) -> None:
        issue = _multiplicity_issue(value, path)
        if issue:
            issues.append(issue)

    def check_property_list(values: Any, path: str) -> None:
        for index, value in enumerate(values if isinstance(values, list) else []):
            if isinstance(value, dict):
                check(value.get("multiplicity"), f"{path}[{index}].multiplicity")

    def check_parameter_list(values: Any, path: str) -> None:
        for index, value in enumerate(values if isinstance(values, list) else []):
            if isinstance(value, dict):
                check(value.get("multiplicity"), f"{path}[{index}].multiplicity")

    for node_index, node in enumerate(diagram.get("nodes") if isinstance(diagram.get("nodes"), list) else []):
        if not isinstance(node, dict) or not isinstance(node.get("data"), dict):
            continue
        data = node["data"]
        features = data.get("features")
        if isinstance(features, dict):
            base = f"$.nodes[{node_index}].data.features"
            check_property_list(features.get("properties"), f"{base}.properties")
            for operation_index, operation in enumerate(
                features.get("operations") if isinstance(features.get("operations"), list) else []
            ):
                if isinstance(operation, dict):
                    check_parameter_list(
                        operation.get("parameters"),
                        f"{base}.operations[{operation_index}].parameters",
                    )
        check_parameter_list(
            data.get("constraintParameters"),
            f"$.nodes[{node_index}].data.constraintParameters",
        )

    for edge_index, edge in enumerate(diagram.get("edges") if isinstance(diagram.get("edges"), list) else []):
        if not isinstance(edge, dict) or not isinstance(edge.get("data"), dict):
            continue
        data = edge["data"]
        for end_name in ("sourceEnd", "targetEnd"):
            end = data.get(end_name)
            if not isinstance(end, dict):
                continue
            base = f"$.edges[{edge_index}].data.{end_name}"
            check(end.get("multiplicity"), f"{base}.multiplicity")
            check_property_list(end.get("qualifiers"), f"{base}.qualifiers")

    return issues


def _nodes_reaching_parent_cycle(parent_by_id: Dict[str, tuple[str, int]]) -> set[str]:
    reaches_cycle: Dict[str, bool] = {}
    for start in parent_by_id:
        if start in reaches_cycle:
            continue
        trail: List[str] = []
        trail_index: Dict[str, int] = {}
        current = start
        while current in parent_by_id and current not in reaches_cycle and current not in trail_index:
            trail_index[current] = len(trail)
            trail.append(current)
            current = parent_by_id[current][0]
        reaches = current in trail_index or reaches_cycle.get(current, False)
        for node_id in trail:
            reaches_cycle[node_id] = reaches
    return {node_id for node_id, reaches in reaches_cycle.items() if reaches}


def _label_capacity(width: float, height: float) -> int:
    """Approximate how many characters a *width* x *height* node box can show at the
    renderer's smallest font.

    Mirrors the render service's deterministic text estimate (``diagram_render_service._fit_text``):
    width per character is ``font * CHAR_WIDTH_RATIO`` and each line is ``font * LINE_HEIGHT``
    tall, evaluated at ``MIN_FONT_SIZE`` (the smallest the renderer shrinks to before it
    ellipsizes). A rectangular text area is assumed; non-rectangular shapes (diamond/
    ellipse/actor) expose *less* room, so this over-estimates capacity and therefore only
    flags labels that would be truncated in any shape (conservative — no false alarms).
    """
    usable_width = max(1.0, width - TEXT_PADDING * 2)
    chars_per_line = max(1, int(usable_width / (MIN_FONT_SIZE * CHAR_WIDTH_RATIO)))
    max_lines = max(1, int(height / (MIN_FONT_SIZE * LINE_HEIGHT)))
    return chars_per_line * max_lines


class DiagramValidationService:
    """Validates canonical GraphPilot diagram JSON and returns a structured result.

    Args:
        schema_service: Optional injected :class:`SchemaRegistry`. A default
            instance is created when omitted.
        type_service: Optional injected :class:`DiagramTypeService`. A default
            instance is created when omitted.
    """

    def __init__(
        self,
        schema_service: Optional[SchemaRegistry] = None,
        type_service: Optional[DiagramTypeService] = None,
    ) -> None:
        self._schema_service = schema_service or SchemaRegistry()
        self._type_service = type_service or DiagramTypeService()
        self._validator: Optional[Draft202012Validator] = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def validate(self, diagram: Any) -> ValidationResult:
        """Validate *diagram* and return a structured :class:`ValidationResult`.

        *diagram* should be a parsed JSON object (dict). A non-dict input fails
        at the schema layer rather than raising.
        """
        issues: List[ValidationIssue] = []

        if not isinstance(diagram, dict):
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    layer=ValidationLayer.SCHEMA,
                    code=ValidationCode.INVALID_ROOT_TYPE.value,
                    message=(
                        "Diagram must be a JSON object; got "
                        f"{type(diagram).__name__}."
                    ),
                    path="$",
                )
            )
            return ValidationResult.from_issues(issues, stats=ValidationStats())

        nodes = diagram.get("nodes")
        edges = diagram.get("edges")
        node_list = nodes if isinstance(nodes, list) else []
        edge_list = edges if isinstance(edges, list) else []
        stats = ValidationStats(node_count=len(node_list), edge_count=len(edge_list))

        # Layer 2: canonical JSON schema validation.
        issues.extend(self._validate_schema(diagram))
        issues.extend(_non_finite_number_issues(diagram))
        issues.extend(_multiplicity_issues(diagram))

        # Layers 3-5 inspect nodes/edges directly. Run them even if the schema
        # layer reported issues so the caller sees as much detail as possible,
        # but skip if nodes/edges are not arrays (already reported by schema).
        if isinstance(nodes, list):
            issues.extend(self._validate_structure(node_list, edge_list))
            issues.extend(self._validate_render_readiness(node_list, edge_list))

        # Layer 4: advisory blueprint/type-profile checks.
        issues.extend(self._validate_type_profile(diagram, node_list, edge_list))

        return ValidationResult.from_issues(issues, stats=stats)

    # ------------------------------------------------------------------
    # Layer 2: schema
    # ------------------------------------------------------------------

    def _get_validator(self) -> Draft202012Validator:
        """Build and cache the schema validator (the schema is immutable).

        Lazy init is intentionally lock-free: under a concurrent first call two
        validators may be built, but reference assignment is atomic and neither
        result is corrupted, so the extra object is simply discarded.
        """
        if self._validator is None:
            # Surface a malformed schema artifact eagerly rather than on the
            # first input that happens to touch the broken part.
            schema = self._schema_service.checked_schema("diagram")
            self._validator = Draft202012Validator(schema)
        return self._validator

    def _validate_schema(self, diagram: Dict[str, Any]) -> List[ValidationIssue]:
        validator = self._get_validator()
        issues: List[ValidationIssue] = []
        # Sort by the rendered JSON path so error order is deterministic without
        # comparing mixed str/int path segments directly.
        for error in sorted(validator.iter_errors(diagram), key=lambda e: _json_path(e.absolute_path)):
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    layer=ValidationLayer.SCHEMA,
                    code=f"{SCHEMA_CODE_PREFIX}{error.validator}",
                    message=error.message,
                    path=_json_path(error.absolute_path),
                    details={"validator": str(error.validator)},
                )
            )
        return issues

    # ------------------------------------------------------------------
    # Layer 3: structural graph validation
    # ------------------------------------------------------------------

    def _validate_structure(
        self, nodes: List[Any], edges: List[Any]
    ) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        # Blocking: no nodes.
        if not nodes:
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    layer=ValidationLayer.STRUCTURE,
                    code=ValidationCode.NO_NODES.value,
                    message="Diagram has no nodes.",
                    path="$.nodes",
                )
            )

        node_ids: List[tuple] = []
        seen_node_ids: set = set()
        parent_by_id: Dict[str, tuple[str, int]] = {}
        positions: List[tuple] = []

        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            node_id = node.get("id")
            if isinstance(node_id, str):
                if node_id in seen_node_ids:
                    issues.append(
                        ValidationIssue(
                            severity=Severity.ERROR,
                            layer=ValidationLayer.STRUCTURE,
                            code=ValidationCode.DUPLICATE_NODE_ID.value,
                            message=f"Duplicate node id {node_id!r}.",
                            path=f"$.nodes[{index}].id",
                            details={"nodeId": node_id},
                        )
                    )
                seen_node_ids.add(node_id)
                node_ids.append((node_id, index))
                parent_id = node.get("parentId")
                if isinstance(parent_id, str):
                    parent_by_id[node_id] = (parent_id, index)

            # Empty required label.
            data = node.get("data")
            label = data.get("label") if isinstance(data, dict) else None
            if isinstance(label, str) and not label.strip():
                issues.append(
                    ValidationIssue(
                        severity=Severity.ERROR,
                        layer=ValidationLayer.STRUCTURE,
                        code=ValidationCode.EMPTY_NODE_LABEL.value,
                        message=f"Node {node_id!r} has an empty label.",
                        path=f"$.nodes[{index}].data.label",
                        details={"nodeId": node_id},
                    )
                )

            # Invalid / non-finite positions.
            position = node.get("position")
            if isinstance(position, dict):
                px, py = position.get("x"), position.get("y")
                if not (_is_finite_number(px) and _is_finite_number(py)):
                    issues.append(
                        ValidationIssue(
                            severity=Severity.ERROR,
                            layer=ValidationLayer.STRUCTURE,
                            code=ValidationCode.INVALID_POSITION.value,
                            message=f"Node {node_id!r} has a non-finite position.",
                            path=f"$.nodes[{index}].position",
                            details={"nodeId": node_id},
                        )
                    )
                elif _is_finite_number(px) and _is_finite_number(py):
                    parent_scope = node.get("parentId") if isinstance(node.get("parentId"), str) else None
                    positions.append((parent_scope, px, py, node_id, index))

            # Invalid sizes (when present).
            for dim in ("width", "height"):
                if dim in node:
                    value = node.get(dim)
                    if not (_is_finite_number(value) and value > 0):
                        issues.append(
                            ValidationIssue(
                                severity=Severity.ERROR,
                                layer=ValidationLayer.STRUCTURE,
                                code=ValidationCode.INVALID_SIZE.value,
                                message=(
                                    f"Node {node_id!r} has an invalid {dim} "
                                    f"({value!r}); must be a positive number."
                                ),
                                path=f"$.nodes[{index}].{dim}",
                                details={"nodeId": node_id},
                            )
                        )

        connected: set = set()
        for node_id, (parent_id, index) in parent_by_id.items():
            if parent_id not in seen_node_ids:
                issues.append(
                    ValidationIssue(
                        severity=Severity.ERROR,
                        layer=ValidationLayer.STRUCTURE,
                        code=ValidationCode.MISSING_NODE_PARENT.value,
                        message=f"Node {node_id!r} parentId references missing node {parent_id!r}.",
                        path=f"$.nodes[{index}].parentId",
                        details={"nodeId": node_id, "parentId": parent_id},
                    )
                )
            else:
                connected.update((node_id, parent_id))

        cycle_nodes = _nodes_reaching_parent_cycle(parent_by_id)
        for node_id, index in node_ids:
            if node_id in cycle_nodes:
                issues.append(
                    ValidationIssue(
                        severity=Severity.ERROR,
                        layer=ValidationLayer.STRUCTURE,
                        code=ValidationCode.CYCLIC_NODE_PARENT.value,
                        message=f"Node {node_id!r} belongs to a cyclic parentId chain.",
                        path=f"$.nodes[{index}].parentId",
                        details={"nodeId": node_id},
                    )
                )

        # Edge IDs and endpoint references.
        seen_edge_ids: set = set()
        for index, edge in enumerate(edges):
            if not isinstance(edge, dict):
                continue
            edge_id = edge.get("id")
            if isinstance(edge_id, str):
                if edge_id in seen_edge_ids:
                    issues.append(
                        ValidationIssue(
                            severity=Severity.ERROR,
                            layer=ValidationLayer.STRUCTURE,
                            code=ValidationCode.DUPLICATE_EDGE_ID.value,
                            message=f"Duplicate edge id {edge_id!r}.",
                            path=f"$.edges[{index}].id",
                            details={"edgeId": edge_id},
                        )
                    )
                seen_edge_ids.add(edge_id)

            for endpoint in ("source", "target"):
                ref = edge.get(endpoint)
                if isinstance(ref, str):
                    connected.add(ref)
                    if ref not in seen_node_ids:
                        issues.append(
                            ValidationIssue(
                                severity=Severity.ERROR,
                                layer=ValidationLayer.STRUCTURE,
                                code=ValidationCode(f"missing_edge_{endpoint}").value,
                                message=(
                                    f"Edge {edge_id!r} {endpoint} references "
                                    f"missing node {ref!r}."
                                ),
                                path=f"$.edges[{index}].{endpoint}",
                                details={"edgeId": edge_id, endpoint: ref},
                            )
                        )

        # Warnings.
        if nodes and not edges:
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    layer=ValidationLayer.STRUCTURE,
                    code=ValidationCode.NO_EDGES.value,
                    message="Diagram has nodes but no edges.",
                    path="$.edges",
                )
            )

        if len(nodes) > 1:
            for node_id, index in node_ids:
                if node_id not in connected:
                    issues.append(
                        ValidationIssue(
                            severity=Severity.WARNING,
                            layer=ValidationLayer.STRUCTURE,
                            code=ValidationCode.DISCONNECTED_NODE.value,
                            message=f"Node {node_id!r} is not connected by any edge.",
                            path=f"$.nodes[{index}].id",
                            details={"nodeId": node_id},
                        )
                    )

        # Overlapping positions.
        seen_positions: dict = {}
        for parent_scope, px, py, node_id, index in positions:
            key = (parent_scope, px, py)
            if key in seen_positions:
                issues.append(
                    ValidationIssue(
                        severity=Severity.WARNING,
                        layer=ValidationLayer.STRUCTURE,
                        code=ValidationCode.OVERLAPPING_POSITION.value,
                        message=(
                            f"Node {node_id!r} overlaps node "
                            f"{seen_positions[key]!r} at position ({px}, {py})."
                        ),
                        path=f"$.nodes[{index}].position",
                        details={"nodeId": node_id, "x": px, "y": py},
                    )
                )
            else:
                seen_positions[key] = node_id

        if len(nodes) > HIGH_NODE_COUNT:
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    layer=ValidationLayer.STRUCTURE,
                    code=ValidationCode.HIGH_NODE_COUNT.value,
                    message=f"Diagram has a high node count ({len(nodes)}).",
                    path="$.nodes",
                    details={"nodeCount": len(nodes)},
                )
            )
        if len(edges) > HIGH_EDGE_COUNT:
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    layer=ValidationLayer.STRUCTURE,
                    code=ValidationCode.HIGH_EDGE_COUNT.value,
                    message=f"Diagram has a high edge count ({len(edges)}).",
                    path="$.edges",
                    details={"edgeCount": len(edges)},
                )
            )

        return issues

    # ------------------------------------------------------------------
    # Layer 4: advisory blueprint/type-profile checks
    # ------------------------------------------------------------------

    def _validate_type_profile(
        self, diagram: Dict[str, Any], nodes: List[Any], edges: List[Any]
    ) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        diagram_type = diagram.get("diagramType")

        if not isinstance(diagram_type, str) or not self._type_service.is_supported(diagram_type):
            # Blocking: unsupported diagram type. (A missing/empty type is also
            # caught by the schema layer; this gives an advisory-layer signal.)
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    layer=ValidationLayer.BLUEPRINT,
                    code=ValidationCode.UNSUPPORTED_DIAGRAM_TYPE.value,
                    message=(
                        f"Unsupported diagramType {diagram_type!r}. Supported: "
                        f"{', '.join(self._type_service.list_valid_types())}."
                    ),
                    path="$.diagramType",
                    details={"diagramType": diagram_type},
                )
            )
            return issues

        profile = self._type_service.get_type_profile(diagram_type)

        # Advisory: blueprintKey mismatch.
        metadata = diagram.get("metadata")
        if isinstance(metadata, dict):
            blueprint_key = metadata.get("blueprintKey")
            if isinstance(blueprint_key, str) and blueprint_key:
                prefix = profile.expected_blueprint_key_prefix
                if not blueprint_key.startswith(prefix):
                    issues.append(
                        ValidationIssue(
                            severity=Severity.WARNING,
                            layer=ValidationLayer.BLUEPRINT,
                            code=ValidationCode.BLUEPRINT_KEY_MISMATCH.value,
                            message=(
                                f"metadata.blueprintKey {blueprint_key!r} does not "
                                f"match diagramType {diagram_type!r} (expected "
                                f"prefix {prefix!r})."
                            ),
                            path="$.metadata.blueprintKey",
                            details={
                                "blueprintKey": blueprint_key,
                                "diagramType": diagram_type,
                            },
                        )
                    )

        # Advisory: unexpected node type / semantic type.
        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            node_type = node.get("type")
            if isinstance(node_type, str) and node_type != profile.node_type:
                issues.append(
                    ValidationIssue(
                        severity=Severity.WARNING,
                        layer=ValidationLayer.BLUEPRINT,
                        code=ValidationCode.UNEXPECTED_NODE_TYPE.value,
                        message=(
                            f"Node {node.get('id')!r} type {node_type!r} is unexpected "
                            f"for {diagram_type!r} (expected {profile.node_type!r})."
                        ),
                        path=f"$.nodes[{index}].type",
                        details={"nodeType": node_type},
                    )
                )
            data = node.get("data")
            semantic = data.get("semanticType") if isinstance(data, dict) else None
            if isinstance(semantic, str) and semantic not in profile.allowed_node_semantic_types:
                issues.append(
                    ValidationIssue(
                        severity=Severity.WARNING,
                        layer=ValidationLayer.BLUEPRINT,
                        code=ValidationCode.UNEXPECTED_NODE_SEMANTIC_TYPE.value,
                        message=(
                            f"Node {node.get('id')!r} semanticType {semantic!r} is "
                            f"unexpected for {diagram_type!r}."
                        ),
                        path=f"$.nodes[{index}].data.semanticType",
                        details={"semanticType": semantic},
                    )
                )
        # Advisory: unexpected edge semantic type.
        for index, edge in enumerate(edges):
            if not isinstance(edge, dict):
                continue
            data = edge.get("data")
            semantic = data.get("semanticType") if isinstance(data, dict) else None
            if isinstance(semantic, str) and semantic not in profile.allowed_edge_semantic_types:
                issues.append(
                    ValidationIssue(
                        severity=Severity.WARNING,
                        layer=ValidationLayer.BLUEPRINT,
                        code=ValidationCode.UNEXPECTED_EDGE_SEMANTIC_TYPE.value,
                        message=(
                            f"Edge {edge.get('id')!r} semanticType {semantic!r} is "
                            f"unexpected for {diagram_type!r}."
                        ),
                        path=f"$.edges[{index}].data.semanticType",
                        details={"semanticType": semantic},
                    )
                )
        # Structural well-formedness (the per-type "structural critic", advisory). Surfaced
        # here for *every* diagram so all flows see it; only generation pipelines escalate
        # these to a block (Layer 6). For `custom`/unknown types the critic has no rules → nothing.
        for violation in check_structural_constraints(diagram, diagram_type):
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    layer=ValidationLayer.BLUEPRINT,
                    code=ValidationCode.STRUCTURAL_CONSTRAINT.value,
                    message=violation.message,
                    details={"rule": violation.rule},
                )
            )

        return issues

    # ------------------------------------------------------------------
    # Layer 5: basic render-readiness
    # ------------------------------------------------------------------

    def _validate_render_readiness(
        self, nodes: List[Any], edges: List[Any]
    ) -> List[ValidationIssue]:
        """Minimal render-readiness checks not already covered by Layer 3.

        Position, size, endpoint, and duplicate-id checks live in Layer 3, and
        "label must be a string" / "style must be an object" are already enforced
        by the schema layer. This layer adds render-quality guards aligned to how
        the renderer actually degrades a diagram: a long-label warning, a
        truncation-risk warning (the label will not fit its box even at the
        renderer's smallest font, so it would be ellipsized), and a redundant
        style-object guard (error) so a render-readiness signal exists even if the
        schema layer is bypassed.
        """
        issues: List[ValidationIssue] = []

        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            data = node.get("data")
            label = data.get("label") if isinstance(data, dict) else None
            if isinstance(label, str) and len(label) > LONG_LABEL_LENGTH:
                issues.append(
                    ValidationIssue(
                        severity=Severity.WARNING,
                        layer=ValidationLayer.RENDER_READINESS,
                        code=ValidationCode.LONG_LABEL.value,
                        message=(
                            f"Node {node.get('id')!r} label is very long "
                            f"({len(label)} chars)."
                        ),
                        path=f"$.nodes[{index}].data.label",
                    )
                )
            # Truncation risk: the label will not fit the node box even at the renderer's
            # smallest font, so the render would ellipsize it (a silent, non-recoverable
            # degradation). Uses the node's saved size or the per-type render fallback.
            if isinstance(label, str) and label.strip():
                semantic = data.get("semanticType") if isinstance(data, dict) else None
                default_w, default_h = DEFAULT_NODE_SIZES.get(semantic, FALLBACK_SIZE)
                raw_w, raw_h = node.get("width"), node.get("height")
                width = raw_w if _is_finite_number(raw_w) and raw_w > 0 else default_w
                height = raw_h if _is_finite_number(raw_h) and raw_h > 0 else default_h
                capacity = _label_capacity(width, height)
                if len(label.strip()) > capacity:
                    issues.append(
                        ValidationIssue(
                            severity=Severity.WARNING,
                            layer=ValidationLayer.RENDER_READINESS,
                            code=ValidationCode.LABEL_TRUNCATED.value,
                            message=(
                                f"Node {node.get('id')!r} label ({len(label.strip())} chars) will be "
                                f"truncated when rendered; its {int(width)}x{int(height)} box fits "
                                f"about {capacity} characters."
                            ),
                            path=f"$.nodes[{index}].data.label",
                            details={
                                "nodeId": node.get("id"),
                                "labelLength": len(label.strip()),
                                "capacity": capacity,
                            },
                        )
                    )
            if "style" in node and not isinstance(node.get("style"), dict):
                issues.append(
                    ValidationIssue(
                        severity=Severity.ERROR,
                        layer=ValidationLayer.RENDER_READINESS,
                        code=ValidationCode.INVALID_STYLE.value,
                        message=f"Node {node.get('id')!r} style must be an object.",
                        path=f"$.nodes[{index}].style",
                    )
                )

        for index, edge in enumerate(edges):
            if not isinstance(edge, dict):
                continue
            if "style" in edge and not isinstance(edge.get("style"), dict):
                issues.append(
                    ValidationIssue(
                        severity=Severity.ERROR,
                        layer=ValidationLayer.RENDER_READINESS,
                        code=ValidationCode.INVALID_STYLE.value,
                        message=f"Edge {edge.get('id')!r} style must be an object.",
                        path=f"$.edges[{index}].style",
                    )
                )

        return issues
