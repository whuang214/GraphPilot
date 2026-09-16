"""Read, digest, and re-check the source regions a draft cites.

Freshness is bound to **the exact cited lines**, not to a repository fingerprint. A
diagram of the service layer is unaffected by an edit to an unrelated module, and a
change inside a cited region is caught precisely, naming the evidence that moved.
"""

import hashlib
import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from services.drafts.draft_contract import DraftFinding
from services.shared.workspace_storage_service import (
    UnsafePathError,
    WorkspaceStorageError,
    WorkspaceStorageService,
)

#: A cited file is read whole to slice its region. Generous for source, bounded so a
#: stray binary cannot be pulled into memory.
MAX_EVIDENCE_FILE_BYTES = 4 * 1024 * 1024


@dataclass(frozen=True)
class ResolvedEvidence:
    """One cited region, read and digested."""

    evidence_id: str
    path: str
    content_digest: str
    line_count: int


@dataclass(frozen=True)
class EvidenceResolution:
    resolved: Tuple[ResolvedEvidence, ...]
    findings: Tuple[DraftFinding, ...]

    @property
    def valid(self) -> bool:
        return not self.findings

    def digests(self) -> Dict[str, str]:
        return {item.evidence_id: item.content_digest for item in self.resolved}


#: A `symbol` that is a bare identifier is a claim checkable against the cited text. One
#: that is not — `imports`, `module docstring`, `urlpatterns block` — is a human label for
#: a region with no single name, and demanding it appear verbatim would reject honest
#: citations. Only the last dotted segment is checked, so `Login.submit` is judged on
#: `submit`: the qualifier is the author's way of saying where, not a string in the file.
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _symbol_outside_region(symbol: Any, region: Sequence[str], path: str = "") -> Optional[str]:
    """Return the identifier a citation names but does not point at, if any.

    A `symbol` was accepted, stored, and never compared to the lines beside it, so a
    citation could name one function and cite a different one entirely — three shipped
    that way in a single corpus run, one naming a test 17 lines below the range it cited.
    That is the exact failure the product exists to prevent: an element that looks
    evidenced and is not.

    Deliberately conservative, because a false refusal here teaches a host to stop giving
    symbols at all. Three cases are left alone: a symbol that is not a bare identifier is
    a human label for a region with no single name (`the import block`); a qualifier is
    judged on its last segment only, so `Login.submit` is checked as `submit`; and a
    symbol equal to the file's own stem is naming the module rather than something in it.

    A single identifier-shaped word like `imports` stays checked even though it is
    probably a label, because the two costs are not equal: a host wrongly refused widens
    the range and moves on, while a miscitation that slips through ships a diagram that
    looks evidenced and is not.
    """
    text = (symbol or "").strip()
    if not text:
        return None
    name = text.rsplit(".", 1)[-1].strip()
    if not _IDENTIFIER.match(name):
        return None
    if name.lower() == PurePosixPath(path).stem.lower():
        return None
    return None if any(name in line for line in region) else name


def region_digest(lines: Sequence[str]) -> str:
    """Digest a cited region.

    Line endings are normalized out: a host on Windows and a host on Linux citing the
    same lines must agree, or every diagram would look stale on the other machine.
    """
    payload = "\n".join(line.rstrip("\r") for line in lines).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


