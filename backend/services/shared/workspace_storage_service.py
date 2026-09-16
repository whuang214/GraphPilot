"""Safe low-level access to diagram and context artifacts in one workspace.

All GraphPilot file reads and writes that touch ``.graphpilot/`` go through
this service. It owns workspace containment, canonical artifact paths, bounded
reads, naming, and sibling-temp atomic writes. Schema, lifecycle, fingerprint,
and conflict policy stay in higher-level services.

New diagrams and their derived artifacts live under ``.graphpilot/diagrams/``.
Explicit legacy flat diagram paths remain readable and writable so existing
files are not stranded, but allocation and listing use only the canonical root.

Path safety uses ``Path.resolve()`` + ``Path.is_relative_to()`` so symlinks and
``..`` traversal cannot escape the workspace.
"""

import hashlib
import json
import logging
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, Union

from django.conf import settings

logger = logging.getLogger(__name__)

#: Ceiling on a single ``.gp.json``.
#:
#: The largest of the 61 diagrams this repository ships is 43 KB, and the layout engine
#: refuses more than 256 nodes, so a legitimate diagram cannot approach this. 8 MB is
#: deliberately far above anything real and far below "read an arbitrary file into
#: memory": it exists to stop a hostile or truncated file, not to constrain authors.
#: Sits between ``MAX_DRAFT_BYTES`` (2 MB, one diagram's semantics) and the 4 MB
#: evidence-file bound, because a diagram carries both plus geometry.
MAX_DIAGRAM_BYTES = 8 * 1024 * 1024


def _reject_non_finite_json_constant(value: str):
    raise ValueError(f"Invalid JSON numeric constant: {value}")


def _normalize_resolved_path(path: Path) -> Path:
    if os.name != "nt":
        return path
    value = str(path)
    if value.startswith("\\\\?\\UNC\\"):
        return Path("\\\\" + value[8:])
    if re.match(r"^\\\\\?\\[A-Za-z]:\\", value):
        return Path(value[4:])
    return path


def os_path(path: Path) -> Path:
    """Return the form a filesystem call should use for an already-safe path.

    Windows applies the 260-character MAX_PATH limit to ordinary paths, and a
    workspace nested inside evaluation evidence exceeds it: the run that found
    this needed 266 characters before writing a single file. The extended-length
    prefix lifts the limit for the syscall only.

    It is deliberately not applied anywhere else. ``_normalize_resolved_path``
    strips the prefix back off precisely so stored paths, digests, and
    ``is_relative_to`` comparisons stay in one canonical form; this is the
    inverse, used at the boundary and never retained.
    """
    if os.name != "nt":
        return path
    value = str(path)
    if value.startswith("\\\\?\\"):
        return path
    if value.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + value[2:])
    if re.match(r"^[A-Za-z]:\\", value):
        return Path("\\\\?\\" + value)
    return path


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class WorkspaceStorageError(Exception):
    """Base exception for workspace storage failures."""


class UnsafePathError(WorkspaceStorageError):
    """Raised when a resolved path escapes the workspace root."""


class DiagramNotFoundError(WorkspaceStorageError):
    """Raised when the expected ``<name>.gp.json`` file does not exist."""


class InvalidDiagramJSONError(WorkspaceStorageError):
    """Raised when a diagram file contains invalid or non-object JSON."""


class WorkspaceResolutionError(WorkspaceStorageError):
    """Raised when a workspace root cannot be derived from an artifact path."""


class ArtifactNotFoundError(WorkspaceStorageError):
    """Raised when a requested workspace artifact is not a regular file."""


class ArtifactTooLargeError(WorkspaceStorageError):
    """Raised when a workspace artifact exceeds its decoded-file byte limit."""


