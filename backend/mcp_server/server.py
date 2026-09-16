"""GraphPilot MCP server.

Thin IDE-facing entry point that exposes the shared backend capabilities
as MCP tools. Handlers stay thin: they delegate to the shared services in
``services/`` rather than duplicating schema, type, or validation logic, so the
MCP tools and browser-facing Django API share behavior while returning the response
shape each client needs.

Run as a script (stdio transport):

    python mcp_server/server.py
"""

import logging
import os
import sys
from functools import wraps
from pathlib import Path
from typing import Annotated, Optional
from urllib.parse import urlencode

# Make the backend package root importable when this file is run as a script
# (``python mcp_server/server.py`` puts ``mcp_server/`` on sys.path, not the
# backend root that holds the ``services`` and ``graphpilot`` packages).
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "graphpilot.settings")

import django  # noqa: E402  (import after sys.path / settings module are set)
from dotenv import load_dotenv  # noqa: E402
from mcp.server.fastmcp import FastMCP  # noqa: E402
from mcp.types import CallToolResult, TextContent  # noqa: E402
from pydantic import Field  # noqa: E402

# Load backend/.env explicitly (not cwd-relative) so the server picks up local
# config regardless of the working directory an MCP client (Cline, VS Code Copilot,
# etc.) launches it from. Done before django.setup() so settings read the populated
# environment.
load_dotenv(BACKEND_DIR / ".env")

# Configure Django so the shared services can read settings (e.g. BASE_DIR).
# ``django.setup()`` is a no-op once the app registry is ready, so this is safe
# under the test runner where Django is already configured.
django.setup()

from django.conf import settings  # noqa: E402

from services.shared.workspace_storage_service import (  # noqa: E402
    WorkspaceStorageService,
    DiagramNotFoundError,
    InvalidDiagramJSONError,
    UnsafePathError,
    WorkspaceResolutionError,
)
from services.diagrams.rendering.diagram_render_service import (  # noqa: E402
    DiagramRenderService,
    DiagramRenderServiceError,
)
from services.shared.editor_origin import editor_base_url  # noqa: E402
from services.shared.schema_registry import SchemaRegistry  # noqa: E402
from services.shared.diagram_type_service import DiagramTypeService  # noqa: E402
from services.diagrams.validation.diagram_validation_service import DiagramValidationService  # noqa: E402
from services.drafts.authoring_contract_service import AuthoringContractService  # noqa: E402
from services.drafts.draft_validation_service import DraftValidationService
from services.drafts.evidence_service import EvidenceService  # noqa: E402
from services.drafts.diagram_edit_service import (  # noqa: E402
    DiagramEditService,
    EditRefused,
)
from services.materialization.diagram_update_service import (  # noqa: E402
    DiagramUpdateService,
    UpdateRefused,
)
from services.materialization.diagram_creation_service import (  # noqa: E402
    DiagramAlreadyExists,
    DiagramCreationService,
    DraftRefused,
)
from services.shared.operation_problem import operation_problem  # noqa: E402

mcp = FastMCP("graphpilot")

logger = logging.getLogger(__name__)


# Shared service instances. These are stateless lookups / cache-friendly, so a
# single instance per process is sufficient for the MVP.
_type_service = DiagramTypeService()
_schema_service = SchemaRegistry()
_validation_service = DiagramValidationService()
_render_service = DiagramRenderService()
_creation_service = DiagramCreationService(render_service=_render_service)
_authoring_contract_service = AuthoringContractService(_schema_service)
# The edit round trip: `diagram_read` projects a saved diagram into a draft file, and
# `diagram_update` merges that file back over it.
_edit_service = DiagramEditService()
_update_service = DiagramUpdateService()
# The same validator `diagram_create` uses, so a dry run cannot pass where a create fails.
_draft_validation_service = DraftValidationService()

# Supported diagram-type identifiers, surfaced as a JSON-schema ``enum`` on the
# ``diagramType`` arguments below so MCP clients advertise the valid values
# (kept in sync with ``DiagramTypeService``) without a separate lookup call.
_SUPPORTED_TYPES = _type_service.list_supported_types()


def _findings_markdown(findings: list, headline: str) -> str:
    """Every finding as a line a host can act on, not a count it has to go looking for.

    `diagram_create` used to report *"the draft was refused with 8 finding(s)"* and list
    none of them: the findings existed only at `structuredContent.error.details.findings`,
    so a host reading the text channel learned how many things were wrong and not one of
    them. Its *warning* channel already itemised properly, which made refusals the worse
    half of the same tool. One renderer, so the two cannot drift again.
    """
    lines = [headline, ""]
    lines += [f"- `{f['code']}` at `{f['path']}` — {f['message']}" for f in findings[:40]]
    if len(findings) > 40:
        lines.append(f"- …and {len(findings) - 40} more.")
    return "\n".join(lines)


def _error(
    code: str,
    message: str,
    *,
    details: Optional[dict] = None,
    retryable: Optional[bool] = None,
    text: Optional[str] = None,
) -> CallToolResult:
    """Return one handled MCP operation failure with ``isError: true``.

    *text* overrides the prose channel where the message alone cannot act as the report —
    a refusal carrying findings, for instance. The structured half is unchanged either way.
    """
    problem = operation_problem(code, message, details=details, retryable=retryable)
    return CallToolResult(
        content=[TextContent(type="text", text=text or problem.message)],
        structuredContent={"error": problem.to_dict()},
        isError=True,
    )


