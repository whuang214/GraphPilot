"""Bounds and secret screening for a submitted draft.

The draft never reaches a provider, so this is not prompt hygiene. It exists because a
draft's prose — evidence summaries, labels, rationale — is copied into
``metadata.evidence`` in a canonical diagram that a user will commit. A credential pasted
into a summary would end up in version control.

This is a defence, not a substitute for host-side secret hygiene: it catches the obvious
labelled shapes and nothing more.
"""

import json
import re
from typing import Any, List, Mapping, Sequence, Tuple

from services.drafts.draft_contract import DraftFinding

#: One draft describes one diagram. Well past any legible diagram, small enough that a
#: runaway document is refused before it is walked.
MAX_DRAFT_BYTES = 2 * 1024 * 1024

_SECRET_LABEL = (
    r"(?:password|passwd|api[ _-]?key|secret[ _-]?key|client[ _-]?secret|"
    r"access[ _-]?token|auth[ _-]?token|private[ _-]?key)"
)
#: A labelled assignment followed by a long unbroken run of secret-shaped characters.
_ASSIGNED_SECRET = re.compile(
    rf"{_SECRET_LABEL}\s*[:=]\s*[\"']?([A-Za-z0-9_\-./+=]{{16,}})",
    re.IGNORECASE,
)
_BEARER = re.compile(r"Authorization\s*:\s*Bearer\s+([A-Za-z0-9_\-./+=]{16,})", re.IGNORECASE)
_PRIVATE_KEY_BLOCK = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")

#: Prose fields a host writes. Structural fields (IDs, paths, semantic types) are
#: pattern-bounded by the schema and cannot hold a credential.
_SCANNED_FIELDS = frozenset(
    {"summary", "statement", "reason", "label", "expression"}
)

#: Arrays of bare strings that are prose. `_walk_prose` keys off the field name, and a
#: string inside a list has no field name of its own — so `requests` was invisible to
#: this scan by construction. It is the *most* exposed field in the document: a verbatim
#: user prompt is where a pasted error message with a token in it ends up, and unlike a
#: host-authored summary nobody composed it with care.
_SCANNED_ARRAYS = frozenset({"requests"})


def size_findings(draft: Any) -> Tuple[DraftFinding, ...]:
    try:
        encoded = len(json.dumps(draft, ensure_ascii=False).encode("utf-8"))
    except (TypeError, ValueError):
        return ()
    if encoded <= MAX_DRAFT_BYTES:
        return ()
    return (
        DraftFinding(
            "draft_too_large",
            "$",
            f"The draft is {encoded} bytes; the limit is {MAX_DRAFT_BYTES}. "
            "A draft describes one diagram, so narrow its scope rather than raising the bound.",
            {"actualBytes": encoded, "maxBytes": MAX_DRAFT_BYTES},
        ),
    )


def secret_findings(draft: Any) -> Tuple[DraftFinding, ...]:
    findings: List[DraftFinding] = []
    for path, value in _walk_prose(draft, "$"):
        if _looks_like_secret(value):
            findings.append(
                DraftFinding(
                    "possible_secret",
                    path,
                    "This reads like a credential. A draft's prose is copied into the saved "
                    "diagram, so it must not carry one. Describe what the code does instead of "
                    "quoting the value.",
                )
            )
    return tuple(findings)


def _looks_like_secret(text: str) -> bool:
    return bool(
        _ASSIGNED_SECRET.search(text) or _BEARER.search(text) or _PRIVATE_KEY_BLOCK.search(text)
    )


def _walk_prose(value: Any, path: str):
    if isinstance(value, Mapping):
        for key, item in value.items():
            child = f"{path}.{key}"
            if isinstance(item, str):
                if key in _SCANNED_FIELDS:
                    yield child, item
            elif key in _SCANNED_ARRAYS and isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
                for index, entry in enumerate(item):
                    if isinstance(entry, str):
                        yield f"{child}[{index}]", entry
            else:
                yield from _walk_prose(item, child)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, item in enumerate(value):
            yield from _walk_prose(item, f"{path}[{index}]")
