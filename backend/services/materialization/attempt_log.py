"""One line per `diagram_create` attempt, beside the diagrams it produced.

An accepted draft leaves a diagram and a trace on disk. **A refused one leaves nothing** —
the findings go back to the caller and the workspace is untouched, by design. So the only
record that authoring was hard is the host's memory of it, and a host that retried four
times and then succeeded reports a success.

This is that record: name, type, accepted, the finding codes, and the shape of the paths
they landed on.

## Why there is no setting

There was one. `GRAPHPILOT_DRAFT_LOG` took a path and was off unless set, and across four
corpus runs it produced a usable measurement **zero** times — the variable reached the
wrong process twice and held an empty value once. Every one of those cost a run, and each
failure was silent, because "off" and "misconfigured" look identical from the outside.

A flag that must be switched on is a flag that is off the one time it matters. So this is
unconditional, and it writes where everything else already goes:

    <workspaceDir>/.graphpilot/attempts.jsonl

That is not a new intrusion. A successful create already writes a diagram, an SVG **and**
the full draft into the same folder — this file is smaller than any of them and holds
strictly less: no draft, no source, no labels. Names, codes, counts.

It is also product behaviour rather than scaffolding. A user whose drafts keep being
refused now has the record of why, in their own repository, without being told to
configure anything first.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

logger = logging.getLogger(__name__)

FILENAME = "attempts.jsonl"


def _shape(path: str) -> str:
    """`$.elements[3].assurance` -> `$.elements[].assurance`, so attempts group.

    Without this, ten refusals on ten different elements are ten distinct strings and
    nothing shows that one rule caused all of them.
    """
    out, depth = [], 0
    for char in path or "":
        if char == "[":
            depth += 1
            out.append(char)
        elif char == "]":
            depth -= 1
            out.append(char)
        elif depth == 0:
            out.append(char)
    return "".join(out)


def record(
    storage_root: Path,
    draft: Any,
    *,
    accepted: bool,
    findings: Sequence[Any] = (),
    warnings: Sequence[Mapping[str, Any]] = (),
) -> None:
    """Append one attempt. Never raises.

    This sits on the create path, so it must never be the reason a create fails. A
    malformed draft is exactly the case worth recording and exactly the case where reading
    fields off it throws, hence the defensive shape rather than trust in the schema — at
    the first call site the draft has not been validated yet.
    """
    try:
        fields = draft if isinstance(draft, Mapping) else {}
        entry = {
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "diagram": str(fields.get("diagramName") or "?"),
            "type": str(fields.get("diagramType") or "?"),
            "accepted": accepted,
            # An accepted create is not necessarily a clean one. Without this, the two
            # `hard_to_read` creates in run 4 recorded as `accepted: true, findings: []`
            # and a later reader would conclude they went perfectly.
            "warnings": sorted({str(w.get("code")) for w in warnings if w.get("code")}),
            # Codes and paths only. A finding's message can quote the source it read.
            "findings": sorted({
                f"{getattr(f, 'code', '?')}@{_shape(getattr(f, 'path', ''))}"
                for f in findings
            }),
            "elements": len(fields.get("elements") or ()),
            "relationships": len(fields.get("relationships") or ()),
            "evidence": len(fields.get("evidence") or ()),
        }
        # Never conjures the folder. A refusal in a workspace GraphPilot has not
        # successfully written to must leave **no trace at all** — a user whose first
        # draft is rejected should not find a `.graphpilot/` they did not ask for, and
        # two tests hold that line. Once the workspace is in use, every attempt is
        # recorded, refusals included.
        if not storage_root.is_dir():
            return
        with (storage_root / FILENAME).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 - a lost line must never cost a diagram
        logger.debug("Could not append to the attempt log", exc_info=True)


def read(storage_root: Path) -> list:
    """Every attempt recorded for one workspace, oldest first."""
    path = Path(storage_root) / FILENAME
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def summarise(attempts: Sequence[Mapping[str, Any]]) -> Optional[dict]:
    """The run's number: calls per accepted diagram, and what caused the rest.

    `None` when nothing was recorded, so a caller can tell "no attempts" from "no
    refusals" — the two used to look the same and one of them means the log is broken.
    """
    if not attempts:
        return None
    accepted = [a for a in attempts if a.get("accepted")]
    causes: dict = {}
    for attempt in attempts:
        if attempt.get("accepted"):
            continue
        for finding in attempt.get("findings") or ():
            causes[finding] = causes.get(finding, 0) + 1
    return {
        "attempts": len(attempts),
        "accepted": len(accepted),
        "attemptsPerDiagram": round(len(attempts) / len(accepted), 2) if accepted else None,
        "refusalsByRule": dict(sorted(causes.items(), key=lambda kv: -kv[1])),
    }