def _sanitize_unexpected_errors(operation: str):
    def decorator(handler):
        @wraps(handler)
        async def wrapped(*args, **kwargs):
            try:
                return await handler(*args, **kwargs)
            except Exception:
                logger.exception("%s failed unexpectedly", operation)
                return _error(
                    "internal_error",
                    "The operation failed unexpectedly.",
                )

        return wrapped

    return decorator


def _workspace_service(workspace_dir: str) -> WorkspaceStorageService:
    raw = str(workspace_dir).strip()
    path = Path(raw)
    if not raw or not path.is_absolute() or not path.is_dir():
        raise ValueError("workspaceDir must be an absolute existing local directory.")
    return WorkspaceStorageService(path)


def _workspace_relative(workspace_dir: str, path: Path) -> str:
    return path.resolve().relative_to(Path(workspace_dir).resolve()).as_posix()


def _edit_url(diagram_path: Path) -> str:
    """Build the editor link, aimed at whichever GraphPilot is actually running.

    The origin is resolved rather than read: this process is spawned by the IDE and
    knows nothing about the dev server or the launcher. `editor_origin` owns that rule,
    and the literal default lives once in `graphpilot.ports` — it used to be written
    here as well, a second copy that nothing kept in step with the first.
    """
    base_url = editor_base_url()
    return f"{base_url}/editor?{urlencode({'diagramPath': diagram_path.as_posix()})}"


def _workspace_relative_path(value: str, field: str) -> str:
    segments = value.split("/") if isinstance(value, str) else ()
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or Path(value).is_absolute()
        or (len(value) >= 2 and value[0].isalpha() and value[1] == ":")
        or any(segment in {"", ".", ".."} for segment in segments)
    ):
        raise UnsafePathError(f"{field} must be a nonempty workspace-relative POSIX path.")
    return value


#: The identifiers do not explain themselves — `bdd` reads as behaviour-driven development
#: to any software reader, and two complete runs were lost to that. The fix was to inline
#: every meaning into this description, which worked and then outlived its reason twice
#: over:
#:
#: 1. It does not scale. One sentence per type, repeated in `tools/list`, which every
#:    client loads at connect. Three types is 500 characters; a dozen is a paragraph
#:    nobody reads, on an argument.
#: 2. The failure it guarded is no longer terminal. Those runs died because the provider
#:    pipeline's append-only history refused the correction once the wrong type was
#:    committed. That pipeline is gone. Today a host that fetches the wrong contract reads
#:    `meaning` at the top of it — *"Not behaviour-driven development… use
#:    activity_diagram for behaviour"* — and pays one cheap call to fetch the right one.
#:
#: So the meanings live in `diagram_list_types`, which exists for exactly this, and the
#: enum below still gives a client the valid values for free. `unsupported_diagram_type`
#: is **not** the safety net here: it catches an identifier that does not exist, while the
#: mistake worth catching is a *valid* identifier chosen for the wrong reason. The
#: contract's own `meaning` is what catches that, after the fact and cheaply.
_DIAGRAM_TYPE_ARG_DESCRIPTION = (
    "A supported diagram type. The identifiers do not explain themselves — call "
    "`diagram_list_types` for what each one means before choosing."
)


def _issue_details(issues) -> dict:
    """Bound the issue list without hiding whole regions of the document.

    Straight truncation kept the first 255 issues in sorted order, so a document
    with many defects under one early path reported nothing about later paths and
    a host had to rediscover them one round at a time. Give every distinct path a
    representative first, then spend what capacity remains on the rest.
    """
    ordered = sorted(issues, key=lambda item: (item.path, item.code, item.message))
    if len(ordered) <= 256:
        return {"issues": [item.to_dict() for item in ordered]}

    capacity = 255
    seen = set()
    breadth = []
    remainder = []
    for item in ordered:
        if item.path in seen:
            remainder.append(item)
            continue
        seen.add(item.path)
        breadth.append(item)
    selected = breadth[:capacity]
    selected.extend(remainder[: capacity - len(selected)])
    selected.sort(key=lambda item: (item.path, item.code, item.message))
    selected.append(
        type(ordered[0])(
            code="additional_issues_omitted",
            message=f"{len(ordered) - len(selected)} additional issues were omitted.",
            path="$",
        )
    )
    return {"issues": [item.to_dict() for item in selected]}


def _structured_result(message: str, structured: dict) -> CallToolResult:
    return CallToolResult(
        content=[TextContent(type="text", text=message)],
        structuredContent=structured,
        isError=False,
    )


def _validation_summary(result: dict) -> str:
    """One line for `content`; the whole `ValidationResult` stays in `structuredContent`."""
    issues = result.get("issues") or []
    verdict = "passed" if result.get("valid") else "failed"
    line = f"Diagram {verdict} validation ({len(issues)} issue(s))."
    if result.get("checkedCitations"):
        stale = len(result.get("staleCitations") or [])
        line += f" Citations checked: {result.get('citationsChecked', 0)}, {stale} stale."
    return line


def _prose_result(markdown: str) -> CallToolResult:
    """Return prose with no structured half, because there is no structure to carry.

    Returning a bare ``str`` looks simpler and is not: FastMCP auto-wraps a primitive
    return into ``{"result": ...}`` to satisfy structured output, so the whole document
    shipped twice — once as ``content``, once as the same string in a box. That is the
    duplication this program spent itself removing, arrived at by accident rather than
    by choice.

    `structuredContent` is optional in the specification. Omitting it says something
    true: there is no structure here, only an argument to read.
    """
    return CallToolResult(
        content=[TextContent(type="text", text=markdown)],
        isError=False,
    )


