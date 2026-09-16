"""One shared handled-operation problem value for protocol adapters."""

import copy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional


#: Whether repeating the *same* call could succeed.
#:
#: Every code an adapter can emit is registered here. Passing ``retryable`` explicitly at
#: a call site is allowed but is not a substitute for registration: only the path that
#: omits it raises, so an unregistered code can lurk until an unusual branch runs.
_RETRYABILITY = MappingProxyType(
    {
        # Transport, arguments, and paths.
        "invalid_arguments": True,
        "invalid_workspace": True,
        "workspace_resolution_error": True,
        "missing_path": True,
        "invalid_path": True,
        "unsafe_path": True,
        # Not retryable: the same unsupported identifier fails identically, and calling it
        # retryable invites a host to spend another round discovering that.
        "unsupported_diagram_type": False,
        # Files and storage.
        "diagram_not_found": True,
        "not_found": True,
        "invalid_json": True,
        "invalid_diagram_json": True,
        "invalid_diagram": True,
        "source_changed": True,
        "load_failed": True,
        "list_failed": True,
        "save_failed": True,
        # Schema and validation services.
        "validation_unavailable": True,
        "validation_failed": True,
        # Draft refusals. None are retryable: the draft has to change first.
        "draft_invalid": False,
        "draft_too_large": False,
        "possible_secret": False,
        "requests_invalid": False,
        # The edit round trip. Neither is retryable as-is: `basis_stale` needs another
        # `diagram_read` first, and a crossed diagram can only be edited in the browser.
        "basis_stale": False,
        "diagram_crossed": False,
        "duplicate_id": False,
        "unresolved_reference": False,
        # A citation whose `symbol` is outside the lines it points at. Explained in
        # REFUSAL_GUIDE and absent here, so nothing said whether retrying helps: it
        # does not, until the draft names different lines.
        "evidence_symbol_not_in_range": False,
        "cyclic_parent": False,
        "semantic_type_unsupported": False,
        "containment_unsupported": False,
        "notation_invalid": False,
        "guard_required": False,
        "assurance_unsupported": False,
        "evidence_required": False,
        "evidence_unexpected": False,
        "evidence_unreadable": False,
        "evidence_stale": False,
        "orphan_evidence": False,
        "orphan_assumption": False,
        "diagram_exists": False,
        # Rendering and layout.
        "render_failed": True,
        "layout_engine_unavailable": False,
        "layout_failed": False,
        "internal_error": False,
    }
)


#: Codes that arrive on a call that **succeeded**, in `operationWarnings`. The diagram was
#: saved; every one of these is advice about it.
#:
#: Registered for the same reason the refusals above are, and after the same failure. The
#: refusal codes had a registry and a test comparing it to `04-operation-errors.md`, so a
#: refusal could not reach a host undocumented. Warnings had neither — they were raw dicts
#: built at the call site — and the document's warning table was maintained by hand beside
#: them. `layout_overlap` was added to the update service and shipped with a green suite
#: and no row in the contract, which is exactly how the refusal table drifted by 50 codes.
#:
#: `long_label`, `label_truncated` and `structural_constraint` are absent on purpose: those
#: reach `operationWarnings` as `ValidationCode` members, which is already a machine-
#: readable list. This registry covers the ones assembled by hand.
_WARNING_CODES = frozenset({
    "content_lost",
    "evidence_stale",
    "hard_to_read",
    "layout_overlap",
    "render_failed",
})


def operation_warning(code: str, message: str, **details: Any) -> Dict[str, Any]:
    """One advisory about a diagram that was saved anyway.

    Rejects an unregistered code, so a new warning cannot reach a host without a row in
    the public contract.
    """
    if code not in _WARNING_CODES:
        raise ValueError(f"Unregistered operation warning code: {code}")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Operation warning message must be nonempty.")
    return {"code": code, "message": message.strip(), **details}


@dataclass(frozen=True)
class OperationProblem:
    code: str
    message: str
    retryable: bool
    details: Optional[Mapping[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        value: Dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }
        if self.details is not None:
            value["details"] = copy.deepcopy(dict(self.details))
        return value


def operation_problem(
    code: str,
    message: str,
    *,
    details: Optional[Mapping[str, Any]] = None,
    retryable: Optional[bool] = None,
) -> OperationProblem:
    if not isinstance(code, str) or not code:
        raise ValueError("Operation problem code must be nonempty.")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Operation problem message must be nonempty.")
    if retryable is None:
        if code not in _RETRYABILITY:
            raise ValueError(f"Unregistered operation problem code: {code}")
        retryable = _RETRYABILITY[code]
    if type(retryable) is not bool:
        raise ValueError("Operation problem retryable must be boolean.")
    if details is not None and not isinstance(details, Mapping):
        raise ValueError("Operation problem details must be an object when present.")
    return OperationProblem(code, message.strip(), retryable, details)