class InvalidJSONFileError(WorkspaceStorageError):
    """Raised when a workspace artifact is not a standard JSON object."""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class WorkspaceStorageService:
    """Safe workspace file access for GraphPilot diagrams.

    Args:
        workspace_dir: Absolute path to the user project workspace.  All
            file operations are constrained to stay inside this directory.

    Raises:
        ValueError: if *workspace_dir* is empty or whitespace.
    """

    def __init__(self, workspace_dir: Union[str, Path]) -> None:
        ws = str(workspace_dir).strip()
        if not ws:
            raise ValueError("workspace_dir must not be empty.")
        self._workspace_root = _normalize_resolved_path(Path(ws).resolve())

    # ------------------------------------------------------------------
    # Workspace resolution
    # ------------------------------------------------------------------

    @classmethod
    def for_diagram_path(cls, diagram_path: Union[str, Path]) -> "WorkspaceStorageService":
        """Build a service whose workspace root is derived from *diagram_path*.

        The workspace root is the parent of the ``.graphpilot`` storage folder
        found among the path's ancestors. This supports the browser-facing API
        flow, where the request carries only ``diagramPath`` (no explicit
        ``workspaceDir``) because the IDE-generated ``editUrl`` only carries a
        path. See ``docs/01-architecture/01-backend-architecture.md`` and the
        storage/workspace decisions in
        ``docs/02-design-and-features/decision-decisions.md``.

        The storage folder is matched as a single path segment, and the
        *nearest* (deepest) ``.graphpilot`` ancestor wins. This assumes
        ``GRAPHPILOT_STORAGE_DIR`` is a single segment (the default
        ``.graphpilot``); a nested value would not be matched here.

        **A diagram outside any storage folder is opened from its own directory.**
        Requiring a ``.graphpilot`` ancestor refused every ``.gp.json`` the product
        itself ships — the training and answer examples under
        ``assets/blueprints/<type>/examples/`` are ordinary diagrams in ordinary folders,
        and an ``editUrl`` pointing at one came back ``invalid_path``. A path is not
        unsafe because of where it sits; the containment that matters is applied
        afterwards by :meth:`resolve_safe_path`, which keeps every read and write inside
        whichever root this returns. For a loose file that root is the file's own folder,
        so opening one grants exactly the directory it lives in and nothing above it.

        Raises:
            WorkspaceResolutionError: if *diagram_path* is empty.
        """
        raw = str(diagram_path).strip()
        if not raw:
            raise WorkspaceResolutionError("diagramPath must not be empty.")
        storage_name = getattr(settings, "GRAPHPILOT_STORAGE_DIR", ".graphpilot")
        resolved = Path(raw).resolve()
        for ancestor in resolved.parents:
            if ancestor.name == storage_name:
                return cls(ancestor.parent)
        # A directory is already a root; a file's root is the folder holding it. Checked
        # on disk rather than by suffix, because a folder may carry a dot in its name.
        return cls(resolved if resolved.is_dir() else resolved.parent)

    # ------------------------------------------------------------------
    # Path safety
    # ------------------------------------------------------------------

    def resolve_safe_path(self, path: Union[str, Path]) -> Path:
        """Resolve *path* and verify it stays inside the workspace root.

        Relative paths are resolved relative to the workspace root.

        Returns:
            The resolved absolute ``Path``.

        Raises:
            UnsafePathError: if the resolved path escapes the workspace.
        """
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = self._workspace_root / candidate
        resolved = _normalize_resolved_path(candidate.resolve())
        if not resolved.is_relative_to(self._workspace_root):
            raise UnsafePathError(
                f"Path {path!r} resolves to {resolved} which is outside the "
                f"workspace root {self._workspace_root}."
            )
        return resolved

    # ------------------------------------------------------------------
    # Storage convention
    # ------------------------------------------------------------------

    def storage_root(self) -> Path:
        """Return the safely resolved ``.graphpilot/`` directory inside the workspace."""
        storage_dir = getattr(settings, "GRAPHPILOT_STORAGE_DIR", ".graphpilot")
        return self.resolve_safe_path(self._workspace_root / storage_dir)

    def diagrams_root(self) -> Path:
        """Return the canonical directory for diagrams and derived artifacts."""
        return self.resolve_safe_path(self.storage_root() / "diagrams")

    def drafts_root(self) -> Path:
        """Return the directory holding the draft each diagram was built from.

        A traceline, not an input. `diagram_create` writes the accepted draft here beside
        the diagram it produced, so that when a diagram turns out to be wrong there is a
        record of what the host actually claimed: which elements it said existed, what it
        cited, and what it admitted it was unsure of.

        This is a different question from the one `D1` answered. `D1` decided what goes
        *inside* the `.gp.json`, and the answer is still nothing — the diagram carries
        evidence and per-element assurance, never the host's prose.
        """
        return self.resolve_safe_path(self.storage_root() / "drafts")

    @staticmethod
    def diagram_extension() -> str:
        """Return the canonical diagram file extension (``.gp.json``).

        Static because the answer does not depend on a workspace, and the callers that
        most needed it had no storage instance to hand: `DiagramRenderService`'s
        `artifact_sibling` and the update service's history naming both spelled the
        suffix out again rather than construct one. Same rule, three spellings -- the
        shape `a5` found behind every drift it chased.
        """
        return ".gp.json"

    def default_diagram_name(self) -> str:
        """Return the built-in fallback diagram name."""
        return "diagram"

    def sanitize_name(self, raw: str) -> str:
        """Turn an arbitrary desired name into a safe filename stem (a slug).

        Lowercases, replaces any run of non-alphanumeric characters with a
        single hyphen, trims hyphens, and caps the length. A trailing diagram
        extension (e.g. ``.gp.json``) is stripped if the caller included one.
        Falls back to :meth:`default_diagram_name` when nothing usable remains.
        """
        base = str(raw).strip().lower()
        ext = self.diagram_extension()
        if base.endswith(ext):
            base = base[: -len(ext)]
        base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
        base = base[:64].strip("-")
        return base or self.default_diagram_name()

    def diagram_file_path(self, name: str) -> Path:
        """Return the canonical diagram path for a sanitized *name*."""
        safe = self.sanitize_name(name)
        return self.diagrams_root() / f"{safe}{self.diagram_extension()}"

    def _resolve_direct_artifact(
        self,
        path: Union[str, Path],
        root: Path,
        suffix: str,
    ) -> Path:
        safe = self.resolve_safe_path(path)
        if safe.parent != root or not safe.name.endswith(suffix) or safe.name == suffix:
            raise UnsafePathError(
                f"Artifact path must be a direct {suffix!r} file beneath {root}: {safe}"
            )
        return safe

    def list_diagram_names(self) -> list[str]:
        """Return sorted names of canonical ``*.gp.json`` diagram files.

        Legacy flat files are intentionally not listed or newly allocated.
        """
        root = self.diagrams_root()
        if not os_path(root).exists() or not os_path(root).is_dir():
            return []
        ext = self.diagram_extension()
        names = []
        try:
            for entry in os_path(root).iterdir():
                if entry.is_file() and entry.name.endswith(ext):
                    names.append(entry.name[: -len(ext)])
        except OSError:
            # e.g. permission denied on the storage folder — treat as empty rather
            # than crashing the load/list flows that call this.
            #
            # Empty is still the right answer for the caller; silence was not. An
            # unreadable folder and an empty one returned the identical `[]` with nothing
            # written anywhere, so a person whose diagrams were merely unreachable was
            # told they had none, and had no thread to pull. The log is the thread.
            logger.warning(
                "Could not list diagrams in %s; reporting none. The folder exists but "
                "could not be read — check permissions.", root, exc_info=True,
            )
            return []
        return sorted(names)

    def diagram_revision(self, path: Union[str, Path]) -> str:
        """Return an opaque content revision for a safely resolved diagram file."""
        safe = self.resolve_safe_path(path)
        if not os_path(safe).is_file():
            raise DiagramNotFoundError(f"Diagram file not found: {safe}")
        return hashlib.sha256(os_path(safe).read_bytes()).hexdigest()

    def unique_name(self, desired: str) -> str:
        """Return a collision-free sanitized name within ``.graphpilot/diagrams/``.

        Sanitizes *desired* and, if a diagram with that name already exists,
        appends a ``-2``, ``-3``, ... suffix until the name is free.
        """
        base = self.sanitize_name(desired)
        existing = set(self.list_diagram_names())
        if base not in existing:
            return base
        n = 2
        while f"{base}-{n}" in existing:
            n += 1
        return f"{base}-{n}"

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def read_bytes(self, path: Union[str, Path], *, max_bytes: int) -> bytes:
        """Read at most *max_bytes* from a regular workspace file."""
        if max_bytes < 0:
            raise ValueError("max_bytes must not be negative.")
        safe = self.resolve_safe_path(path)
        if not os_path(safe).is_file():
            raise ArtifactNotFoundError(f"Artifact file not found: {safe}")
        with os_path(safe).open("rb") as stream:
            data = stream.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ArtifactTooLargeError(
                f"Artifact exceeds the {max_bytes}-byte limit: {safe}"
            )
        return data

    def read_text(self, path: Union[str, Path], *, max_bytes: int) -> str:
        """Read a bounded workspace file as strict UTF-8 text."""
        return self.read_bytes(path, max_bytes=max_bytes).decode("utf-8")

    def read_json_object(
        self,
        path: Union[str, Path],
        *,
        max_bytes: int,
    ) -> Dict[str, Any]:
        """Read a bounded standard-JSON file whose top-level value is an object."""
        safe = self.resolve_safe_path(path)
        try:
            data = json.loads(
                self.read_text(safe, max_bytes=max_bytes),
                parse_constant=_reject_non_finite_json_constant,
            )
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            raise InvalidJSONFileError(f"Artifact contains invalid JSON: {safe}") from exc
        if not isinstance(data, dict):
            raise InvalidJSONFileError(
                f"Artifact must contain a JSON object; got {type(data).__name__}: {safe}"
            )
        return data

    def load_diagram(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load and parse a diagram JSON file.

        Bounded, like every other read here. This one was not: every neighbour takes a
        ``max_bytes`` and this streamed straight into ``json.load``, so a 40 MB
        ``.gp.json`` was read whole in 0.06s while ``read_json_object`` refused the same
        file. A diagram is opened from wherever a caller points, including a repository
        somebody else wrote, and the asymmetry meant the one entry point that takes an
        untrusted file was the one with no bound.

        Args:
            path: Absolute or workspace-relative path to the diagram file.

        Returns:
            The parsed diagram as a dict.

        Raises:
            UnsafePathError: if the path escapes the workspace.
            DiagramNotFoundError: if the path does not point to a regular file.
            ArtifactTooLargeError: if the file exceeds ``MAX_DIAGRAM_BYTES``.
            InvalidDiagramJSONError: if the file contains invalid JSON or
                the top-level value is not an object.
        """
        safe = self.resolve_safe_path(path)
        # ``is_file`` (not ``exists``) so a directory path maps cleanly to
        # DiagramNotFoundError instead of failing later in ``open()``.
        if not os_path(safe).is_file():
            raise DiagramNotFoundError(f"Diagram file not found: {safe}")
        try:
            data = json.loads(
                self.read_text(safe, max_bytes=MAX_DIAGRAM_BYTES),
                parse_constant=_reject_non_finite_json_constant,
            )
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            raise InvalidDiagramJSONError(
                f"Diagram file contains invalid JSON: {safe}"
            ) from exc
        if not isinstance(data, dict):
            raise InvalidDiagramJSONError(
                f"Diagram file must contain a JSON object; got {type(data).__name__}: {safe}"
            )
        return data

    # ------------------------------------------------------------------
    # Write helpers (raw safe-write primitives; no diagram validation)
    # ------------------------------------------------------------------

    def ensure_storage_root(self) -> Path:
        """Create the ``.graphpilot/`` storage folder if it does not exist.

        The folder is created only if it lies safely within the workspace.

        Returns:
            The ``Path`` to the storage root.

        Raises:
            UnsafePathError: if the resolved folder escapes the workspace.
        """
        root = self.storage_root()
        # Safety check — storage_root is always inside workspace, but validate
        # explicitly so any future override or misconfiguration is caught early.
        self.resolve_safe_path(root)
        os_path(root).mkdir(parents=True, exist_ok=True)
        return root

    def serialize_json_object(self, value: Dict[str, Any]) -> bytes:
        """Serialize a JSON object using the canonical persisted-file formatting."""
        if not isinstance(value, dict):
            raise TypeError(f"value must be a dict; got {type(value).__name__}.")
        text = json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
        )
        return f"{text}\n".encode("utf-8")

    def write_json_object(
        self,
        path: Union[str, Path],
        value: Dict[str, Any],
    ) -> Path:
        """Atomically write a JSON object with the canonical persisted formatting."""
        return self.write_bytes(path, self.serialize_json_object(value))

    def write_json_object_exclusive(
        self,
        path: Union[str, Path],
        value: Dict[str, Any],
    ) -> Path:
        """Create a canonical JSON object file without replacing an existing path."""
        safe_target = self.resolve_safe_path(path)
        os_path(safe_target.parent).mkdir(parents=True, exist_ok=True)
        data = self.serialize_json_object(value)
        descriptor = os.open(os_path(safe_target), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(data)
        except Exception:
            try:
                safe_target.unlink()
            except OSError:
                pass
            raise
        return safe_target

    def is_existing_file(self, path: Union[str, Path]) -> bool:
        """Whether a safe path is an existing regular file.

        On Windows hosts still enforcing the legacy 260-character limit,
        ``Path.is_file()`` answers False for an overlong path whether or not the
        file is there. Long-path-aware hosts may accept the ordinary path, but the
        boundary remains the portable contract. This asks through the same form
        the writes use, so the answer is about the file rather than its name length.
        """
        return os_path(self.resolve_safe_path(path)).is_file()

    def write_bytes_exclusive(self, path: Union[str, Path], data: bytes) -> Path:
        """Create a binary file without replacing an existing path."""
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f"data must be bytes; got {type(data).__name__}.")
        safe_target = self.resolve_safe_path(path)
        os_path(safe_target.parent).mkdir(parents=True, exist_ok=True)
        descriptor = os.open(os_path(safe_target), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(data)
        except Exception:
            try:
                safe_target.unlink()
            except OSError:
                pass
            raise
        return safe_target

    def remove_file(self, path: Union[str, Path]) -> bool:
        """Remove a safely resolved regular file and report whether it existed."""
        safe = self.resolve_safe_path(path)
        try:
            safe.unlink()
        except FileNotFoundError:
            return False
        return True

    def create_diagram(
        self,
        name: str,
        diagram: Dict[str, Any],
        *,
        deduplicate: bool = True,
    ) -> Path:
        """Write *diagram* under ``.graphpilot/diagrams/`` (path-safe, atomic).

        The *name* is sanitized into a safe filename stem. When *deduplicate*
        is ``True`` (the default), a ``-2``/``-3``/... suffix is appended on a
        name collision so an existing diagram is never overwritten; pass
        ``deduplicate=False`` to overwrite an existing same-named file.

        .. note::
            Low-level auto-naming write primitive; it does **not** validate. The
            validated new-diagram path is ``DiagramPersistenceService.create`` (used by
            the MCP ``diagram_generate_direct`` flow), which validates and then calls this.

        Returns:
            The resolved ``Path`` to the written ``<name>.gp.json`` file.
        """
        safe = self.unique_name(name) if deduplicate else self.sanitize_name(name)
        return self.write_diagram(self.diagram_file_path(safe), diagram)

    def write_diagram(
        self,
        path: Union[str, Path],
        diagram: Dict[str, Any],
    ) -> Path:
        """Write diagram JSON to an explicit path on disk atomically.

        Uses a temporary file + ``os.replace`` so a partial write never
        corrupts the existing file.

        .. note::
            This is a *raw safe-write primitive*: it is path-safe and atomic but
            does **not** validate. The validated write funnel is
            ``DiagramPersistenceService`` (``save`` to overwrite an existing file,
            ``create`` for a new one); go through it so no unvalidated diagram is
            ever persisted. To write a new diagram by name (sanitization +
            collision handling) use :meth:`create_diagram`.

        Args:
            path: An explicit absolute or workspace-relative path to the target
                ``<name>.gp.json`` file.
            diagram: The diagram dict to serialise.

        Returns:
            The resolved ``Path`` to the written file.

        Raises:
            UnsafePathError: if the target path escapes the workspace.
            TypeError: if *diagram* is not a dict.
        """
        if not isinstance(diagram, dict):
            raise TypeError(f"diagram must be a dict; got {type(diagram).__name__}.")

        safe_target = self.resolve_safe_path(Path(path))
        os_path(safe_target.parent).mkdir(parents=True, exist_ok=True)

        # Write to a sibling temp file then atomically replace the target.
        dir_ = safe_target.parent
        fd, tmp_path = tempfile.mkstemp(dir=str(os_path(dir_)), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(diagram, fh, ensure_ascii=False, indent=2, allow_nan=False)
            os.replace(tmp_path, str(os_path(safe_target)))
        except Exception:
            # Best-effort cleanup of the temp file on failure.
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

        return safe_target

    def write_text(self, path: Union[str, Path], text: str) -> Path:
        """Write arbitrary *text* to an explicit path on disk atomically.

        A raw safe-write primitive (path-safe, atomic via a temp file +
        ``os.replace``) used for derived sibling artifacts such as the rendered
        ``<name>.svg`` produced by ``DiagramRenderService``.

        Args:
            path: An explicit absolute or workspace-relative target path.
            text: The text content to write (UTF-8).

        Returns:
            The resolved ``Path`` to the written file.

        Raises:
            UnsafePathError: if the target path escapes the workspace.
            TypeError: if *text* is not a string.
        """
        if not isinstance(text, str):
            raise TypeError(f"text must be a str; got {type(text).__name__}.")

        safe_target = self.resolve_safe_path(Path(path))
        os_path(safe_target.parent).mkdir(parents=True, exist_ok=True)

        dir_ = safe_target.parent
        fd, tmp_path = tempfile.mkstemp(dir=str(os_path(dir_)), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
            os.replace(tmp_path, str(os_path(safe_target)))
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

        return safe_target

    def write_bytes(self, path: Union[str, Path], data: bytes) -> Path:
        """Write arbitrary binary *data* to an explicit path on disk atomically.

        The binary counterpart of :meth:`write_text` (path-safe, atomic via a temp
        file + ``os.replace``), used for derived binary sibling artifacts such as
        the rasterized ``<name>.png`` produced by ``DiagramRenderService``.

        Args:
            path: An explicit absolute or workspace-relative target path.
            data: The bytes to write.

        Returns:
            The resolved ``Path`` to the written file.

        Raises:
            UnsafePathError: if the target path escapes the workspace.
            TypeError: if *data* is not bytes-like.
        """
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f"data must be bytes; got {type(data).__name__}.")

        safe_target = self.resolve_safe_path(Path(path))
        os_path(safe_target.parent).mkdir(parents=True, exist_ok=True)

        dir_ = safe_target.parent
        fd, tmp_path = tempfile.mkstemp(dir=str(os_path(dir_)), suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
            os.replace(tmp_path, str(os_path(safe_target)))
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

        return safe_target