def _markdown_result(markdown: str, structured: dict) -> CallToolResult:
    """Return a tool result that renders the same in every MCP client.

    ``content`` is a single Markdown ``TextContent`` (a summary + the editor link +
    file paths) — the one channel every chat client renders consistently — and
    ``structuredContent`` carries the machine-readable fields (passed through verbatim
    by the MCP server). No image content block: agent-loop clients (Cline, Copilot)
    do not render MCP images cleanly (they leak the base64 into the model), so viewing
    the picture is done via the editor link, the saved ``.svg``, or an explicit
    ``diagram_render`` ``format="png"`` save.
    """
    return CallToolResult(
        content=[TextContent(type="text", text=markdown)],
        structuredContent=structured,
        isError=False,
    )


@mcp.tool()
@_sanitize_unexpected_errors("health")
async def health() -> dict:
    """Return a simple health check."""
    return _structured_result("GraphPilot MCP server is up.", {"status": "ok"})


@mcp.tool()
@_sanitize_unexpected_errors("echo")
async def echo(message: str) -> str:
    """Echo a message for quick connectivity tests.

    ``{"result": ...}`` is the shape FastMCP's auto-wrapping was already producing for a
    bare ``str`` return, kept verbatim so the wire contract does not change. Stated here
    rather than inherited, because a payload nobody chose is a payload nobody can rely on.
    """
    return _structured_result(message, {"result": message})


@mcp.tool()
@_sanitize_unexpected_errors("diagram_list_types")
async def diagram_list_types() -> dict:
    """List the diagram types GraphPilot supports, and what each identifier means.

    **Call this before choosing a type.** ``diagramTypeMeanings`` is the payload that
    matters, not ``diagramTypes``: the identifiers do not explain themselves, and
    choosing on the name alone has cost whole runs. Pick against the meaning.

    The meanings are returned as data rather than restated here, so a new diagram type
    is one entry in ``DIAGRAM_TYPE_GUIDE`` and no edit to any description anywhere.

    Read-only; writes no files.
    """
    guide = _type_service.choosing_guide()
    return _structured_result(
        "\n\n".join(
            [
                "Choose against `meaning` and `chooseWhen`, never against the identifier.",
                *(
                    f"**{item['diagramType']}** — {item['meaning']}\n\n"
                    f"Choose it when: {item['chooseWhen']}"
                    for item in guide
                ),
            ]
        ),
        {
            # One array, not a list of names beside a map of meanings. The old shape let a
            # host read the identifiers and skip the explanations, which is precisely how
            # `bdd_diagram` was read as behaviour-driven development twice. There is no
            # name-only view here to skim.
            "howToChoose": (
                "Read `meaning` and `chooseWhen` on every entry before picking. The "
                "identifiers do not explain themselves and choosing on the name alone has "
                "cost whole runs. If more than one looks plausible, `chooseWhen` is the "
                "tiebreak: it describes the request, not the notation."
            ),
            "diagramTypes": guide,
        },
    )


