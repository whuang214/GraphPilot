"""Shared validated-write workflow for GraphPilot diagrams.

``DiagramPersistenceService`` is the single **validated-write funnel**: it orchestrates
the ``create`` (new diagram), ``create_exact`` (identity-bound creation), and
``save`` (overwrite) flows used by the browser-facing Django API
(``POST /api/diagrams/save``), the MCP ``diagram_generate_direct`` and
``diagram_generate_from_context`` tools, and the planned MCP ``diagram_update``
tool. It composes the existing shared services rather than
duplicating their logic:

- ``WorkspaceStorageService`` owns workspace resolution, path safety, and the atomic
  write (see ``docs/01-architecture/01-backend-architecture.md``).
- ``DiagramValidationService`` owns the deterministic validation layers.

Validation is enforced **here**, not inside ``WorkspaceStorageService`` (whose
``create_diagram``/``write_diagram`` stay low-level, path-safe primitives), so
the separation of concerns is preserved while no caller can persist an
unvalidated diagram.

Write rules (see ``docs/01-architecture/04-api-routes.md`` and the backend
architecture doc):

- validate before write (create or overwrite)
- ``save`` (overwrite): a diagram with blocking errors is rejected and the
  existing file is left unchanged (returned as a non-saved ``SaveOutcome``)
- ``create`` (new file): a diagram with blocking errors raises
  ``DiagramValidationError`` and nothing is written
- blueprint/type drift produces warnings only and never blocks a write
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from services.shared.workspace_storage_service import WorkspaceStorageService, DiagramNotFoundError
from services.diagrams.validation.diagram_validation_service import DiagramValidationService
from services.diagrams.validation.validation_contract import ValidationResult


class DiagramValidationError(Exception):
    """Raised by a validated write when the diagram fails validation.

    Carries the :class:`ValidationResult` so callers can surface the blocking
    issues. Raised by :meth:`DiagramPersistenceService.create` (the new-diagram path);
    :meth:`DiagramPersistenceService.save` instead returns a non-saved ``SaveOutcome`` so
    the browser API can render the validation errors in its response.
    """

    def __init__(self, validation: ValidationResult) -> None:
        self.validation = validation
        super().__init__(validation.summary)


@dataclass
class SaveOutcome:
    """Result of a :meth:`DiagramPersistenceService.save` call.

    ``saved`` is ``True`` only when validation passed and the file was written.
    When ``saved`` is ``False`` the existing file was left untouched and
    ``validation`` carries the blocking issues.
    """

    saved: bool
    resolved_path: Path
    validation: ValidationResult


@dataclass
class CreateOutcome:
    """Result of a successful :meth:`DiagramPersistenceService.create` call.

    ``create`` raises :class:`DiagramValidationError` when validation fails, so a
    returned ``CreateOutcome`` always represents a written file.
    """

    resolved_path: Path
    validation: ValidationResult


class DiagramPersistenceService:
    """Validates and overwrites an existing diagram in a workspace.

    Args:
        validation_service: Optional injected :class:`DiagramValidationService`.
            A default instance is created when omitted.
    """

    def __init__(self, validation_service: Optional[DiagramValidationService] = None) -> None:
        self._validation_service = validation_service or DiagramValidationService()

    def save(self, diagram_path: str, diagram: Dict[str, Any]) -> SaveOutcome:
        """Validate *diagram* and, if valid, overwrite the file at *diagram_path*.

        The workspace root is derived from *diagram_path* (the parent of the
        ``.graphpilot`` storage folder), so writes are constrained to that
        derived root.

        Args:
            diagram_path: Absolute path to the target ``<name>.gp.json``.
            diagram: The full updated GraphPilot diagram JSON.

        Returns:
            A :class:`SaveOutcome`. ``saved`` is ``False`` (no write performed)
            when validation reports blocking errors.

        Raises:
            WorkspaceResolutionError: if a workspace root cannot be derived from
                *diagram_path*.
            UnsafePathError: if the resolved path escapes the workspace root.
            TypeError: if *diagram* is not a dict.
            OSError: if the atomic write fails for an I/O reason.
        """
        if not isinstance(diagram, dict):
            raise TypeError(f"diagram must be a dict; got {type(diagram).__name__}.")

        file_service = WorkspaceStorageService.for_diagram_path(diagram_path)
        resolved = file_service.resolve_safe_path(diagram_path)

        result = self._validation_service.validate(diagram)
        if not result.valid:
            return SaveOutcome(saved=False, resolved_path=resolved, validation=result)
        if not resolved.is_file():
            raise DiagramNotFoundError(f"Diagram file not found: {resolved}")

        file_service.write_diagram(resolved, diagram)
        return SaveOutcome(saved=True, resolved_path=resolved, validation=result)

    def create(
        self,
        workspace_dir: str,
        name: str,
        diagram: Dict[str, Any],
        *,
        deduplicate: bool = True,
    ) -> CreateOutcome:
        """Validate *diagram* and, if valid, write it as a new named file.

        The single **validated-write** path for new diagrams: validation is
        enforced here rather than in ``WorkspaceStorageService``, so no caller can
        persist an unvalidated diagram. Path safety and the atomic write stay in
        ``WorkspaceStorageService`` (``create_diagram`` sanitizes *name* and, when
        *deduplicate* is set, avoids clobbering an existing file).

        Args:
            workspace_dir: The workspace root the new diagram is written under.
            name: The desired diagram name (sanitized into the file stem).
            diagram: The full GraphPilot diagram JSON.
            deduplicate: When ``True`` (default) a ``-2``/``-3`` suffix avoids a
                name collision; ``False`` overwrites a same-named file.

        Returns:
            A :class:`CreateOutcome` carrying the resolved written path.

        Raises:
            DiagramValidationError: if the diagram fails validation (nothing is
                written).
            TypeError: if *diagram* is not a dict.
            OSError: if the atomic write fails for an I/O reason.
        """
        if not isinstance(diagram, dict):
            raise TypeError(f"diagram must be a dict; got {type(diagram).__name__}.")

        result = self._validation_service.validate(diagram)
        if not result.valid:
            raise DiagramValidationError(result)

        file_service = WorkspaceStorageService(workspace_dir)
        resolved = file_service.create_diagram(name, diagram, deduplicate=deduplicate)
        return CreateOutcome(resolved_path=resolved, validation=result)

    def create_exact(
        self,
        workspace_dir: str,
        name: str,
        diagram: Dict[str, Any],
    ) -> CreateOutcome:
        """Validate and exclusively create one exact canonical diagram target.

        Unlike :meth:`create`, this identity-aware publication path never sanitizes to
        a different stem, deduplicates, or overwrites. A concurrent or pre-existing
        target raises :class:`FileExistsError` from the storage primitive.
        """
        if not isinstance(diagram, dict):
            raise TypeError(f"diagram must be a dict; got {type(diagram).__name__}.")

        result = self._validation_service.validate(diagram)
        if not result.valid:
            raise DiagramValidationError(result)

        file_service = WorkspaceStorageService(workspace_dir)
        if not isinstance(name, str) or file_service.sanitize_name(name) != name:
            raise ValueError("name must be an exact canonical diagram stem.")
        resolved = file_service.resolve_safe_path(file_service.diagram_file_path(name))
        written = file_service.write_json_object_exclusive(resolved, diagram)
        return CreateOutcome(resolved_path=written, validation=result)
