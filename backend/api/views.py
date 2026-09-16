import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.diagram_contract import (
    DiagramLoadResponse,
    DiagramSaveResponse,
)
from services.shared.operation_problem import operation_problem
from services.diagrams.persistence.diagram_persistence_service import DiagramPersistenceService
from services.shared.workspace_storage_service import (
    WorkspaceStorageService,
    DiagramNotFoundError,
    InvalidDiagramJSONError,
    UnsafePathError,
    WorkspaceResolutionError,
)
from services.diagrams.rendering.diagram_render_service import (
    DiagramRenderService,
    DiagramRenderServiceError,
)
from services.diagrams.validation.diagram_validation_service import DiagramValidationService
from services.shared.diagram_type_service import DiagramTypeService
from services.diagrams.validation.validation_contract import Severity

logger = logging.getLogger(__name__)


@api_view(['GET'])
def health(_request):
    return Response({'status': 'ok'})


# Shared validation + persistence services. The validation service caches the
# compiled schema validator, so we build it once and inject it into the
# persistence service; both the save and validate routes then reuse that one
# compiled validator. Mirrors the MCP server pattern.
_validation_service = DiagramValidationService()
_persistence_service = DiagramPersistenceService(validation_service=_validation_service)

# Shared, stateless render service (mirrors the MCP server pattern).
_render_service = DiagramRenderService()

# Shared type registry accessor (for the save/validate diagramType reconcile below).
_type_service = DiagramTypeService()


def _error(code, message, http_status, *, details=None, retryable=None):
    problem = operation_problem(code, message, details=details, retryable=retryable)
    return Response({"error": problem.to_dict()}, status=http_status)


def _stamp_custom_authoring(diagram):
    """Record that a UI save last touched this diagram (metadata.authoring = "custom").

    This marker is now **informational provenance** only — strict-vs-freeform is decided by
    ``diagramType`` (see ``_reconcile_diagram_type``), not by ``authoring``. Only stamps when
    metadata is already the required object; a missing/invalid metadata is left untouched so
    validation still rejects it. Shared by the save and validate routes."""
    metadata = diagram.get('metadata')
    if isinstance(metadata, dict):
        metadata['authoring'] = 'custom'
    return diagram


def _reconcile_diagram_type(diagram):
    """Flip a UI-edited diagram to the universal ``custom`` type when it uses elements outside
    its declared type's vocabulary — the live half of the freeform model (``diagramType`` is the
    strict/freeform switch; see ``00-diagram-json-schema.md``). A diagram that still fits its
    type keeps it; a ``custom`` board stays ``custom``. Shared by the save and validate routes."""
    diagram_type = diagram.get('diagramType')
    if isinstance(diagram_type, str) and diagram_type != _type_service.CUSTOM_TYPE:
        if not _type_service.conforms_to_type(diagram.get('nodes'), diagram.get('edges'), diagram_type):
            diagram['diagramType'] = _type_service.CUSTOM_TYPE
    return diagram


@api_view(['GET'])
def diagram_load(request):
    """Load an existing saved diagram for the visual editor.

    Thin handler over ``WorkspaceStorageService``: it derives the workspace root from
    the absolute ``path`` (the parent of the ``.graphpilot`` storage folder),
    loads the diagram, and returns it. All business rules (path safety, file
    access) stay in the shared service.
    """
    path = (request.query_params.get('path') or '').strip()
    if not path:
        return _error('missing_path', 'Query parameter "path" is required.', status.HTTP_400_BAD_REQUEST)
    try:
        service = WorkspaceStorageService.for_diagram_path(path)
        resolved = service.resolve_safe_path(path)
        diagram = service.load_diagram(resolved)
        revision = service.diagram_revision(resolved)
    except WorkspaceResolutionError as exc:
        return _error('invalid_path', str(exc), status.HTTP_400_BAD_REQUEST)
    except UnsafePathError as exc:
        # Defensive: the workspace root is derived from the resolved path, so a
        # path that escapes it is not normally reachable through this route.
        return _error('unsafe_path', str(exc), status.HTTP_400_BAD_REQUEST)
    except DiagramNotFoundError as exc:
        return _error('not_found', str(exc), status.HTTP_404_NOT_FOUND)
    except InvalidDiagramJSONError as exc:
        return _error('invalid_json', str(exc), status.HTTP_422_UNPROCESSABLE_ENTITY)
    except OSError as exc:
        # Catch-all for residual I/O errors (e.g. permission denied) so the
        # response stays a clean error shape rather than an unhandled 500.
        logger.warning("diagram_load failed for %r: %s", path, exc, exc_info=True)
        return _error('load_failed', 'Could not read the diagram file.', status.HTTP_422_UNPROCESSABLE_ENTITY)
    return Response(
        DiagramLoadResponse(
            diagram_path=str(resolved),
            diagram=diagram,
            revision=revision,
        ).to_dict()
    )