_WORKFLOW = """\
# Creating a GraphPilot diagram

You read the repository and decide what the diagram means. GraphPilot turns that into
notation, layout, validation, and files. **No model runs on GraphPilot's side**, so this
costs one tool call and no provider time.

## The five steps

1. **Choose the type — call `diagram_list_types` first.** The identifiers do not explain
   themselves and that call is the only place they are explained. Choosing on the name
   alone has cost whole runs.
2. **Get the contract.** `diagram_get_authoring_contract` returns the exact draft shape
   for that type, its element and relationship vocabulary, the direction each
   relationship runs, and a worked example. Read it before authoring.
3. **Read the repository and author the draft.** Cite the exact file and line range
   behind every element and relationship you call `grounded`.
4. **Check it with `diagram_check_draft`, passing `workspaceDir`.** Nothing is written,
   so call it as often as you like. **A refused `diagram_create` also writes nothing and
   does not consume the diagram name** — nothing here is one-shot, and you can call it
   again with the same name. Check because it is quicker and because it reports what it
   checked, not because a mistake is expensive. **Pass `workspaceDir` or your citations
   are not read.** The mistake you genuinely cannot repair is a citation that *resolves
   but points at the wrong code*: no tool can catch that, and a saved diagram is never
   overwritten. So read the lines you cite.
5. **Call `diagram_create`.** You get a saved `.gp.json`, its `.svg`, and an editor link.
   Present the link to the user as a clickable **Open in the GraphPilot editor**.

**If `diagram_create` warns that the picture is hard to read, that one is not yours.**
GraphPilot places every node and every end label, so overlapping text is a limit of its
layout, not a mistake in your draft — and no check could have told you sooner, because it
is measured from the drawn SVG. **Do not reword, drop or restructure anything to clear
it.** Hosts have flattened guards to `yes`/`no` and demoted decisions to notes chasing
these, which changes what the diagram says to fix how it looks. Report it, give the user
the editor link, and let them drag a label — they can see the picture and you cannot.

## Changing a diagram that already exists

**A saved diagram is never overwritten by `diagram_create`.** If the name is taken, the
diagram is already there — and somebody may have opened it in the editor since, moved
things, renamed one, added a note. Re-creating cannot happen, and re-materializing would
recompute every position, which the person experiences as their work being destroyed.

So editing is its own path, and it is two calls:

1. **`diagram_read`** — writes a draft file for you to edit in place, computed from the
   saved diagram, so it includes anything a person added in the browser.
2. **`diagram_update`** — merges your edited file back.

**Always read first.** An update submits the *whole* desired state: an element your file
does not mention is removed. A draft you wrote from scratch omits everything you never knew
about, and omission deletes. If the diagram changed between your read and your write, the
update refuses and asks you to read again — that refusal is the only thing standing between
a stale draft and somebody's afternoon.

You will not see positions, sizes or routes in that file, and you never author them. They
are preserved by id when you write. What you leave alone cannot be lost.

Append your ask to `requests`, at the end. The earlier entries are the record of why the
diagram looks the way it does, and they must come back unchanged.

**Nothing here deletes a diagram.** Removing one is the user's call, in their own
repository.

**GraphPilot writes into the repository you are diagramming**, under
`<workspaceDir>/.graphpilot/` — the diagram, its SVG, the draft that produced it, and one
line per `diagram_create` attempt in `attempts.jsonl`, which records names, codes and
counts and never the draft itself. Nothing outside that folder is touched, and nothing at
all is written by a refusal. If you were told not to modify the codebase, this is the
exception: it is the output you were asked for. The folder may need adding to
`.gitignore`, which is the user's call and worth mentioning to them.

## What you own, and what you do not

You own the semantics: which elements exist, what relates to what, the relationship kind,
labels, roles, multiplicities, evidence, and assumptions.

GraphPilot owns the mechanics: node and edge JSON, relationship-end objects, markers, line
styles, positions, sizes, validation, and files. **Never author positions, styles, or
relationship-end objects** — say `composition, source, target, sourceRole` and the end is
built for you.

## Authority is a field, not a choice of tool

- `as_implemented` — the diagram reflects the current source. Every element cites
  evidence, and freshness is checked against the exact lines you cited.
- `conceptual` — a design that makes no claim about this repository. Cite nothing.

## Honesty rules

- **`assurance` follows `authority`, on every element and relationship.** In an
  `as_implemented` diagram each one is `grounded` (needs `evidenceRefs`) or `assumed`
  (needs an `assumptionRef`). In a `conceptual` diagram **every** one is `conceptual` —
  there is no repository to cite, so the other two are refused.
- An assumption may never be presented as repository fact.
- Prefer omission to a guess: an absent multiplicity is honest, an invented `1..1` is not.
  **This outranks any field the contract describes as expected.** A composition asks for
  the part's role because it is usually knowable and worth drawing — but if the source
  does not name it, leave it out. Nothing that says "state this" is asking you to invent.
- Prefer the weaker true relationship. If the source shows two things interact but not
  that one owns the other, that is a `dependency`, not a `composition`.
- Say what the source does not establish in your reply to the user. A diagram cannot show
  a gap, and resolving one silently is the failure this whole contract exists to prevent.

## What the diagram keeps

`requests` — the ask, verbatim — is stored **inside** the saved `.gp.json`, alongside
evidence and per-element assurance. It is the only durable record of why the diagram looks
the way it does, and a later reader who never saw this conversation has nothing else.

Everything else you reason about on the way there is yours to deliver in your reply. The
diagram is read by people who did not commission it, so it carries the citation rather
than the essay.

So they are yours to deliver. **After a successful create, tell the user what you were
unsure about, what you assumed and why, and what you decided to leave out** — then ask
whether any of it should change the diagram. A `.gp.json` nobody questions, built on an
assumption nobody saw, is the failure this whole tool exists to avoid.

Your draft is kept beside the diagram at `.graphpilot/drafts/<diagramName>.draft.json`, so
the reasoning survives for whoever debugs the diagram later. That is a trace, not a
delivery: nobody reads it unless something is already wrong.

## If the draft is refused

Every reason **at the stage that failed** comes back at once, each with the exact JSON
path. Fix them all before calling again — never resubmit one fix at a time.

Checking runs in stages, and a later stage cannot see past an earlier failure:

1. **Shape** — is it a valid draft document at all? Missing fields, wrong types, bad enums.
2. **Meaning** — do the ids resolve, does every assumption get referenced, is the notation
   legal for this type?
3. **Evidence** — can each cited region actually be read?

So a field that is both missing *and* would fail a rule reports twice, one stage apart:
supply it, and the next call tells you the value is wrong. That is two rounds by design,
not a contradiction — and **neither round costs anything**, because a refusal writes no
file and does not consume the name. `diagram_check_draft` runs the same stages, so find
out there if you prefer; a refused `diagram_create` tells you exactly the same thing.

The `code` names the thing to fix first.
"""


@mcp.tool()
@_sanitize_unexpected_errors("diagram_workflow")
async def diagram_workflow() -> CallToolResult:
    """Call this first. Explains how to author a diagram draft and create a diagram.

    Instructions only: reads no source, writes no file, and executes nothing.
    """
    return _prose_result(_WORKFLOW)


@mcp.tool()
@_sanitize_unexpected_errors("diagram_get_authoring_contract")
async def diagram_get_authoring_contract(
    diagramType: Annotated[
        str,
        Field(
            description=_DIAGRAM_TYPE_ARG_DESCRIPTION,
            json_schema_extra={"enum": list(_SUPPORTED_TYPES)},
        ),
    ],
) -> dict:
    """Return how to author a draft for one diagram type, with a worked example.

    Read-only. The vocabulary, relationship directions, and required fields are derived
    from the same tables that reject an invalid draft, so this cannot tell you one thing
    and `diagram_create` refuse you for another.
    """
    try:
        contract = _authoring_contract_service.build(diagramType)
    except ValueError as exc:
        return _error("unsupported_diagram_type", str(exc))
    return _markdown_result(
        _authoring_contract_service.render_summary(contract),
        contract,
    )