class EvidenceService:
    def __init__(self, storage: WorkspaceStorageService) -> None:
        self._storage = storage

    def resolve(self, evidence: Sequence[Mapping[str, Any]]) -> EvidenceResolution:
        """Read every cited region, or report exactly which ones could not be read."""
        resolved: List[ResolvedEvidence] = []
        findings: List[DraftFinding] = []
        cache: Dict[str, Optional[List[str]]] = {}

        for index, record in enumerate(evidence):
            locator = record["locator"]
            path = locator["path"]
            base = f"$.evidence[{index}].locator"

            if path not in cache:
                cache[path] = self._read_lines(path)
            lines = cache[path]
            if lines is None:
                findings.append(
                    DraftFinding(
                        "evidence_unreadable",
                        f"{base}.path",
                        f"'{path}' could not be read. It must be a readable UTF-8 file inside the workspace.",
                    )
                )
                continue

            start = locator["lineRange"]["start"]
            end = locator["lineRange"]["end"]
            if start > end:
                findings.append(
                    DraftFinding(
                        "evidence_unreadable",
                        f"{base}.lineRange",
                        f"start {start} is after end {end}.",
                    )
                )
                continue
            if not lines:
                findings.append(
                    DraftFinding(
                        "evidence_unreadable",
                        f"{base}.path",
                        f"'{path}' is empty, so it cannot establish anything.",
                        {"path": path},
                    )
                )
                continue
            if end > len(lines):
                findings.append(
                    DraftFinding(
                        "evidence_unreadable",
                        f"{base}.lineRange.end",
                        f"'{path}' has {len(lines)} lines, so {end} is past the end of the file. "
                        f"The last valid end is {len(lines)}.",
                        {"path": path, "lineCount": len(lines), "requestedEnd": end},
                    )
                )
                continue

            region = lines[start - 1 : end]
            missing = _symbol_outside_region(locator.get("symbol"), region, path)
            if missing:
                findings.append(
                    DraftFinding(
                        "evidence_symbol_not_in_range",
                        f"{base}.symbol",
                        f"'{missing}' does not appear in {path} lines {start}-{end}. The "
                        f"citation names one thing and points at another — widen the range "
                        f"to cover it, or correct the symbol.",
                        {"path": path, "symbol": missing, "start": start, "end": end},
                    )
                )
                continue

            resolved.append(
                ResolvedEvidence(
                    evidence_id=record["id"],
                    path=path,
                    content_digest=region_digest(region),
                    line_count=end - start + 1,
                )
            )

        return EvidenceResolution(tuple(resolved), tuple(sorted(findings, key=lambda f: (f.path, f.code))))

    def recheck(self, recorded: Sequence[Mapping[str, Any]]) -> Tuple[DraftFinding, ...]:
        """Re-hash previously cited regions and report the ones that moved.

        *recorded* is ``metadata.evidence`` from a saved diagram: each entry carries its
        locator and the digest taken when the diagram was created.
        """
        findings: List[DraftFinding] = []
        for index, record in enumerate(recorded):
            locator = record["locator"]
            path = locator["path"]
            lines = self._read_lines(path)
            base = f"$.evidence[{index}]"
            if lines is None:
                findings.append(
                    DraftFinding(
                        "evidence_unreadable",
                        f"{base}.locator.path",
                        f"'{path}' can no longer be read.",
                        {"evidenceId": record.get("id")},
                    )
                )
                continue
            start = locator["lineRange"]["start"]
            end = locator["lineRange"]["end"]
            if end > len(lines) or start > end:
                findings.append(
                    DraftFinding(
                        "evidence_stale",
                        f"{base}.locator.lineRange",
                        f"'{path}' is now {len(lines)} lines, so the cited range no longer exists.",
                        {"evidenceId": record.get("id"), "path": path},
                    )
                )
                continue
            if region_digest(lines[start - 1 : end]) != record.get("contentDigest"):
                findings.append(
                    DraftFinding(
                        "evidence_stale",
                        f"{base}.contentDigest",
                        f"'{path}' lines {start}-{end} changed since this diagram was created. "
                        "Re-read the region and author the evidence again.",
                        {"evidenceId": record.get("id"), "path": path},
                    )
                )
        return tuple(sorted(findings, key=lambda f: (f.path, f.code)))

    def _read_lines(self, path: str) -> Optional[List[str]]:
        try:
            self._storage.resolve_safe_path(path)
            text = self._storage.read_text(path, max_bytes=MAX_EVIDENCE_FILE_BYTES)
        except (UnsafePathError, WorkspaceStorageError, OSError, UnicodeDecodeError, ValueError):
            return None
        if not text:
            # "".split("\n") is [""], which would let an empty file answer for line 1 and
            # digest nothing at all. An empty file cannot establish anything.
            return []
        lines = text.split("\n")
        # A trailing newline terminates the last line, it does not begin another. Left in,
        # the phantom made every such file report one line too many — so a host citing the
        # true last line was told "the last valid end is 162" on a 161-line file, and a
        # citation to that phantom line was accepted. Real ranges are unaffected, so no
        # stored digest moves.
        if lines and lines[-1] == "":
            lines.pop()
        return lines