@api_view(['POST'])
def diagram_save(request):
    """Validate and overwrite an existing diagram from the visual editor.

    Thin handler over ``DiagramPersistenceService``: it derives the workspace root from
    the absolute ``diagramPath`` and saves only when validation passes. Blocking
    validation errors return the save-failure shape and leave the file
    unchanged; blueprint/type drift produces warnings only and does not block.
    """
    data = request.data if isinstance(request.data, dict) else {}
    raw_path = data.get('diagramPath')
    path = raw_path.strip() if isinstance(raw_path, str) else ''
    diagram = data.get('diagram')
    expected_revision = data.get('expectedRevision')

    if not path:
        return _error('missing_path', 'Field "diagramPath" is required.', status.HTTP_400_BAD_REQUEST)
    if not isinstance(diagram, dict):
        return _error('invalid_diagram', 'Field "diagram" must be a JSON object.', status.HTTP_400_BAD_REQUEST)

    try:
        file_service = WorkspaceStorageService.for_diagram_path(path)
        resolved = file_service.resolve_safe_path(path)
        if isinstance(expected_revision, str) and expected_revision and file_service.diagram_revision(resolved) != expected_revision:
            return _error(
                'source_changed',
                'The diagram changed on disk after it was loaded. Reload or explicitly resolve the conflict before saving.',
                status.HTTP_409_CONFLICT,
            )
    except WorkspaceResolutionError as exc:
        return _error('invalid_path', str(exc), status.HTTP_400_BAD_REQUEST)
    except UnsafePathError as exc:
        return _error('unsafe_path', str(exc), status.HTTP_400_BAD_REQUEST)
    except DiagramNotFoundError as exc:
        return _error('not_found', str(exc), status.HTTP_404_NOT_FOUND)
    except OSError as exc:
        logger.warning("diagram_save revision check failed for %r: %s", path, exc, exc_info=True)
        return _error('save_failed', 'Could not read the current diagram revision.', status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Reconcile the type first (flip to `custom` if the board went off its type's vocabulary),
    # then record the UI touch as informational authoring. Strictness follows diagramType; MCP
    # generate/update produce a concrete type. `metadata` is open, so this needs no schema change.
    _reconcile_diagram_type(diagram)
    _stamp_custom_authoring(diagram)

    try:
        outcome = _persistence_service.save(path, diagram)
    except WorkspaceResolutionError as exc:
        return _error('invalid_path', str(exc), status.HTTP_400_BAD_REQUEST)
    except UnsafePathError as exc:
        return _error('unsafe_path', str(exc), status.HTTP_400_BAD_REQUEST)
    except DiagramNotFoundError as exc:
        return _error('not_found', str(exc), status.HTTP_404_NOT_FOUND)
    except OSError as exc:
        # Catch-all for residual I/O errors (e.g. permission denied) so the
        # response stays a clean error shape rather than an unhandled 500.
        logger.warning("diagram_save failed for %r: %s", path, exc, exc_info=True)
        return _error('save_failed', 'Could not write the diagram file.', status.HTTP_422_UNPROCESSABLE_ENTITY)

    if not outcome.saved:
        issues = [
            {"code": issue.code, "message": issue.message, "path": issue.path}
            for issue in outcome.validation.issues
            if issue.severity == Severity.ERROR
        ]
        return _error(
            'validation_failed',
            'Diagram validation failed. The existing file was not overwritten.',
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"issues": issues},
        )

    # Render-on-save: write the sibling <name>.svg beside the saved JSON. Best-effort
    # — the save already succeeded, so a render failure returns a nonfatal warning
    # and omits svgPath rather than failing the request.
    svg_path = None
    warning = None
    try:
        svg_path = str(_render_service.render(outcome.resolved_path))
    except (DiagramRenderServiceError, OSError) as exc:
        logger.warning("render-on-save failed for %s: %s", outcome.resolved_path, exc)
        # Ask the renderer where it would have written, rather than re-deriving it. This
        # string is the user's only pointer to the file that is now missing, and it agreed
        # with the renderer by coincidence rather than by construction.
        intended_svg = _render_service.artifact_sibling(outcome.resolved_path, ".svg")
        warning = operation_problem(
            "render_failed",
            "The diagram was saved, but SVG rendering failed.",
            details={
                "diagramPath": str(outcome.resolved_path),
                "intendedSvgPath": str(intended_svg),
            },
        )

    return Response(
        DiagramSaveResponse(
            saved=True,
            diagram_path=str(outcome.resolved_path),
            diagram=diagram,
            revision=WorkspaceStorageService.for_diagram_path(outcome.resolved_path).diagram_revision(outcome.resolved_path),
            svg_path=svg_path,
            warning=warning,
        ).to_dict()
    )


@api_view(['GET'])
def diagram_list(request):
    """List diagrams stored under a workspace's ``.graphpilot/diagrams/`` folder.

    Additive, read-only companion to ``diagram_load`` backing the workspace browser:
    it derives the workspace from a ``path`` within it
    (any diagram path under that workspace) and returns the available named
    diagrams. Path safety stays in ``WorkspaceStorageService``; no files are written.
    """
    path = (request.query_params.get('path') or '').strip()
    if not path:
        return _error('missing_path', 'Query parameter "path" is required.', status.HTTP_400_BAD_REQUEST)
    try:
        service = WorkspaceStorageService.for_diagram_path(path)
        diagrams = [
            {'name': name, 'path': str(service.diagram_file_path(name))}
            for name in service.list_diagram_names()
        ]
    except WorkspaceResolutionError as exc:
        return _error('invalid_path', str(exc), status.HTTP_400_BAD_REQUEST)
    except OSError as exc:
        logger.warning("diagram_list failed for %r: %s", path, exc, exc_info=True)
        return _error('list_failed', 'Could not list diagrams.', status.HTTP_422_UNPROCESSABLE_ENTITY)
    return Response({'diagrams': diagrams})


@api_view(['POST'])
def diagram_validate(request):
    """Validate diagram JSON with no write and no workspace resolution.

    Path-free companion used by the editor's "open any file" flow: a diagram opened
    from anywhere on disk (File System Access API, outside
    a ``.graphpilot`` workspace) is validated here before the browser writes it
    via a file handle. Applies the same ``metadata.authoring = "custom"``
    normalization as the save route and returns the normalized diagram so the
    client writes a single canonical form.
    """
    data = request.data if isinstance(request.data, dict) else {}
    diagram = data.get('diagram')
    if not isinstance(diagram, dict):
        return _error('invalid_diagram', 'Field "diagram" must be a JSON object.', status.HTTP_400_BAD_REQUEST)

    _reconcile_diagram_type(diagram)
    _stamp_custom_authoring(diagram)
    try:
        result = _validation_service.validate(diagram)
    except (FileNotFoundError, OSError, ValueError) as exc:
        # Defensive: a missing/invalid bundled schema would otherwise crash as a 500.
        # Mirrors the MCP diagram_validate tool. (The success response shape differs by
        # design: this route returns the normalized diagram for the open-any-file flow.)
        logger.error("diagram_validate unavailable: %s", exc, exc_info=True)
        return _error('validation_unavailable', str(exc), status.HTTP_422_UNPROCESSABLE_ENTITY)
    errors = [
        {'code': issue.code, 'message': issue.message, 'path': issue.path}
        for issue in result.issues
        if issue.severity == Severity.ERROR
    ]
    return Response({'valid': result.valid, 'validationErrors': errors, 'diagram': diagram})


@api_view(['POST'])
def diagram_render(request):
    """Render inline diagram JSON to an SVG string (path-free, no write).

    Verification companion to the MCP ``diagram_render`` tool, used by the editor's
    "Preview render" action: the browser posts the canonical JSON it would save and
    gets back the backend SVG, so the server-rendered shapes can be compared
    against the React Flow canvas without writing any file. Backed by
    ``DiagramRenderService.to_svg`` (pure; no path safety needed since nothing is
    read from or written to disk).
    """
    data = request.data if isinstance(request.data, dict) else {}
    diagram = data.get('diagram')
    if not isinstance(diagram, dict):
        return _error('invalid_diagram', 'Field "diagram" must be a JSON object.', status.HTTP_400_BAD_REQUEST)
    try:
        svg = _render_service.to_svg(diagram)
    except DiagramRenderServiceError as exc:
        return _error('render_failed', str(exc), status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception as exc:  # noqa: BLE001 — unvalidated path-free JSON; never 500
        # This endpoint renders unvalidated, path-free JSON (e.g. malformed node
        # entries), so any unexpected error is treated as bad input rather than a 500.
        logger.warning("diagram_render (inline) failed: %s", exc, exc_info=True)
        return _error('render_failed', 'Could not render the diagram.', status.HTTP_422_UNPROCESSABLE_ENTITY)
    return Response({'svg': svg})