@mcp.tool()
@_sanitize_unexpected_errors("diagram_create")
async def diagram_create(
    workspaceDir: Annotated[
        str,
        Field(description="Absolute path to the local workspace root. Everything is read from and written beneath it."),
    ],
    draft: Annotated[
        dict,
        Field(
            description=(
                "Complete inline graphpilot.draft.v1 document: diagramName, diagramType, "
                "authority, requests, evidence, elements, relationships. `diagramName` names the file "
                "and is a lowercase hyphenated slug of at most 64 characters. Call "
                "diagram_get_authoring_contract for the exact "
                "shape and the diagram type's vocabulary. The diagram carries its own "
                "evidence; the draft is kept beside it as a trace, so a diagram that "
                "turns out to be wrong can be traced back to what was claimed."
            )
        ),
    ],
) -> dict:
    """Materialize one authored draft into a new saved diagram, then render it.

    Deterministic and provider-free: you supply the semantics, GraphPilot supplies the
    notation, layout, validation, and files. Refuses to overwrite an existing diagram.
    """
    try:
        _workspace_service(workspaceDir)
    except ValueError as exc:
        return _error("invalid_workspace", str(exc))

    try:
        result = _creation_service.create(workspaceDir, draft)
    except DraftRefused as refusal:
        findings = [finding.to_dict() for finding in refusal.findings]
        return _error(
            refusal.code,
            f"The draft was refused with {len(findings)} finding(s); "
            "fix them all and call again.",
            details={"findings": findings},
            retryable=False,
            text=_findings_markdown(
                findings,
                f"**Refused — {len(findings)} finding(s).** Nothing was written and the "
                "name is still free. Fix them all, then call again.",
            ),
        )
    except DiagramAlreadyExists as exists:
        return _error(
            "diagram_exists",
            "A diagram with that name already exists and is never overwritten — it may "
            "carry edits this draft does not know about. Choose another `diagramName`. "
            "Removing the existing one is the user's decision to make, not yours.",
            details={"diagramPath": exists.diagram_path.as_posix()},
            retryable=False,
        )
    except (UnsafePathError, WorkspaceResolutionError) as exc:
        return _error("unsafe_path", str(exc))

    edit_url = _edit_url(result.diagram_path)
    structured = {
        "outcome": "created",
        "diagramName": draft["diagramName"],
        "diagramType": result.diagram["diagramType"],
        "diagramPath": result.diagram_path.as_posix(),
        "svgPath": result.svg_path.as_posix() if result.svg_path else None,
        "draftPath": result.draft_path.as_posix() if result.draft_path else None,
        "editUrl": edit_url,
        "nodeCount": result.node_count,
        "edgeCount": result.edge_count,
        "assurance": {
            "authority": result.diagram["metadata"].get("authority"),
            "assumedElementIds": result.diagram["metadata"]
            .get("assurance", {})
            .get("assumedElementIds", []),
        },
        "operationWarnings": [dict(warning) for warning in result.warnings],
    }
    lines = [
        f"Created **{draft['diagramName']}** "
        f"({result.node_count} nodes, {result.edge_count} edges).",
        "",
        f"[Open in the GraphPilot editor]({edit_url})",
        "",
        f"- Diagram: `{result.diagram_path.as_posix()}`",
    ]
    if result.svg_path:
        lines.append(f"- SVG: `{result.svg_path.as_posix()}`")
    for warning in result.warnings:
        lines.append(f"- Warning ({warning['code']}): {warning['message']}")
    return _markdown_result("\n".join(lines), structured)


@mcp.tool()
@_sanitize_unexpected_errors("diagram_read")
async def diagram_read(
    workspaceDir: Annotated[
        str,
        Field(description="Absolute path to the local workspace root."),
    ],
    diagramName: Annotated[
        str,
        Field(description="The `diagramName` the diagram was created with."),
    ],
) -> dict:
    """Open a saved diagram for editing. Writes a draft file for you to edit in place.

    **Call this before `diagram_update`, every time.** The draft it writes is computed from
    the saved diagram, so it includes anything a person has added in the browser since the
    diagram was made — and a write that did not start here would delete all of it, because
    an id your draft does not mention is an id the write removes.

    What you get back is a **path, not a document**: edit the file, then call
    `diagram_update`. Nothing you leave alone can be lost, which is not true of a document
    you have to echo back.

    The draft holds semantics only. No positions, sizes, routes or styles — those are
    preserved by id when you write, and you never author them.

    Append your ask to `requests`, at the end. The earlier rows are the record of why this
    diagram looks the way it does and must come back unchanged.
    """
    try:
        _workspace_service(workspaceDir)
    except ValueError as exc:
        return _error("invalid_workspace", str(exc))

    try:
        result = _edit_service.read(workspaceDir, diagramName)
    except EditRefused as refusal:
        return _error(refusal.code, refusal.message, details=refusal.details,
                      retryable=False)
    except (UnsafePathError, WorkspaceResolutionError) as exc:
        return _error("unsafe_path", str(exc))

    structured = {
        "outcome": "opened",
        "diagramName": diagramName,
        "diagramType": result.draft["diagramType"],
        "draftPath": result.draft_path.as_posix(),
        "diagramPath": result.diagram_path.as_posix(),
        "elementCount": result.element_count,
        "relationshipCount": result.relationship_count,
        "requestCount": len(result.draft.get("requests") or ()),
        "editUrl": _edit_url(result.diagram_path),
    }
    return _markdown_result(
        "\n".join([
            f"Opened **{diagramName}** for editing "
            f"({result.element_count} elements, {result.relationship_count} relationships).",
            "",
            f"Edit this file, then call `diagram_update`:",
            f"`{result.draft_path.as_posix()}`",
            "",
            "- Change what you need and leave the rest alone.",
            "- Append one entry to `requests`, saying what you are about to do.",
            "- Do not touch `basis` — it records what this read saw.",
            "- An element you delete from the file is deleted from the diagram.",
        ]),
        structured,
    )


@mcp.tool()
@_sanitize_unexpected_errors("diagram_update")
async def diagram_update(
    workspaceDir: Annotated[
        str,
        Field(description="Absolute path to the local workspace root."),
    ],
    draft: Annotated[
        dict,
        Field(
            description=(
                "The draft file `diagram_read` wrote, with your edits. It is the whole "
                "desired state: an element you leave out is removed from the diagram. "
                "Keep `basis` exactly as you found it, and append one entry to `requests`."
            )
        ),
    ],
) -> dict:
    """Write an edited draft back over a saved diagram, keeping what the draft cannot say.

    Positions, sizes, routes, hand-typed descriptions and the viewport all survive, copied
    across by id — so a person's arrangement is not destroyed by a change to one label.
    Anything new is placed against the arrangement that is already there.

    **Whole desired state.** An id absent from `elements` is deleted, including something a
    person drew. The result names everything it removed; pass that on.

    Refuses if the diagram changed after your read: somebody saved in the browser, and your
    draft does not know what they added. Read it again and re-apply your change.
    """
    try:
        _workspace_service(workspaceDir)
    except ValueError as exc:
        return _error("invalid_workspace", str(exc))

    try:
        result = _update_service.update(workspaceDir, draft)
    except UpdateRefused as refusal:
        findings = [finding.to_dict() for finding in refusal.findings]
        if findings:
            return _error(
                refusal.code,
                f"The draft was refused with {len(findings)} finding(s); "
                "fix them all and call again.",
                details={"findings": findings},
                retryable=False,
                text=_findings_markdown(
                    findings,
                    f"**Refused — {len(findings)} finding(s).** The diagram is unchanged "
                    "and your draft file is still there. Fix them, then call again.",
                ),
            )
        return _error(refusal.code, refusal.message, retryable=False)
    except (UnsafePathError, WorkspaceResolutionError) as exc:
        return _error("unsafe_path", str(exc))

    removed = [item.as_dict() for item in result.removed]
    structured = {
        "outcome": "updated",
        "diagramName": draft["diagramName"],
        "diagramPath": result.diagram_path.as_posix(),
        "svgPath": result.svg_path.as_posix() if result.svg_path else None,
        "editUrl": _edit_url(result.diagram_path),
        "removed": removed,
        "added": list(result.added_ids),
        "historyPath": result.history_path.as_posix() if result.history_path else None,
        "operationWarnings": result.warnings,
    }
    lines = [
        f"Updated **{draft['diagramName']}**.",
        "",
        f"[Open in the GraphPilot editor]({_edit_url(result.diagram_path)})",
    ]
    if result.svg_path:
        lines.append(f"- SVG redrawn: `{result.svg_path.as_posix()}`")
    if result.added_ids:
        lines.append(f"- Added: {', '.join(result.added_ids)}")
    if removed:
        lines.append("- **Removed** — tell the user:")
        for item in removed:
            hand = " *(drawn by a person)*" if item.get("drawnBy") == "user" else ""
            lines.append(f"  - `{item['id']}` {item['label']}{hand}")
            # Prose a person typed that no draft could show them. Without this an agent
            # reports "removed Frame" and a decision record naming a colleague is gone.
            for text in item.get("lostText") or ():
                lines.append(f"    - text lost with it: \u201c{text}\u201d")
    for warning in result.warnings:
        lines.append(f"- Warning ({warning['code']}): {warning['message']}")
    return _markdown_result("\n".join(lines), structured)


@mcp.tool()
@_sanitize_unexpected_errors("diagram_check_draft")
async def diagram_check_draft(
    draft: Annotated[
        dict,
        Field(
            description=(
                "A graphpilot.draft.v1 document, complete or in progress. Nothing is "
                "written."
            )
        ),
    ],
    workspaceDir: Annotated[
        str,
        Field(
            description=(
                "Absolute path to the repository the draft cites. Optional, and strongly "
                "recommended for an as_implemented draft: with it, every citation is read "
                "and checked here instead of at create time. Read-only — nothing is "
                "written to it."
            )
        ),
    ] = "",
) -> dict:
    """Check a draft without creating anything. No files are written.

    Runs the same validator as `diagram_create`, so a draft that passes here would be
    accepted there. **A refused `diagram_create` also writes nothing and does not consume
    the diagram name.** This tool is a convenience, not a safety net: use it because it is
    faster than a create and because it reports what it checked, not because attempting
    the real thing is risky.

    **Pass `workspaceDir` when the draft cites a repository**, or the citations are the
    one thing left unchecked. A corpus run shipped three diagrams whose citations named a
    symbol seventeen lines outside the range they pointed at, all accepted, none noticed.
    Note the limit of any such check: it proves a cited region *exists*, never that it
    says what you claimed.

    Call this as often as you like while authoring.
    """
    result = _draft_validation_service.validate(draft)
    findings = [finding.to_dict() for finding in result.findings]

    checked = ["schema", "vocabulary", "notation", "references", "assurance"]
    not_checked = ["the diagram name is free"]
    digests: dict = {}
    if workspaceDir and not findings:
        # Only worth resolving once the draft is structurally sound: evidence findings on
        # a malformed draft are noise, and the schema stage gates them at create time too.
        try:
            storage = WorkspaceStorageService(workspaceDir)
            resolution = EvidenceService(storage).resolve(draft.get("evidence") or ())
            findings += [finding.to_dict() for finding in resolution.findings]
            checked.append("evidence locators resolve")
            if resolution.valid:
                digests = dict(resolution.digests())
        except (UnsafePathError, WorkspaceResolutionError, OSError) as exc:
            not_checked.append(f"evidence locators resolve ({exc})")
    elif workspaceDir:
        not_checked.append("evidence locators resolve (fix the findings below first)")
    else:
        not_checked.append("evidence locators resolve (pass workspaceDir to check them)")

    warnings: list = []
    if not findings:
        # Real digests where the citations were just read, placeholders otherwise. Either
        # way they reach only `metadata`, never a label, so the warnings are the same.
        # Everything the render-readiness layer knows is a function of the draft, so a
        # host can be told here rather than after the write. Never fatal: a preview that
        # cannot be built must not turn a sound draft into a failed check.
        try:
            warnings = list(
                _creation_service.preview_warnings(draft, evidence_digests=digests)
            )
            # Narrowed deliberately. The fit check reads `nodes`, so it covers element
            # labels; a host got a clipped *edge* label — `«extend» [an uncancelled hold
            # exists for th…` — through a clean check and met it at create. A `checked`
            # list that overstates is worse than a shorter honest one.
            checked.append("element label lengths, and whether each fits its element")
            not_checked.append(
                "a relationship's label — a composed one (`«extend» [condition]`, "
                "`[guard]`, `role 0..*`) is only measured once it is drawn"
            )
        except Exception:  # noqa: BLE001 - advisory only; the draft itself already passed
            logger.exception("Could not preview render warnings for a checked draft")
            not_checked.append("label lengths (the preview could not be built)")
    not_checked.append(
        "whether labels overlap, or spill outside the element they belong to, once "
        "drawn — measured from the rendered picture, so it arrives with `diagram_create`"
    )

    valid = not findings
    structured = {
        "valid": valid,
        "findingCount": len(findings),
        "findings": findings,
        "warnings": warnings,
        "checked": checked,
        "notChecked": not_checked,
    }
    if valid:
        lines = [
            "This draft would be accepted. "
            + (
                "Citations were read and resolve. Only the diagram name is still checked "
                "by `diagram_create`."
                if "evidence locators resolve" in checked
                else "Evidence locators and the diagram name are still checked by "
                "`diagram_create` — pass `workspaceDir` to check the citations here."
            )
        ]
        if warnings:
            lines += [
                "",
                f"**{len(warnings)} warning(s)** — it would be accepted like this, and "
                "these are worth fixing first, because a saved diagram is never "
                "overwritten:",
                "",
            ]
            # A warning is measured on the *built* diagram, so it often has no path into
            # the draft you wrote — the structural critic names the offending item in its
            # message instead. Printing `at ``` for those was worse than printing nothing.
            lines += [
                f"- `{w['code']}` — {w['message']}"
                + (f" (in the built diagram at `{w['path']}`)" if w.get("path") else "")
                for w in warnings[:40]
            ]
        return _markdown_result("\n".join(lines), structured)
    return _markdown_result(
        _findings_markdown(
            findings, f"**{len(findings)} finding(s).** Fix them all, then check again."
        ),
        structured,
    )


@mcp.tool()
@_sanitize_unexpected_errors("diagram_validate")
async def diagram_validate(
    diagram: Annotated[
        dict,
        Field(description="Inline canonical GraphPilot diagram JSON (the full document: nodes, edges, viewport, metadata)."),
    ],
    workspaceDir: Annotated[
        Optional[str],
        Field(
            description=(
                "Absolute path to the repository the diagram describes. Supply it and "
                "every citation in `metadata.evidence` is re-read and re-hashed, so the "
                "answer covers whether the diagram is still true of the code. Omit it and "
                "only the document's own structure is checked."
            )
        ),
    ] = None,
) -> dict:
    """Validate a GraphPilot diagram, and optionally check it is still true.

    Read-only; writes no files.

    Without *workspaceDir* this checks the document against the canonical schema and the
    semantic rules — that it is a well-formed diagram, not that it is a correct one.

    **With *workspaceDir* it also re-reads every cited region and compares the digest**
    against the one recorded when the diagram was created. That is the question a diagram
    is for: code moves, and a diagram whose citations have drifted is confidently wrong
    rather than obviously stale. The same idiom as `diagram_check_draft` — the argument
    that turns citation checking on is spelled the same way and means the same thing.

    Drift is reported as a warning, not a failure. The diagram was true when it was made,
    the code changed underneath it, and neither of those is an error in the document.
    """
    try:
        result = _validation_service.validate(diagram).to_dict()
    except (FileNotFoundError, OSError, ValueError) as exc:
        # Defensive: a missing/invalid bundled schema would otherwise crash the tool.
        return _error("validation_unavailable", str(exc))

    if not workspaceDir:
        result["checkedCitations"] = False
        return _structured_result(_validation_summary(result), result)

    # `EvidenceService.recheck` existed and no surface reached it, while
    # `03-design/03-validation.md` listed evidence freshness as something GraphPilot
    # checks. Found as `a5.f9`: a built capability nobody wired up, so the promise was
    # false and the code looked dead.
    recorded = ((diagram.get("metadata") or {}).get("evidence")) or []
    try:
        storage = WorkspaceStorageService(workspaceDir)
    except (UnsafePathError, WorkspaceResolutionError) as exc:
        return _error("unsafe_path", str(exc))
    drifted = [f.to_dict() for f in EvidenceService(storage).recheck(recorded)]
    result["checkedCitations"] = True
    result["citationsChecked"] = len(recorded)
    result["staleCitations"] = drifted
    return _structured_result(_validation_summary(result), result)


@mcp.tool()
@_sanitize_unexpected_errors("diagram_render")
async def diagram_render(
    diagramPath: Annotated[
        Optional[str],
        Field(description="Absolute path to an existing saved <name>.gp.json (path mode); the sibling <name>.svg (or <name>.png when format='png') is overwritten."),
    ] = None,
    diagram: Annotated[
        Optional[dict],
        Field(description="Inline canonical GraphPilot diagram JSON (inline mode); nothing is read from or written to disk."),
    ] = None,
    format: Annotated[
        str,
        Field(
            description="Output format: 'svg' (default) or 'png'. 'png' requires diagramPath and writes/overwrites the sibling <name>.png (the explicit image-file save).",
            json_schema_extra={"enum": ["svg", "png"]},
        ),
    ] = "svg",
) -> dict:
    """Render a GraphPilot diagram to SVG (inline or file) or save a PNG file.

    SVG modes: inline (*diagram*) returns ``{"svg": ...}`` without touching the
    filesystem (mirroring the path-free ``POST /api/diagrams/render`` HTTP endpoint);
    path mode (*diagramPath*) overwrites the sibling ``<name>.svg`` and returns
    ``{"svgPath": ...}``.

    PNG mode (``format='png'``) is the explicit "save the image file" action: it
    **requires *diagramPath***, writes the full-resolution sibling ``<name>.png``
    (rasterized from the same SVG via ``resvg``), and returns ``{"pngPath": ...}``
    with a short Markdown confirmation.

    Provide exactly one of *diagram* or *diagramPath*. Missing / unsafe / malformed
    inputs and render failures return the common error shape.

    All three success modes answer in ``structuredContent``, which is what
    `01-diagram-tools.md` publishes. Two of them used to return a bare dict instead:
    FastMCP then serialized it into ``content`` and left ``structuredContent`` null, so a
    host reading the documented ``structuredContent.svgPath`` found nothing — while the
    PNG branch of the same tool, one line below, worked. Only visible over the real
    transport; calling the function directly returns the dict either way.
    """
    fmt = (format or "svg").lower()
    if fmt not in ("svg", "png"):
        return _error("invalid_arguments", "format must be 'svg' or 'png'.")
    if diagram is not None and diagramPath is not None:
        return _error("invalid_arguments", "Provide either 'diagram' or 'diagramPath', not both.")
    # PNG is a file-save action: it needs a diagramPath to write <name>.png beside.
    if fmt == "png" and diagram is not None:
        return _error("invalid_arguments", "format='png' requires 'diagramPath' (the PNG is written beside the saved diagram).")

    # Inline mode (SVG only): render in-memory and return the SVG string (no file I/O).
    if diagram is not None:
        try:
            svg = _render_service.to_svg(diagram)
        except DiagramRenderServiceError as exc:
            return _error("render_failed", str(exc))
        except Exception as exc:  # noqa: BLE001 — inline JSON is unvalidated; never crash the tool
            logger.warning("diagram_render (inline) failed: %s", exc, exc_info=True)
            return _error("render_failed", f"Could not render the diagram: {exc}")
        # `_structured_result` rather than `_markdown_result`: the SVG can be tens of
        # kilobytes, and `_markdown_result` would put it in `content` as well.
        return _structured_result(f"Rendered inline SVG ({len(svg)} characters).", {"svg": svg})

    # Path mode: load the saved diagram and write the sibling artifact.
    if diagramPath is None:
        return _error("invalid_arguments", "Provide 'diagram' (inline JSON) or 'diagramPath'.")
    try:
        artifact_path = (
            _render_service.render_png(diagramPath) if fmt == "png" else _render_service.render(diagramPath)
        )
    except WorkspaceResolutionError as exc:
        return _error("workspace_resolution_error", str(exc))
    except UnsafePathError as exc:
        return _error("unsafe_path", str(exc))
    except DiagramNotFoundError as exc:
        return _error("diagram_not_found", str(exc))
    except InvalidDiagramJSONError as exc:
        return _error("invalid_diagram_json", str(exc))
    except DiagramRenderServiceError as exc:
        return _error("render_failed", str(exc))
    except OSError:
        return _error("render_failed", "Could not read or write the diagram artifact.")
    if fmt == "png":
        return _markdown_result(f"Saved PNG: `{artifact_path}`", {"pngPath": str(artifact_path)})
    return _markdown_result(f"Saved SVG: `{artifact_path}`", {"svgPath": str(artifact_path)})


if __name__ == "__main__":
    mcp.run(transport="stdio")
