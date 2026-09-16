"""``render_example_gallery`` — offline batch-review contact sheet.

Renders **every** curated example (all supported types) to inline SVG
via :meth:`DiagramRenderService.to_svg` and emits **one** self-contained static HTML
page. Each card shows the rendered diagram, its goal, its tags
(``source`` / ``register`` / ``complexity`` / ``reviewStatus`` / …), and its validity +
render status; a per-type **vocabulary-coverage** panel surfaces which ``semanticType``s
are still missing from the pool. The whole answer-key library is therefore reviewable —
for correctness, realism, *and* completeness — at a glance, instead of opening every
``output.gp.json`` individually.

Offline and key-free (``drawsvg`` only — already pinned). Output goes to the
gitignored ``backend/review_galleries/`` directory::

    python manage.py render_example_gallery
    python manage.py render_example_gallery --types activity_diagram --pools eval
    python manage.py render_example_gallery --out some/dir --open

Method + rationale: ``docs/02-design-and-features/06-answer-key-generation-design.md``.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import webbrowser
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from typing import Any, Dict, List, Mapping, Optional, Tuple

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from services.diagrams.rendering.diagram_render_service import DiagramRenderService, DiagramRenderServiceError
from services.diagrams.catalog.diagram_types import SUPPORTED_DIAGRAM_TYPES, get_type_profile
from services.diagrams.validation.diagram_validation_service import DiagramValidationService
from services.diagrams.validation.structural_constraints import check_structural_constraints
from services.diagrams.validation.validation_contract import Severity
from services.diagrams.layout.diagram_layout_service import DiagramLayoutService
from services.diagrams.rendering.legibility import measure
from operations.edited_examples import load_scenario, replay
from services.drafts.draft_projection_service import project
from services.drafts.evidence_service import EvidenceService
from services.materialization.faithfulness import check as faithfulness_check
from services.materialization.materializer import materialize
from services.shared.workspace_storage_service import WorkspaceStorageService

#: Every example lives under `assets/blueprints/<type>/examples/<pool>/`. The pools are
#: four reasons an example exists: an answer proves the renderer, a generated diagram
#: proves the contract against a real repository, a training example is what
#: `diagram_get_authoring_contract` serves to a host, and an edited pair proves that
#: changing a diagram does not destroy the arrangement somebody made.
#:
#: `edited` is the one pool whose card is not a single picture, because the thing worth
#: reviewing is not either diagram on its own — it is what changed between them and, more
#: importantly, what did not.
POOLS: Tuple[str, ...] = ("answers", "generated", "training", "edited")

#: What each pool is for, shown above its cards so a reviewer knows which question to ask.
_POOL_PURPOSE = {
    "answers": "conceptual, deterministic from their drafts — these prove the renderer",
    "generated": "authored by a host from a real repository — these prove the contract",
    "training": "what <code>diagram_get_authoring_contract</code> serves to a host",
    "edited": "a person arranged it, then a host changed it — look at what did <b>not</b> move",
}

#: Reviewed most often first. `answers` is the largest pool and the least often looked at
#: on purpose: a test asserts over all 36 on every run, so a person reads them only after
#: a rendering change. The other two are only ever judged by eye.
_REVIEW_ORDER: Tuple[str, ...] = ("edited", "training", "generated", "answers")

#: How a card's picture came to exist. Only the first is evidence about the current code.
PROVENANCE_MATERIALIZED = "materialized"
#: No draft exists, so nothing can rebuild it — the saved document is drawn as it is.
PROVENANCE_STORED = "stored"
#: A draft exists and its citations no longer resolve, so the diagram cannot be rebuilt
#: from it. Kept distinct from `stored` because it is not an absence — it is a defect, and
#: the whole point of the page is that a reviewer sees one.
PROVENANCE_MISCITED = "miscited"
PROVENANCE_FAILED = "failed"

#: What `--regen` can rewrite. `eval` is the two conceptual pools; `generated` is the
#: corpus pool, whose drafts come from a host rather than from us.
REGEN_CHOICES: Tuple[str, ...] = ("eval", "generated", "edited", "all")
_XML_PROLOG = re.compile(r"^\s*<\?xml[^>]*\?>\s*")
# Tags shown in the header/badge are not repeated as chips.
_BADGE_TAGS = {"reviewstatus"}
# Preferred display order for the tag chips; unknown keys follow, sorted.
_TAG_ORDER = [
    "source", "reviewer", "domain", "structure", "size",
    "register", "complexity", "paraphraseSet", "diagramType",
]


@dataclass
class ExampleCard:
    diagram_type: str
    pool: str
    name: str
    svg: str
    #: What the draft said it set out to show, which is what a reviewer judges against.
    #: Deliberately not `request.original`: the ask is not an input to anything here.
    goal: str
    tags: List[Tuple[str, str]]
    review_status: str
    node_count: int
    edge_count: int
    valid: bool
    errors: List[str]
    struct_issues: List[str]
    render_ok: bool
    render_error: str
    #: Absolute path of the saved `.gp.json`, so a reviewer can open it in the editor and
    #: correct it. Empty when the card is not backed by a file the editor could load.
    source_path: str = ""
    #: The source documents behind this card, shown on demand. A picture alone answers
    #: "does it look right" and never "is it right" — what the host actually claimed is
    #: in the draft, and the canonical JSON is where a notation rule can be checked.
    draft_json: str = ""
    diagram_json: str = ""
    #: `edited` only. The authored scenario — the create, the arrangement, the edit — which
    #: is not a draft and must not be offered as one: a source viewer that labels it
    #: "Draft" hands a reader a document no host would ever submit.
    scenario_json: str = ""
    #: `edited` only. The diagram as the person left it, so both halves of the pair can be
    #: read as JSON and not only looked at. A picture shows that a node moved; only the
    #: documents show that a `description` nobody mentioned came through untouched.
    before_json: str = ""
    #: `edited` only. The draft `diagram_read` handed the host, and the draft the host sent
    #: back. **The submitted one is the real artifact of an edit** — whole desired state,
    #: exactly what `diagram_update` receives. Without it a reviewer can see that the
    #: diagram changed and not whether the host authored the change correctly.
    read_draft_json: str = ""
    submitted_draft_json: str = ""
    #: `edited` only. The saved path of the *before* diagram, so a reviewer can open either
    #: half in the editor. Both halves are real files on disk, and a person tidying the
    #: result of an edit is the whole reason the merge preserves what it preserves.
    before_path: str = ""
    #: The ask that produced the edit, shown on the card rather than buried in the
    #: scenario — it is the one line that explains why the two pictures differ.
    edit_request: str = ""
    #: How this card's picture was produced by *this* run. The distinction that matters is
    #: not where an example came from but whether the page can still make it: a card the
    #: pipeline built is evidence about the current code, and a card read off disk is only
    #: evidence that a file parses.
    provenance: str = PROVENANCE_MATERIALIZED
    #: What the draft declared and the diagram does not carry. Always **our** defect:
    #: the draft was accepted, so a loss here happened after the host's work was done.
    losses: List[str] = field(default_factory=list)
    #: Unreadable or misplaced strings in *this* diagram. The page total answers "is the
    #: renderer getting better"; only the per-card number answers "which one do I open",
    #: which is the question a reviewer actually has.
    illegible: int = 0
    text_count: int = 0
    #: `edited` only. The same diagram before the host touched it, drawn beside the after
    #: — because neither picture alone shows the thing being reviewed, which is what
    #: survived. Empty for every other pool, and the card falls back to one picture.
    before_svg: str = ""
    #: What the write reported. `held` is the number a reviewer checks first: an element
    #: that moved without the host mentioning it is indistinguishable, to the person who
    #: arranged the diagram, from their work being destroyed.
    held: int = 0
    moved: List[str] = field(default_factory=list)
    added: List[str] = field(default_factory=list)
    removed: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TypeCoverage:
    diagram_type: str
    node_total: int
    node_missing: List[str]
    edge_total: int
    edge_missing: List[str]

    @property
    def has_gap(self) -> bool:
        return bool(self.node_missing or self.edge_missing)


class Command(BaseCommand):
    help = "Render all curated examples + vocabulary coverage to one offline HTML contact sheet."

    def add_arguments(self, parser):
        parser.add_argument("--types", default="", help="comma-separated diagram types; empty = all")
        parser.add_argument(
            "--pools", default="",
            help=f"comma-separated pools ({', '.join(POOLS)}); empty = all",
        )
        parser.add_argument("--out", default="", help="output root (default: backend/review_galleries)")
        parser.add_argument(
            "--regen",
            choices=REGEN_CHOICES,
            default="",
            help="rewrite examples on disk before rendering. `eval` rematerializes the "
                 "answers and training examples from their drafts; `generated` pulls the "
                 "newest host drafts out of the corpus repositories and materializes "
                 "those; `edited` replays each edit scenario and rewrites both halves of "
                 "its before/after pair; `all` does every one. Without it nothing on disk "
                 "is touched — the page is built in memory either way",
        )
        parser.add_argument(
            "--corpus",
            default="",
            help="where the corpus repositories live, for --regen generated "
                 "(default: ../GraphPilot-Test-Repos beside this repository)",
        )
        parser.add_argument(
            "--no-open",
            dest="open_browser",
            action="store_false",
            help="do not open the page in a browser (it opens by default — the whole point "
                 "of the page is that somebody looks at it)",
        )
        parser.set_defaults(open_browser=True)
        parser.add_argument(
            "--keep",
            action="store_true",
            help="keep earlier runs instead of replacing them (they are normally deleted, "
                 "since a gallery is regenerated in seconds and two of them only invite "
                 "reviewing the stale one)",
        )

    def _announce(self, index: Path, summary: str) -> None:
        """Say where the page is, as something that can actually be opened.

        A bare filesystem path is not clickable in most terminals and the page is useless
        unless somebody looks at it, so print the URL form too. The landing page above it
        is rewritten each time, so whichever gallery was just built can be reached from
        the other without hunting through timestamped folders.
        """
        self.stdout.write(self.style.SUCCESS(f"Wrote {index} ({summary})."))
        self.stdout.write(self.style.HTTP_INFO(f"  open:  {index.resolve().as_uri()}"))

    def _maybe_open(self, index: Path, opts) -> None:
        """Open the page, unless nobody is there to look at it.

        Defaulting `--open` to on is right for a person and wrong for everything else: the
        gallery tests run this command against a temp directory that is deleted the moment
        they finish, so every suite run left dead browser tabs behind. A captured stdout
        means the caller is a test or a script, so the page is written and not opened.
        """
        if not opts["open_browser"]:
            return
        if not (hasattr(self.stdout, "isatty") and self.stdout.isatty()):
            return
        webbrowser.open(index.resolve().as_uri())

    def handle(self, *args, **opts):
        types = [t.strip() for t in opts["types"].split(",") if t.strip()] or list(SUPPORTED_DIAGRAM_TYPES)
        pools = [p.strip() for p in opts["pools"].split(",") if p.strip()] or list(POOLS)
        unknown_types = sorted(set(types) - set(SUPPORTED_DIAGRAM_TYPES))
        unknown_pools = sorted(set(pools) - set(POOLS))
        if unknown_types:
            raise CommandError(f"Unknown diagram type(s): {', '.join(unknown_types)}")
        if unknown_pools:
            raise CommandError(f"Unknown pool(s): {', '.join(unknown_pools)}")
        out_root = Path(opts["out"]) if opts["out"] else Path(settings.BASE_DIR) / "review_galleries"

        render = DiagramRenderService()
        validation = DiagramValidationService()
        layout = DiagramLayoutService()

        # Regeneration happens before the page is built, so what is rendered is what was
        # just written rather than the previous state of it.
        if opts["regen"] in ("eval", "all"):
            changed = regen_eval(layout, types)
            self.stdout.write(
                self.style.SUCCESS(f"  regen eval: rewrote {len(changed)} output(s)")
                if changed else "  regen eval: every output already matches its draft"
            )
            for name in changed[:12]:
                self.stdout.write(f"      {name}")
        if opts["regen"] in ("edited", "all"):
            changed = regen_edited()
            self.stdout.write(
                self.style.SUCCESS(f"  regen edited: rewrote {len(changed)} half-pair(s)")
            )
            for name in changed[:12]:
                self.stdout.write(f"      {name}")

        if opts["regen"] in ("generated", "all"):
            corpus = Path(opts["corpus"]) if opts["corpus"] else _default_corpus_root()
            if not corpus.is_dir():
                raise CommandError(
                    f"No corpus at {corpus}. Pass --corpus, or run the `corpus-run` skill first."
                )
            written, removed = regen_generated(layout, corpus)
            self.stdout.write(self.style.SUCCESS(
                f"  regen generated: {len(written)} from {corpus.name}, {len(removed)} removed"
            ))
            if not written:
                self.stdout.write(self.style.WARNING(
                    "      no drafts in the corpus — hosts must run first (see the "
                    "`corpus-run` skill); diagrams without a draft stay marked `stored`"
                ))

        cards: List[ExampleCard] = []
        coverage: List[TypeCoverage] = []
        legibility: Counter = Counter()
        for diagram_type in types:
            type_diagrams: List[dict] = []
            for pool in pools:
                for example_dir in _example_dirs(diagram_type, pool):
                    card, diagram = _build_card(
                        diagram_type,
                        pool,
                        example_dir,
                        render,
                        validation,
                        layout,
                    )
                    if diagram is not None:
                        type_diagrams.append(diagram)
                        if card.render_ok:
                            reading = measure(diagram, card.svg)
                            legibility.update(reading.counts)
                            card.text_count = reading.texts
                            card.illegible = reading.illegible
                    cards.append(card)
            coverage.append(_coverage(diagram_type, type_diagrams))

        meta = {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "gitCommit": _git_commit(),
            "count": len(cards),
            "types": types,
            "pools": pools,
            "layoutEngine": "pygraphviz-dot",
            "legibility": dict(legibility),
        }

        run_dir = _fresh_run_dir(out_root, opts["keep"])
        index = run_dir / "index.html"
        index.write_text(_render_html(cards, coverage, meta), encoding="utf-8")

        # Console summary: counts plus any vocabulary-coverage gap.
        invalid = [c for c in cards if not c.valid]
        unrendered = [c for c in cards if not c.render_ok]
        self._announce(index, f"{len(cards)} examples")
        if invalid:
            self.stdout.write(self.style.WARNING(f"  {len(invalid)} invalid: " + ", ".join(f"{c.diagram_type}/{c.pool}/{c.name}" for c in invalid)))
        if unrendered:
            self.stdout.write(self.style.WARNING(f"  {len(unrendered)} failed to render: " + ", ".join(f"{c.diagram_type}/{c.pool}/{c.name}" for c in unrendered)))
        for cov in coverage:
            if cov.has_gap:
                missing = ", ".join([f"node:{m}" for m in cov.node_missing] + [f"edge:{m}" for m in cov.edge_missing])
                self.stdout.write(self.style.WARNING(f"  [{cov.diagram_type}] coverage gap -> {missing}"))
        self._maybe_open(index, opts)

    # ---- generated diagrams --------------------------------------------------

# ---------------------------------------------------------------------------
# Data gathering
# ---------------------------------------------------------------------------


def _blueprints_dir() -> Path:
    return Path(getattr(settings, "BASE_DIR", Path.cwd())) / "assets" / "blueprints"


def _default_corpus_root() -> Path:
    """The corpus repositories, which sit beside this one rather than inside it.

    They are deliberately outside: a host reading them must see an ordinary application,
    not one that ships with the tool diagramming it.
    """
    return Path(settings.BASE_DIR).parent.parent / "GraphPilot-Test-Repos"


def _example_dirs(diagram_type: str, pool: str) -> List[Path]:
    base = _blueprints_dir() / diagram_type / "examples" / pool
    return [p.parent for p in sorted(base.glob("*/output.gp.json"))]


class EvidenceUnavailable(RuntimeError):
    """An `as_implemented` draft cites a repository this machine cannot read."""


def materialize_example(draft: Mapping[str, Any], layout, workspace: Optional[Path]) -> dict:
    """Run the pipeline `diagram_create` runs — the same `materialize`, not a lookalike.

    Going through `materialize` rather than `assemble_canonical` matters: it is what
    attaches `metadata.authority`, the assumed-element list, and the evidence records with
    their content digests. Calling the layer underneath produced a diagram that drew
    identically and carried none of its provenance, which is precisely the kind of
    near-miss this change exists to stop.

    A `conceptual` draft cites nothing, so it needs no workspace. An `as_implemented` one
    is only faithful if its citations can be read and digested, so a missing repository
    raises rather than quietly producing evidence records with no digest.
    """
    digests: Mapping[str, str] = {}
    if draft["authority"] == "as_implemented":
        if workspace is None or not workspace.is_dir():
            raise EvidenceUnavailable(
                f"{draft['diagramName']} cites a repository that is not on this machine "
                f"({workspace}). Its evidence digests cannot be recomputed."
            )
        resolution = EvidenceService(WorkspaceStorageService(str(workspace))).resolve(
            draft.get("evidence") or ()
        )
        if not resolution.valid:
            raise EvidenceUnavailable(
                f"{draft['diagramName']}: {resolution.findings[0].message}"
            )
        digests = resolution.digests()

    diagram, _engine = materialize(draft, evidence_digests=digests, layout_service=layout)
    return diagram


def _workspace_for(example_dir: Path, corpus_root: Optional[Path] = None) -> Optional[Path]:
    """The repository an example's citations point at, if it names one."""
    source = json.loads(_read(example_dir / "source.json") or "{}")
    repository = source.get("repository")
    if not repository:
        return None
    return (corpus_root or _default_corpus_root()) / str(repository)


def regen_eval(layout, types: List[str]) -> List[str]:
    """Rewrite `output.gp.json` from `draft.json` for every conceptual example.

    The answers are golden files: `test_answers_round_trip` asserts
    `materialize(draft) == output.gp.json`, so when a notation rule legitimately changes
    that test fails and this is how the new output is accepted. Doing it by hand across 39
    files is how a golden file quietly stops being golden.

    **Drafts are never written.** A draft is source — hand-authored to teach or reviewed
    once when it was derived — and regenerating one would be regenerating the answer from
    the answer.
    """
    changed: List[str] = []
    for diagram_type in types:
        for pool in ("answers", "training"):
            for example_dir in _example_dirs(diagram_type, pool):
                draft_text = _read(example_dir / "draft.json")
                if not draft_text.strip():
                    continue
                target = example_dir / "output.gp.json"
                rebuilt = materialize_example(
                    json.loads(draft_text), layout, _workspace_for(example_dir)
                )
                if _write_if_changed(target, rebuilt):
                    changed.append(f"{diagram_type}/{pool}/{example_dir.name}")
    return changed


def _write_if_changed(target: Path, diagram: dict) -> bool:
    """Write only a real change, in the format the product itself writes.

    Two details, both of which make the difference between a useful command and a noisy
    one. The serialization is `WorkspaceStorageService`'s, so a regenerated answer is
    byte-identical to what `diagram_create` would have saved rather than merely equivalent.
    And every clock reading is carried over from the file being replaced, because they are
    generated fresh on every materialization: without this, regenerating produces a diff
    every single time and "no diff" stops meaning anything. That now includes each entry
    in the request log, which is stamped when the ask arrives rather than when the example
    was last rebuilt.
    """
    previous_text = _read(target)
    if previous_text.strip():
        previous = json.loads(previous_text)
        previous_metadata = previous.get("metadata") or {}
        # A draft rather than a diagram: no `metadata`, and its one clock reading is
        # `basis.readAt`, stamped by `diagram_read` on every replay. Carried for the same
        # reason as the rest — otherwise `--regen edited` reports a diff every single run
        # and "no diff" stops meaning anything.
        if "metadata" not in diagram:
            if "basis" in diagram and "basis" in previous:
                diagram["basis"] = dict(previous["basis"])
        else:
            for stamp in ("createdAt", "updatedAt"):
                if stamp in previous_metadata:
                    diagram["metadata"][stamp] = previous_metadata[stamp]
            # Matched by position: the log is append-only, so entry *n* is the same ask it
            # was last time. A rebuilt example that gained one keeps today's stamp for it.
            for entry, before in zip(diagram["metadata"].get("requests") or (),
                                     previous_metadata.get("requests") or ()):
                entry["at"] = before["at"]

    serialized = json.dumps(diagram, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    if serialized == previous_text:
        return False
    target.write_text(serialized, encoding="utf-8")
    return True


def regen_edited() -> List[str]:
    """Replay every edit scenario and rewrite the pair it produces.

    Both diagrams are generated. Neither is ever stored by hand, so the pair on the page
    is evidence about the merge and the placement rules **as they are today** rather than
    a screenshot of the day somebody made it.

    It runs the real services in a temporary workspace, so a regression anywhere in
    create, read, merge, geometry or update shows up here as a changed picture.
    """
    changed: List[str] = []
    for diagram_type in SUPPORTED_DIAGRAM_TYPES:
        # Globbed on the authored file, not on `_example_dirs`, which looks for an
        # `output.gp.json` -- so a scenario that has never been replayed would be
        # invisible to the one command whose job is to replay it.
        base = _blueprints_dir() / diagram_type / "examples" / "edited"
        for path in sorted(base.glob("*/scenario.json")):
            example_dir = path.parent
            scenario = load_scenario(example_dir)
            if scenario is None:
                continue
            pair = replay(scenario)
            # Four documents, because an edit is a round trip and each step is a thing a
            # reviewer might need to check. The two drafts matter most: `read.draft.json`
            # is what the host was handed, `submitted.draft.json` is what it sent back, and
            # the diff between them is the edit as the product actually sees it — not as
            # the scenario's shorthand describes it.
            for target, document in (
                (example_dir / "before.gp.json", pair.before),
                (example_dir / "read.draft.json", pair.projected),
                (example_dir / "submitted.draft.json", pair.submitted),
                (example_dir / "output.gp.json", pair.after),
            ):
                if _write_if_changed(target, document):
                    changed.append(f"{diagram_type}/edited/{example_dir.name}/{target.name}")
    return changed


def regen_generated(layout, corpus_root: Path) -> Tuple[List[str], List[str]]:
    """Refresh the generated pool from whatever the hosts most recently wrote.

    A host is needed to reach a draft and never needed again, so the draft is what gets
    copied — the diagram the host produced is **regenerated** rather than copied, which is
    what proves it can be. A diagram that only survives because it was saved is not
    evidence that the pipeline still makes it.

    Anything in the pool the corpus no longer has is deleted, so the page always shows the
    newest run rather than an accumulation of several.
    """
    # Projected from the saved diagrams rather than read from a draft file beside them.
    # `diagram_create` no longer keeps a trace: that path is the edit working file now, and
    # a leftover trace there would be mistaken for one. Nothing is lost, because the
    # projection reproduces every class-1 field from the diagram and the ask itself is in
    # `metadata.requests` -- which is also a stronger claim than the trace made, since it
    # is derived from what was saved rather than from what was submitted.
    found: dict = {}
    for diagram_path in sorted(corpus_root.glob("*/.graphpilot/diagrams/*.gp.json")):
        diagram = json.loads(diagram_path.read_text(encoding="utf-8"))
        if diagram.get("diagramType") not in SUPPORTED_DIAGRAM_TYPES:
            # Crossed in the editor. No draft can describe it, so it cannot be regenerated.
            continue
        name = diagram_path.name[: -len(".gp.json")]
        found[name] = (project(diagram), diagram_path.parents[2].name)

    written, removed = [], []
    for diagram_type in SUPPORTED_DIAGRAM_TYPES:
        pool_root = _blueprints_dir() / diagram_type / "examples" / "generated"
        for existing in sorted(p for p in pool_root.glob("*/") if p.is_dir()):
            if existing.name not in found:
                shutil.rmtree(existing, ignore_errors=True)
                removed.append(f"{diagram_type}/{existing.name}")

    for name, (draft, repository) in sorted(found.items()):
        if "request" in draft:
            # A corpus run predating the reduced envelope. Migrating it here would mean
            # carrying the old shape indefinitely for a pool whose whole purpose is to
            # show what the current contract produces.
            raise CommandError(
                f"{name} was authored against the old draft envelope (`request`/`scope`). "
                "Re-run the corpus before syncing: the generated pool exists to show what "
                "the contract produces now."
            )
        diagram_type = draft["diagramType"]
        target = _blueprints_dir() / diagram_type / "examples" / "generated" / name
        target.mkdir(parents=True, exist_ok=True)
        (target / "draft.json").write_text(
            json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (target / "source.json").write_text(
            json.dumps({"repository": repository, "diagramType": diagram_type}, indent=2) + "\n",
            encoding="utf-8")
        try:
            _write_if_changed(
                target / "output.gp.json",
                materialize_example(draft, layout, corpus_root / repository),
            )
        except EvidenceUnavailable:
            # A draft whose citations do not resolve cannot be rebuilt — but it is exactly
            # what a reviewer needs to see, so the host's own diagram is copied in and the
            # gallery badges it `miscited`. Aborting the sync instead would let one bad
            # citation hide the eight diagrams that are fine.
            saved = corpus_root / repository / ".graphpilot" / "diagrams" / f"{name}.gp.json"
            if saved.is_file():
                shutil.copy2(saved, target / "output.gp.json")
        written.append(f"{diagram_type}/{name}")
    return written, removed


def _build_edited_card(diagram_type, example_dir, render, validation):
    """A pair, not a picture.

    Every other card answers *does this look right*. This one answers *did changing it
    cost anybody anything*, and that question needs both halves — a reviewer reads the
    two side by side and checks that the arrangement in the left is still the arrangement
    in the right.

    Both diagrams are read from disk here rather than replayed, because replaying on every
    page build would run three full edit round trips for a page that is often rebuilt just
    to re-read the HTML. `--regen edited` is what replays.
    """
    name = example_dir.name
    scenario = load_scenario(example_dir) or {}
    before = json.loads(_read(example_dir / "before.gp.json") or "null")
    after = json.loads(_read(example_dir / "output.gp.json") or "null")

    card = ExampleCard(
        diagram_type=diagram_type, pool="edited", name=name, svg="",
        goal=str(scenario.get("shows") or ""), tags=[], review_status="none",
        node_count=0, edge_count=0, valid=False, errors=[], struct_issues=[],
        render_ok=False, render_error="",
    )
    if before is None or after is None:
        card.render_error = "no before/after pair on disk — run `--regen edited`"
        card.provenance = PROVENANCE_STORED
        return card, None

    try:
        card.before_svg = _inline_svg(render.to_svg(before))
        card.svg = _inline_svg(render.to_svg(after))
        card.render_ok = True
    except Exception as exc:  # noqa: BLE001 - a render failure is a card, not a crash
        card.render_error = str(exc)
        return card, after

    result = validation.validate(after)
    card.valid = result.valid
    card.errors = [i.message for i in result.issues if i.severity == "error"][:6]
    card.node_count = len(after.get("nodes") or ())
    card.edge_count = len(after.get("edges") or ())
    card.source_path = str(example_dir / "output.gp.json")
    card.before_path = str(example_dir / "before.gp.json")
    card.diagram_json = json.dumps(after, indent=2, ensure_ascii=False)
    card.before_json = json.dumps(before, indent=2, ensure_ascii=False)
    card.read_draft_json = _read(example_dir / "read.draft.json")
    card.submitted_draft_json = _read(example_dir / "submitted.draft.json")
    card.scenario_json = json.dumps(scenario, indent=2, ensure_ascii=False)
    card.edit_request = str((scenario.get("edit") or {}).get("request") or "")

    # Recomputed from the two files rather than stored, so the numbers on the page cannot
    # disagree with the pictures beside them.
    was = {node["id"]: node["position"] for node in before["nodes"]}
    now = {node["id"]: node["position"] for node in after["nodes"]}
    survivors = sorted(set(was) & set(now))
    card.held = sum(1 for i in survivors if was[i] == now[i])
    card.moved = [i for i in survivors if was[i] != now[i]]
    card.added = sorted(set(now) - set(was))
    # `lostText` is the reason this pool is worth having. An audit deleted a node whose
    # description read "Reynolds 853. Confirmed with Priya" -- a decision record naming a
    # colleague -- and the host reported only the label, because a description is
    # deliberately invisible in the draft. A card that showed the same thing would repeat
    # the mistake it exists to expose.
    card.removed = [
        {
            "id": node["id"],
            "label": (node.get("data") or {}).get("label", ""),
            "lostText": [
                str((node.get("data") or {})[key])
                for key in ("description", "constraintExpression")
                if str((node.get("data") or {}).get(key) or "").strip()
            ],
            "drawnBy": (node.get("origin") or {}).get("assurance"),
        }
        for node in before["nodes"]
        if node["id"] not in now
    ]
    return card, after


def _build_card(diagram_type, pool, example_dir, render, validation, layout):
    """One card, whichever pool it came from.

    **The picture is produced by this run, not read from disk.** Where a draft exists the
    real pipeline runs over it — materialize, lay out, render — so the page shows what the
    code draws *today*. It used to re-run layout over the saved canonical document, which
    is a different and much weaker claim: layout never touches semantics, markers, edge
    dashing, route mode, ends or origin, so a notation change could not move the page and
    the page still said it was current.

    Nothing is written. `--regen` is what writes.
    """
    name = example_dir.name
    if pool == "edited":
        return _build_edited_card(diagram_type, example_dir, render, validation)
    draft_text = _read(example_dir / "draft.json")
    draft = json.loads(draft_text) if draft_text.strip() else None
    source = json.loads(_read(example_dir / "source.json") or "{}")

    # The most recent ask is what the diagram currently answers; `goal` was a host
    # paraphrase of the first one and is no longer carried.
    asks = (draft or {}).get("requests") or ()
    goal = str(asks[-1]) if asks else ""
    tags: List[Tuple[str, str]] = []
    if source.get("repository"):
        tags.append(("repository", str(source["repository"])))
    if draft:
        tags.append(("authority", str(draft.get("authority", "?"))))
        for key, label in (("evidence", "cites"), ("assumptions", "assumptions"),
                           ("requests", "asks")):
            tags.append((label, str(len(draft.get(key) or ()))))

    def failed(message: str) -> Tuple[ExampleCard, None]:
        return ExampleCard(
            diagram_type, pool, name, "", goal, tags, "invalid",
            0, 0, False, [message], [], False, "", provenance=PROVENANCE_FAILED,
        ), None

    errors: List[str] = []
    if draft is not None:
        try:
            diagram = materialize_example(draft, layout, _workspace_for(example_dir))
            provenance = PROVENANCE_MATERIALIZED
        except EvidenceUnavailable as exc:
            # Either the repository is not on this machine, or a citation does not resolve.
            # The second is a defect in the diagram and must not read as an absence, so it
            # gets its own state and the reason is shown on the card rather than hidden.
            try:
                diagram = json.loads((example_dir / "output.gp.json").read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return failed(f"cannot rebuild and no saved diagram: {exc}")
            reason = str(exc).split(": ", 1)[-1]
            if "does not appear in" in reason:
                provenance = PROVENANCE_MISCITED
                errors.append(reason)
            else:
                provenance = PROVENANCE_STORED
                tags.append(("not rebuilt", reason[:48]))
        except Exception as exc:
            return failed(f"materialization failed: {exc}")
    else:
        # No draft, so nothing can reproduce this: draw what is stored and say so. The
        # nine corpus diagrams are here because they predate stored drafts.
        try:
            diagram = json.loads((example_dir / "output.gp.json").read_text(encoding="utf-8"))
            provenance = PROVENANCE_STORED
        except (OSError, json.JSONDecodeError) as exc:
            return failed(f"could not load output.gp.json: {exc}")

    result = validation.validate(diagram)
    errors += [i.message for i in result.issues if i.severity == Severity.ERROR]
    struct = [v.message for v in check_structural_constraints(diagram, diagram_type)]

    # Every check above examines the diagram alone: is it legal, is it structurally sound,
    # is it readable. None asks whether it still says what the draft said, which is how a
    # dropped field passed every badge green for months. A loss here is our defect.
    losses = [str(loss) for loss in faithfulness_check(draft or {}, diagram)] if draft else []

    try:
        svg = _inline_svg(render.to_svg(diagram))
        render_ok, render_error = True, ""
    except DiagramRenderServiceError as exc:
        svg, render_ok, render_error = "", False, str(exc)

    return ExampleCard(
        diagram_type, pool, name, svg, goal, tags, pool,
        len(diagram.get("nodes") or []), len(diagram.get("edges") or []),
        bool(result.valid), errors, struct, render_ok, render_error,
        losses=losses,
        source_path=str(example_dir / "output.gp.json"),
        draft_json=draft_text,
        diagram_json=json.dumps(diagram, indent=2),
        provenance=provenance,
    ), diagram


def _coverage(diagram_type: str, diagrams: List[dict]) -> TypeCoverage:
    profile = get_type_profile(diagram_type)
    node_present, edge_present = set(), set()
    for d in diagrams:
        for n in d.get("nodes") or []:
            st = (n.get("data") or {}).get("semanticType")
            if st:
                node_present.add(st)
        for e in d.get("edges") or []:
            st = (e.get("data") or {}).get("semanticType")
            if st:
                edge_present.add(st)
    node_all = set(profile.allowed_node_semantic_types)
    edge_all = set(profile.allowed_edge_semantic_types)
    return TypeCoverage(
        diagram_type,
        len(node_all), sorted(node_all - node_present),
        len(edge_all), sorted(edge_all - edge_present),
    )


def _editor_link(path: str, label: str) -> str:
    """A link that opens one saved diagram in the editor, named so it says which."""
    if not path:
        return ""
    href = "http://127.0.0.1:5173/editor?diagramPath=" + quote(path, safe="")
    return (
        f'<a class="editor-link half" href="{href}" target="_blank" rel="noopener">'
        f"{_esc(label)}</a>"
    )


def _inline_svg(svg: str) -> str:
    """Strip the XML prolog so the SVG embeds cleanly inside HTML."""
    return _XML_PROLOG.sub("", svg).strip()


def _git_commit() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=str(settings.BASE_DIR),
        )
        return proc.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

_CSS = """
:root {
  --bg: #eef1f5; --panel: #ffffff; --ink: #1f2933; --muted: #6b7684;
  --line: #e2e7ee; --accent: #2f6feb;
  --ok-bg: #e6f4ea; --ok-fg: #1e7e34; --err-bg: #fdecea; --err-fg: #b3261e;
  --warn-bg: #fff4e0; --warn-fg: #8a5a00; --chip-bg: #eef2f7; --chip-fg: #46525f;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink);
  font: 14px/1.55 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
.wrap { max-width: 1400px; margin: 0 auto; padding: 0 20px; }
.topbar { position: sticky; top: 0; z-index: 5; background: var(--panel);
  border-bottom: 1px solid var(--line); box-shadow: 0 1px 4px rgba(20,30,50,.06); }
/* Two rows rather than one wrapping heap: what this page is, then how to narrow it.
   The filter row is the one a reviewer uses repeatedly across fifty-four cards, so it
   gets its own line and stays put while the page scrolls. */
.topbar .wrap { padding: 10px 20px 0; }
.topbar .title-row { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.topbar h1 { font-size: 17px; margin: 0; letter-spacing: .2px; }
.topbar .meta { color: var(--muted); font-size: 12px; }
.topbar .title-row .meta { margin-left: auto; }
.topbar .hint { color: var(--muted); font-size: 12px; padding: 0 0 9px; }
main.wrap { padding-top: 22px; padding-bottom: 60px; }
h2.section { font-size: 15px; text-transform: uppercase; letter-spacing: .06em;
  color: var(--muted); margin: 30px 0 12px; border-bottom: 1px solid var(--line); padding-bottom: 6px; }
.count { color: var(--muted); font-weight: 500; }
.pool { font-size: 13px; color: var(--muted); margin: 10px 0 8px; font-weight: 600; }
.pool.sub { margin-top: 20px; color: var(--ink); font-size: 12.5px; text-transform: uppercase;
  letter-spacing: .05em; }
h2.section { scroll-margin-top: 96px; }
.jump { display: flex; gap: 8px; flex-wrap: wrap; margin: 2px 0 0; }
.jump a { display: inline-flex; align-items: center; gap: 6px; text-decoration: none;
  font-size: 12.5px; font-weight: 700; color: var(--accent); border: 1px solid var(--line);
  border-radius: 999px; padding: 3px 11px; }
.jump a:hover { border-color: var(--accent); background: #f2f6fd; }
.jump .n { font-weight: 600; color: var(--muted); }

/* coverage */
.cov-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
.cov-card { background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--ok-fg);
  border-radius: 10px; padding: 12px 14px; }
.cov-card.gap { border-left-color: var(--err-fg); }
.cov-card .t { font-weight: 700; margin-bottom: 4px; }
.cov-card .nums { color: var(--muted); font-size: 12.5px; }
.cov-card .miss { margin-top: 8px; }
.cov-card .miss .lbl { color: var(--err-fg); font-weight: 600; font-size: 12px; }
.allgood { color: var(--ok-fg); font-weight: 600; font-size: 12.5px; margin-top: 6px; }

/* cards */
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 18px; }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
  box-shadow: 0 1px 3px rgba(20,30,50,.06); overflow: hidden; display: flex; flex-direction: column; }
.card-head { display: flex; justify-content: space-between; align-items: flex-start;
  gap: 10px; padding: 12px 14px; border-bottom: 1px solid var(--line); }
.card-title { font-weight: 700; font-size: 13.5px; word-break: break-word; }
.card-title .pool-tag { color: var(--muted); font-weight: 500; }
.badges { display: flex; flex-wrap: wrap; gap: 5px; justify-content: flex-end; }
.badge { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 999px;
  background: var(--chip-bg); color: var(--chip-fg); white-space: nowrap; }
.badge.ok { background: var(--ok-bg); color: var(--ok-fg); }
.badge.err { background: var(--err-bg); color: var(--err-fg); }
.badge.warn { background: var(--warn-bg); color: var(--warn-fg); }
.badge.repo { background: #e8eefc; color: #2f4f8f; }
/* The card is a thumbnail. A composition diamond is 16px, and scaled into a 340px card a
   wide diagram puts it on screen at under 2px — so the card exists to find the diagram,
   and the overlay exists to look at it. */
.diagram { display: block; width: 100%; background: #fbfcfe; border: 0;
  border-bottom: 1px solid var(--line); padding: 12px; text-align: center;
  max-height: 320px; overflow: hidden; cursor: zoom-in; }
.diagram svg { max-width: 100%; height: auto; pointer-events: none; }
.diagram:hover { background: #f2f6fd; }
.diagram:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }
.scale-note { font-size: 11px; color: var(--muted); padding: 5px 14px 0; font-style: italic; }
.actions { margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; }
.editor-link { font-size: 12px; font-weight: 600; text-decoration: none; color: var(--accent);
  border: 1px solid var(--accent); border-radius: 6px; padding: 4px 10px; }
.editor-link:hover { background: var(--accent); color: #fff; }
.src-link { font: inherit; font-size: 12px; font-weight: 600; cursor: pointer;
  color: var(--muted); background: #fff; border: 1px solid var(--line);
  border-radius: 6px; padding: 4px 10px; }
.src-link:hover { color: var(--accent); border-color: var(--accent); }

/* Source viewer: the draft and the canonical diagram behind a card. */
.src-stage { flex: 1; overflow: auto; background: #fbfcfe; padding: 18px 22px; }
.json { font: 12.5px/1.55 ui-monospace, "Cascadia Code", Consolas, monospace;
  white-space: pre; color: #1d2430; }
.j-row { padding: 0 4px; border-radius: 3px; }
.j-head { cursor: pointer; }
.j-head:hover { background: #eef3fa; }
.j-toggle { display: inline-block; width: 12px; color: var(--muted); }
.j-key { color: #7048a8; }
.j-str { color: #1d6b3f; }
.j-num { color: #0b6ba8; }
.j-bool, .j-null { color: #a8500b; }
.j-count { color: var(--muted); font-style: italic; margin-left: 8px; font-size: 11.5px; }
.j-children { }
.j-raw { font: 12.5px/1.5 ui-monospace, Consolas, monospace; white-space: pre-wrap; }
.md { max-width: 780px; font-size: 14.5px; line-height: 1.6; }
.md h3, .md h4, .md h5 { margin: 18px 0 6px; }
.md p { margin: 8px 0; }
.md ul { margin: 6px 0 6px 20px; }
.md li { margin: 2px 0; }
.md code { background: #eef2f7; padding: 1px 5px; border-radius: 4px; font-size: 12.5px; }

/* Full-size viewer. Pans by dragging, zooms with the wheel, closes with Escape. */
.viewer { position: fixed; inset: 0; z-index: 50; background: rgba(15, 22, 34, .82);
  display: none; flex-direction: column; }
.viewer.on { display: flex; }
.viewer-bar { display: flex; align-items: center; gap: 12px; padding: 10px 16px;
  background: #fff; border-bottom: 1px solid var(--line); }
.viewer-name { font-weight: 700; }
.viewer-hint { color: var(--muted); font-size: 12px; }
.viewer-bar .spacer { flex: 1; }
.viewer-bar button { font: inherit; font-size: 12.5px; border: 1px solid var(--line);
  background: #fff; border-radius: 6px; padding: 4px 10px; cursor: pointer; }
.viewer-bar button:hover { background: #eef2f8; }
.viewer-stage { flex: 1; overflow: hidden; cursor: grab; background: #fff; }
.viewer-stage.dragging { cursor: grabbing; }
.viewer-stage > div { transform-origin: 0 0; }
.viewer-stage svg { display: block; max-width: none; }
.diagram .render-err { color: var(--err-fg); font-size: 12.5px; padding: 24px; }
.body { padding: 12px 14px; }
.body h4 { margin: 0 0 4px; font-size: 11px; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); }
.goal { background: #f7f9fc; border-left: 3px solid var(--accent); border-radius: 0 6px 6px 0;
  padding: 8px 10px; color: #37424f; font-size: 13px; margin-bottom: 10px; white-space: pre-wrap; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { font-size: 11.5px; background: var(--chip-bg); color: var(--chip-fg);
  padding: 2px 8px; border-radius: 6px; }
.chip b { color: var(--ink); font-weight: 600; }
.untagged { color: var(--muted); font-size: 12px; font-style: italic; }
.errs { margin: 10px 0 0; padding-left: 18px; color: var(--err-fg); font-size: 12px; }
.status-approved { background: var(--ok-bg); color: var(--ok-fg); }
.status-draft { background: var(--warn-bg); color: var(--warn-fg); }
.status-none { background: var(--chip-bg); color: var(--chip-fg); }

/* The `edited` pool's card carries two diagrams rather than one. A card is about 340px
   across, so each half is drawn at roughly half that -- unreadable as a picture and
   perfectly readable as a *shape*, which is what a before/after comparison actually
   needs. Either half opens full size. */
/* The filter bar. Pools and types are independent: choosing none of a group means
   "all of it", so a reviewer who wants every training diagram clicks one thing. */
/* Capped and scrollable, because this row grows with the vocabulary.
   Three diagram types wrap to one line; a dozen would wrap to four, and the header is
   sticky — so it would eat the viewport and push the first pool of cards under the fold.
   That is exactly how a pool went unnoticed once already, and it should not come back the
   day someone adds diagram types. */
.filters {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 9px 0 10px; border-top: 1px solid var(--line); margin-top: 9px;
}
/* The chips scroll; the controls beside them never do. Three diagram types wrap to one
   line, a dozen to two, and thirty would push the first pool of cards under a sticky
   header — which is exactly how a pool went unnoticed once. Capping the strip keeps the
   header a fixed share of the viewport, and keeping the search and the reset outside it
   means the way out of a filter is always reachable. */
.filters .chips {
  display: flex; flex-wrap: wrap; align-items: center; gap: 5px;
  flex: 1; min-width: 0; max-height: 22vh; overflow-y: auto;
}
.filters .controls {
  display: flex; align-items: center; gap: 6px; flex-shrink: 0; padding-top: 1px;
}
.flabel {
  font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em;
  color: #9aa4b2; margin-right: 3px;
}
/* A rule between groups, so `pool` and `type` read as two questions and not one list. */
.flabel:not(:first-child) {
  margin-left: 12px; padding-left: 15px; border-left: 1px solid var(--line);
}
.chipf {
  font: inherit; font-size: 12px; font-weight: 500; cursor: pointer;
  padding: 4px 11px; border-radius: 999px; line-height: 1.35;
  border: 1px solid var(--line); background: #fff; color: #46505e;
  transition: background .12s, border-color .12s, color .12s;
}
.chipf:hover { border-color: var(--accent); color: var(--accent); }
.chipf[aria-pressed="true"] {
  background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600;
}
.chipf[aria-pressed="true"] .n { color: #fff; opacity: .75; }
.chipf .n {
  margin-left: 6px; font-variant-numeric: tabular-nums; font-size: 11px; color: #97a1ae;
}
.chipf.reset { border-style: dashed; margin-left: 4px; }
.search {
  font: inherit; font-size: 12px; padding: 4px 11px 4px 15px; border-radius: 999px;
  min-width: 150px; border: 1px solid var(--line); background: #fff; color: #46505e;
}
.search:focus { outline: none; border-color: var(--accent); }
.shown { font-size: 11.5px; color: var(--muted); font-variant-numeric: tabular-nums; }
.pool-section[hidden], .type-block[hidden], .card[hidden] { display: none; }
.no-match { color: var(--muted); font-style: italic; padding: 24px 0; }

/* Reference, not the main event: shut by default so the cards start at the top. */
.panels { margin: 14px 0 4px; }
.panels > summary {
  cursor: pointer; font-size: 13px; font-weight: 600; color: var(--fg);
  padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px;
  background: var(--card); list-style-position: inside;
}
.panels > summary:hover { border-color: var(--accent); }
.panels > summary .count { font-weight: 400; color: var(--muted); }

.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
/* Two diagrams in a one-column card would each be drawn at about 165px, which is too
   small to tell whether anything moved -- the one question this pool exists to answer.
   The card takes two columns so each half gets the width a single-diagram card gets. */
.card:has(.pair) { grid-column: span 2; }
@media (max-width: 800px) { .card:has(.pair) { grid-column: span 1; } }
/* A column so the edit link sits at the bottom of both halves rather than following
   whichever diagram happens to be shorter. */
.pair figure { margin: 0; min-width: 0; display: flex; flex-direction: column; }
.pair figure .diagram { flex: 1; }
.pair figcaption {
  font-size: 11px; color: var(--muted); margin-bottom: 4px; text-align: center;
}
/* A pair is scaled to fit, never cropped.
   `.diagram` clips at 320px, which is right for a single thumbnail you click into — but
   fatal here. The change an edit makes is almost never at the top of the drawing, so both
   halves showed the same unchanged header and the pair looked identical. Six cards
   claiming to show a difference, none of them showing it. */
.pair .diagram {
  min-height: 120px; max-height: 340px; overflow: visible;
  display: flex; align-items: center; justify-content: center;
}
.pair .diagram svg { max-height: 316px; max-width: 100%; width: auto; height: auto; }
.editor-link.half { display: block; margin: 6px auto 0; width: fit-content;
  font-size: 11px; padding: 2px 8px; }
.ask { margin: 0 0 10px; padding: 8px 11px; border-radius: 6px;
       background: #f2f6ff; border: 1px solid #d6e2fb; }
.ask .lbl { display: block; font-size: 10.5px; text-transform: uppercase;
            letter-spacing: .05em; color: var(--muted); margin-bottom: 2px; }
.ask .q { font-size: 13px; color: #1d2430; }
.good { color: var(--ok-fg); }
.bad { color: var(--err-fg); }
"""


#: A card is about 340px across. Scaled to that, anything wider than roughly twice it
#: puts a 16px marker under 8px, which is where a diamond stops reading as a diamond.
_LEGIBLE_CARD_WIDTH = 700.0
_SVG_WIDTH = re.compile(r'<svg[^>]*\bwidth="([\d.]+)')


def _svg_width(svg: str) -> Optional[float]:
    match = _SVG_WIDTH.search(svg)
    return float(match.group(1)) if match else None


# ---------------------------------------------------------------------------
# Legibility — measured from the drawn SVG, not from a model of it
# ---------------------------------------------------------------------------
# These numbers drove the H2 round and were computed by throwaway scripts, which meant
# nobody but their author could reproduce them. They live here now: the page that shows
# the diagrams also states how legible they are.



def _fresh_run_dir(out_root: Path, keep: bool) -> Path:
    """A directory for this run, having removed the ones it supersedes.

    A gallery costs seconds to regenerate and nothing to store, which is exactly why it
    accumulates: eleven runs had piled up before anyone noticed. Two copies of the same
    page is worse than one, because the stale one is the one you end up reviewing.
    """
    out_root.mkdir(parents=True, exist_ok=True)
    if not keep:
        for previous in out_root.iterdir():
            if previous.is_dir():
                shutil.rmtree(previous, ignore_errors=True)
            else:
                previous.unlink(missing_ok=True)
    run_dir = out_root / (datetime.now().strftime("%Y-%m-%dT%H-%M-%S"))
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _esc(text: str) -> str:
    return html.escape(text or "")


def _render_html(cards: List[ExampleCard], coverage: List[TypeCoverage], meta: dict) -> str:
    parts: List[str] = [
        "<!doctype html>",
        '<html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<link rel="icon" href="data:,">',
        "<title>GraphPilot — review gallery</title>",
        f"<style>{_CSS}</style></head><body>",
        '<header class="topbar"><div class="wrap">',
        '<div class="title-row">',
        "<h1>GraphPilot · review gallery</h1>",
        f'<div class="meta">{meta["count"]} examples · '
        f'generated {_esc(meta["generatedAt"])} · commit {_esc(meta["gitCommit"])} · '
        f'layout {_esc(meta["layoutEngine"])}</div>',
        "</div>",
        # Filters, not jump links. An anchor still leaves thirty-six answers between a
        # reviewer and the pool they came for, and scrolling past them is exactly how the
        # newest pool became invisible to the person who asked for it.
        '<nav class="filters" id="filters"><div class="chips">'
        '<span class="flabel">pool</span>' + "".join(
            f'<button class="chipf" data-filter="pool" data-value="{_esc(pool)}" '
            f'aria-pressed="false">{_esc(pool)}'
            f'<span class="n">{sum(1 for c in cards if c.pool == pool)}</span></button>'
            for pool in _REVIEW_ORDER
            if any(c.pool == pool for c in cards)
        )
        # One chip per diagram type that has cards, straight from the registered types —
        # add a diagram type and it appears here, in its section, and in the search index,
        # with no edit to this file.
        + '<span class="flabel">type</span>' + "".join(
            f'<button class="chipf" data-filter="type" data-value="{_esc(kind)}" '
            f'aria-pressed="false">{_esc(kind.replace("_diagram", ""))}'
            f'<span class="n">{sum(1 for c in cards if c.diagram_type == kind)}</span></button>'
            for kind in meta["types"]
            if any(c.diagram_type == kind for c in cards)
        )
        + "</div>"
        # Outside the scrolling strip above, so the way out of a filter is always reachable
        # however many types there are.
        + '<div class="controls">'
          '<input class="search" id="search" type="search" placeholder="name…" '
          'aria-label="Filter cards by name">'
          '<button class="chipf reset" id="reset" hidden>show all</button>'
          '<span class="shown" id="shown"></span>'
          "</div></nav>",
        '<div class="hint">click a diagram to open it full size · '
        '<b>Edit in GraphPilot</b> needs the editor running on :5173 '
        '(<code>cd frontend; npm run dev</code>)</div>',
        "</div></header>",
        '<main class="wrap">',
    ]

    legible = meta.get("legibility")
    if legible:
        # A Counter omits keys that never incremented, and a clean run is exactly the case
        # where they do not — so read defensively or the best result crashes the page.
        clipped = legible.get("clipped", 0)
        buried = legible.get("buried", 0)
        collided = legible.get("collided", 0)
        bad = clipped + buried + collided
        total = max(legible.get("texts", 0), 1)
        cls = "cov-card gap" if bad else "cov-card"
        summary = (
            f'<div class="miss"><span class="lbl">of which:</span> '
            f'<span class="chip">{clipped} clipped by its own node</span>'
            f'<span class="chip">{buried} buried under another</span>'
            f'<span class="chip">{collided} overlapping other text</span></div>'
            if bad else '<div class="allgood">every drawn string is legible and in place</div>'
        )
        # Folded shut. These two panels are reference a reviewer consults, not the thing
        # they came for — and open by default they pushed the first pool of cards below
        # the fold, which is how the newest pool went unnoticed by the person who asked
        # for it. The headline number stays visible on the summary line.
        parts.append(
            '<details class="panels"><summary>Legibility and vocabulary coverage '
            f'<span class="count">· {bad} of {total} strings unreadable or misplaced '
            f'({bad / total:.1%})</span></summary>'
            '<h2 class="section">Legibility</h2><div class="cov-grid">'
            f'<div class="{cls}"><div class="t">drawn text</div>'
            f'<div class="nums">{bad} of {total} unreadable or misplaced '
            f'({bad / total:.1%})</div>{summary}</div></div>'
        )
    else:
        parts.append('<details class="panels"><summary>Vocabulary coverage</summary>')

    # Coverage panel
    parts.append('<h2 class="section">Vocabulary coverage</h2><div class="cov-grid">')
    for cov in coverage:
        cls = "cov-card gap" if cov.has_gap else "cov-card"
        node_cov = cov.node_total - len(cov.node_missing)
        edge_cov = cov.edge_total - len(cov.edge_missing)
        block = [
            f'<div class="{cls}"><div class="t">{_esc(cov.diagram_type)}</div>',
            f'<div class="nums">nodes {node_cov}/{cov.node_total} · edges {edge_cov}/{cov.edge_total}</div>',
        ]
        if cov.has_gap:
            chips = "".join(f'<span class="chip">{_esc(m)}</span>' for m in cov.node_missing + cov.edge_missing)
            block.append(f'<div class="miss"><span class="lbl">missing:</span> {chips}</div>')
        else:
            block.append('<div class="allgood">all semanticTypes present</div>')
        block.append("</div>")
        parts.append("".join(block))
    parts.append("</div></details>")

    # Grouped by *why an example exists*, then by diagram type. Grouping by type first
    # buries the two pools anyone actually comes here to review: the nine generated
    # diagrams split three ways behind twelve answers each, and the three worked examples
    # one at a time. A reviewer arrives with one question, and the question maps to a pool.
    for pool in _REVIEW_ORDER:
        pool_cards = [c for c in cards if c.pool == pool]
        if not pool_cards:
            continue
        # `data-pool` and `data-type` are what the filter bar acts on. Hiding a card
        # without hiding the heading above it leaves a reviewer reading "answers · 36"
        # over an empty strip, which reads as a bug rather than as a filter.
        parts.append(
            f'<section class="pool-section" data-pool="{_esc(pool)}" id="pool-{_esc(pool)}">'
            f'<h2 class="section">{_esc(pool)} '
            f'<span class="count">· {len(pool_cards)}</span></h2>'
            f'<div class="pool">{_POOL_PURPOSE.get(pool, "")}</div>'
        )
        for diagram_type in meta["types"]:
            type_cards = [c for c in pool_cards if c.diagram_type == diagram_type]
            if not type_cards:
                continue
            parts.append(
                f'<div class="type-block" data-type="{_esc(diagram_type)}">'
                f'<div class="pool sub">{_esc(diagram_type)} ({len(type_cards)})</div>'
                '<div class="cards">'
            )
            parts.extend(_render_card(c) for c in type_cards)
            parts.append("</div></div>")
        parts.append("</section>")

    # Shown when a filter combination matches nothing, so the page says so rather than
    # going blank and looking broken.
    parts.append('<div class="no-match" id="nomatch" hidden>'
                 'Nothing matches those filters. <b>show all</b> clears them.</div>')
    parts.append("</main>")
    parts.append(_VIEWER_MARKUP)
    parts.append(f"<script>{_VIEWER_SCRIPT}</script>")
    parts.append(f"<script>{_FILTER_SCRIPT}</script>")
    parts.append("</body></html>")
    return "\n".join(parts)


#: Filtering, in about forty lines and no dependency.
#:
#: Selecting nothing in a group means "all of it", so the common case — *show me only the
#: edited pool* — is one click rather than three deselections. Empty headings are hidden
#: with their cards, because "answers · 36" over an empty strip reads as a broken page.
_FILTER_SCRIPT = """
(function () {
  var bar = document.getElementById('filters');
  if (!bar) return;
  var search = document.getElementById('search');
  var reset = document.getElementById('reset');
  var shown = document.getElementById('shown');
  var sections = [].slice.call(document.querySelectorAll('.pool-section'));
  var picked = { pool: new Set(), type: new Set() };

  function keeps(group, value) {
    return picked[group].size === 0 || picked[group].has(value);
  }

  function apply() {
    var term = (search.value || '').trim().toLowerCase();
    var visible = 0;
    sections.forEach(function (section) {
      var poolOk = keeps('pool', section.dataset.pool);
      var anyInSection = 0;
      [].forEach.call(section.querySelectorAll('.type-block'), function (block) {
        var typeOk = poolOk && keeps('type', block.dataset.type);
        var anyInBlock = 0;
        [].forEach.call(block.querySelectorAll('.card'), function (card) {
          var hit = typeOk && (!term || card.dataset.search.indexOf(term) !== -1);
          card.hidden = !hit;
          if (hit) { anyInBlock++; }
        });
        block.hidden = anyInBlock === 0;
        anyInSection += anyInBlock;
      });
      section.hidden = anyInSection === 0;
      visible += anyInSection;
    });
    var total = document.querySelectorAll('.card').length;
    var filtering = picked.pool.size || picked.type.size || term;
    shown.textContent = filtering ? ('showing ' + visible + ' of ' + total) : '';
    reset.hidden = !filtering;
    var empty = document.getElementById('nomatch');
    if (empty) { empty.hidden = visible !== 0; }
  }

  bar.addEventListener('click', function (event) {
    var chip = event.target.closest('.chipf');
    if (!chip) return;
    if (chip.id === 'reset') {
      picked.pool.clear(); picked.type.clear(); search.value = '';
      [].forEach.call(bar.querySelectorAll('.chipf[data-filter]'), function (other) {
        other.setAttribute('aria-pressed', 'false');
      });
      apply();
      return;
    }
    var group = chip.dataset.filter;
    var value = chip.dataset.value;
    if (picked[group].has(value)) { picked[group].delete(value); }
    else { picked[group].add(value); }
    chip.setAttribute('aria-pressed', picked[group].has(value) ? 'true' : 'false');
    apply();
  });

  search.addEventListener('input', apply);
  apply();
})();
"""


_VIEWER_MARKUP = """
<div class="viewer" id="viewer" role="dialog" aria-modal="true" aria-label="Diagram viewer">
  <div class="viewer-bar">
    <span class="viewer-name" id="viewer-name"></span>
    <span class="viewer-hint">drag to pan · scroll to zoom</span>
    <span class="spacer"></span>
    <button type="button" data-zoom="out">&minus;</button>
    <button type="button" id="viewer-scale">100%</button>
    <button type="button" data-zoom="in">+</button>
    <button type="button" data-zoom="fit">Fit</button>
    <button type="button" id="viewer-close">Close (Esc)</button>
  </div>
  <div class="viewer-stage" id="viewer-stage"><div id="viewer-inner"></div></div>
</div>
<div class="viewer src-viewer" id="src-viewer" role="dialog" aria-modal="true" aria-label="Source viewer">
  <div class="viewer-bar">
    <span class="viewer-name" id="src-name"></span>
    <span class="viewer-hint" id="src-hint"></span>
    <span class="spacer"></span>
    <button type="button" id="src-collapse">Collapse all</button>
    <button type="button" id="src-copy">Copy</button>
    <button type="button" id="src-close">Close (Esc)</button>
  </div>
  <div class="src-stage"><div id="src-body"></div></div>
</div>
"""

# Deliberately dependency-free: the page has to open from the filesystem with no server.
_VIEWER_SCRIPT = """
(function () {
  var viewer = document.getElementById('viewer');
  var stage = document.getElementById('viewer-stage');
  var inner = document.getElementById('viewer-inner');
  var nameEl = document.getElementById('viewer-name');
  var scaleEl = document.getElementById('viewer-scale');
  var scale = 1, tx = 0, ty = 0, natural = { w: 0, h: 0 };

  function apply() {
    inner.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')';
    scaleEl.textContent = Math.round(scale * 100) + '%';
  }
  function fit() {
    if (!natural.w || !natural.h) return;
    var pad = 32;
    scale = Math.min(1, (stage.clientWidth - pad) / natural.w, (stage.clientHeight - pad) / natural.h);
    tx = Math.max(0, (stage.clientWidth - natural.w * scale) / 2);
    ty = Math.max(0, (stage.clientHeight - natural.h * scale) / 2);
    apply();
  }
  // Opening shows the diagram at a size its labels can be read at, not the size that
  // makes all of it fit: fitting a 2,900px-tall activity diagram into a window lands at
  // 29%, which is the problem the overlay exists to solve. Fit-all is a button instead.
  function fitWidth() {
    if (!natural.w) return;
    var pad = 32;
    scale = Math.min(1, (stage.clientWidth - pad) / natural.w);
    tx = Math.max(0, (stage.clientWidth - natural.w * scale) / 2);
    ty = 16;
    apply();
  }
  // Takes the button that was clicked, not the card it sits in.
  //
  // It used to take the card and ask it for `.diagram svg`, which returns the *first* one.
  // With a single diagram per card that is the right answer by accident; with a pair it
  // means clicking `after` opens `before`, silently, and a reviewer comparing the two
  // full size is looking at the same picture twice and concluding nothing changed.
  function open(trigger) {
    var svg = trigger.querySelector('svg');
    if (!svg) return;
    var card = trigger.closest('.card');
    nameEl.textContent = (card && card.getAttribute('data-name') || '')
      + (trigger.getAttribute('data-half') ? ' · ' + trigger.getAttribute('data-half') : '');
    inner.innerHTML = '';
    var copy = svg.cloneNode(true);
    copy.style.pointerEvents = 'none';
    natural = { w: parseFloat(copy.getAttribute('width')) || 800,
                h: parseFloat(copy.getAttribute('height')) || 600 };
    copy.setAttribute('width', natural.w);
    copy.setAttribute('height', natural.h);
    copy.style.maxWidth = 'none';
    inner.appendChild(copy);
    viewer.classList.add('on');
    document.body.style.overflow = 'hidden';
    fitWidth();
  }
  function close() {
    viewer.classList.remove('on');
    document.body.style.overflow = '';
    inner.innerHTML = '';
  }

  document.addEventListener('click', function (event) {
    var trigger = event.target.closest('.diagram[data-open]');
    if (trigger) { open(trigger); return; }
    if (event.target.id === 'viewer-close') close();
    var zoom = event.target.closest('[data-zoom]');
    if (!zoom) return;
    var how = zoom.getAttribute('data-zoom');
    if (how === 'fit') { fit(); return; }
    var next = how === 'in' ? scale * 1.25 : scale / 1.25;
    scale = Math.min(8, Math.max(0.05, next));
    apply();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && viewer.classList.contains('on')) close();
  });

  stage.addEventListener('wheel', function (event) {
    if (!viewer.classList.contains('on')) return;
    event.preventDefault();
    var rect = stage.getBoundingClientRect();
    var px = event.clientX - rect.left, py = event.clientY - rect.top;
    var factor = event.deltaY < 0 ? 1.12 : 1 / 1.12;
    var next = Math.min(8, Math.max(0.05, scale * factor));
    // Keep the point under the cursor fixed while zooming.
    tx = px - (px - tx) * (next / scale);
    ty = py - (py - ty) * (next / scale);
    scale = next;
    apply();
  }, { passive: false });

  var dragging = false, lastX = 0, lastY = 0;
  stage.addEventListener('pointerdown', function (event) {
    dragging = true; lastX = event.clientX; lastY = event.clientY;
    stage.classList.add('dragging');
    stage.setPointerCapture(event.pointerId);
  });
  stage.addEventListener('pointermove', function (event) {
    if (!dragging) return;
    tx += event.clientX - lastX; ty += event.clientY - lastY;
    lastX = event.clientX; lastY = event.clientY;
    apply();
  });
  ['pointerup', 'pointercancel'].forEach(function (type) {
    stage.addEventListener(type, function () { dragging = false; stage.classList.remove('dragging'); });
  });
})();

// ---- source viewer: the draft and the canonical diagram -----------------------------
// Hand-rolled rather than pulled from a CDN, because the page has to open from a file://
// URL on a machine with no network. It is a few hundred lines of nothing clever.
(function () {
  var panel = document.getElementById('src-viewer');
  var body = document.getElementById('src-body');
  var nameEl = document.getElementById('src-name');
  var hintEl = document.getElementById('src-hint');
  var collapseBtn = document.getElementById('src-collapse');
  var copyBtn = document.getElementById('src-copy');
  if (!panel) return;

  var raw = '';

  function esc(text) {
    return String(text).replace(/[&<>]/g, function (ch) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[ch];
    });
  }

  // A row per line, so an object can be folded by hiding the rows between its braces.
  function renderJson(value, out, indent, key, last) {
    var pad = '  '.repeat(indent);
    var prefix = key === null ? '' : '<span class="j-key">"' + esc(key) + '"</span>: ';
    var tail = last ? '' : ',';

    if (value !== null && typeof value === 'object') {
      var isArray = Array.isArray(value);
      var keys = isArray ? value.map(function (_, i) { return i; }) : Object.keys(value);
      var open = isArray ? '[' : '{';
      var close = isArray ? ']' : '}';
      if (!keys.length) {
        out.push('<div class="j-row">' + pad + prefix + open + close + tail + '</div>');
        return;
      }
      var id = 'f' + (out.length) + '-' + indent;
      out.push(
        '<div class="j-row j-head" data-fold="' + id + '">' + pad +
        '<span class="j-toggle">\\u25be</span>' + prefix + open +
        '<span class="j-count">' + keys.length + (isArray ? ' items' : ' keys') + '</span>' +
        '</div>'
      );
      out.push('<div class="j-children" data-body="' + id + '">');
      keys.forEach(function (k, i) {
        renderJson(isArray ? value[k] : value[k], out, indent + 1,
                   isArray ? null : String(k), i === keys.length - 1);
      });
      out.push('</div>');
      out.push('<div class="j-row">' + pad + close + tail + '</div>');
      return;
    }

    var cls = value === null ? 'j-null'
      : typeof value === 'number' ? 'j-num'
      : typeof value === 'boolean' ? 'j-bool' : 'j-str';
    var text = typeof value === 'string' ? '"' + esc(value) + '"' : esc(String(value));
    out.push('<div class="j-row">' + pad + prefix + '<span class="' + cls + '">' + text + '</span>' + tail + '</div>');
  }

  function open(sourceId, title) {
    var node = document.getElementById(sourceId);
    if (!node) return;
    raw = node.textContent;
    nameEl.textContent = title;
    var parsed;
    try { parsed = JSON.parse(raw); } catch (err) {
      body.innerHTML = '<pre class="j-raw">' + esc(raw) + '</pre>';
      hintEl.textContent = 'could not parse as JSON';
      panel.classList.add('on');
      return;
    }
    var out = [];
    renderJson(parsed, out, 0, null, true);
    body.innerHTML = '<div class="json">' + out.join('') + '</div>';
    hintEl.textContent = (raw.length / 1024).toFixed(1) + ' KB \u00b7 click a line to fold it';
    panel.classList.add('on');
  }

  function close() { panel.classList.remove('on'); body.innerHTML = ''; }

  document.addEventListener('click', function (event) {
    var link = event.target.closest('.src-link');
    if (link) {
      event.preventDefault();
      open(link.getAttribute('data-src'), link.getAttribute('data-title'));
      return;
    }
    var head = event.target.closest('.j-head');
    if (head && panel.contains(head)) {
      var id = head.getAttribute('data-fold');
      var children = body.querySelector('[data-body="' + id + '"]');
      if (children) {
        var folded = children.style.display === 'none';
        children.style.display = folded ? '' : 'none';
        head.querySelector('.j-toggle').textContent = folded ? '\\u25be' : '\\u25b8';
      }
    }
  });

  document.getElementById('src-close').addEventListener('click', close);
  panel.addEventListener('click', function (event) { if (event.target === panel) close(); });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && panel.classList.contains('on')) close();
  });

  collapseBtn.addEventListener('click', function () {
    var collapsing = collapseBtn.textContent === 'Collapse all';
    body.querySelectorAll('.j-children').forEach(function (node) {
      // The outermost object stays open; collapsing it shows a reviewer nothing.
      if (node.parentElement !== body.firstElementChild) return;
      node.style.display = collapsing ? 'none' : '';
    });
    body.querySelectorAll('.j-head').forEach(function (node) {
      var children = body.querySelector('[data-body="' + node.getAttribute('data-fold') + '"]');
      if (children && children.parentElement === body.firstElementChild) {
        node.querySelector('.j-toggle').textContent = collapsing ? '\\u25b8' : '\\u25be';
      }
    });
    collapseBtn.textContent = collapsing ? 'Expand all' : 'Collapse all';
  });

  copyBtn.addEventListener('click', function () {
    navigator.clipboard.writeText(raw).then(function () {
      copyBtn.textContent = 'Copied';
      setTimeout(function () { copyBtn.textContent = 'Copy'; }, 1200);
    }, function () { copyBtn.textContent = 'Copy failed'; });
  });
})();
"""


def _render_card(c: ExampleCard) -> str:
    valid_badge = '<span class="badge ok">valid</span>' if c.valid else '<span class="badge err">invalid</span>'
    if c.struct_issues:
        struct_badge = f'<span class="badge warn">{len(c.struct_issues)} structural</span>'
    else:
        struct_badge = '<span class="badge ok">structural ok</span>'
    # A diagram can be valid, legible and correctly cited while missing something the
    # host authored. Nothing on this page could say so until now.
    faithful_badge = (
        f'<span class="badge err" title="{_esc("; ".join(c.losses)[:400])}">'
        f'{len(c.losses)} lost</span>'
        if c.losses
        else ''
    )
    counts_badge = f'<span class="badge">{c.node_count}n · {c.edge_count}e</span>'
    # A reviewer's question is "which one do I open", and a page total cannot answer it.
    legibility_badge = (
        f'<span class="badge err" title="strings clipped, buried or overlapping in this '
        f'diagram, out of {c.text_count} drawn">{c.illegible} unreadable</span>'
        if c.illegible
        else '<span class="badge ok">legible</span>'
    )
    # Says whether this picture is evidence about the current code or only about a file
    # that parses. `stored` is a standing reminder, not decoration: those diagrams predate
    # stored drafts, so nothing here can rebuild them.
    origin_badge = {
        PROVENANCE_MATERIALIZED: '<span class="badge repo" title="the pipeline built this '
                                 'picture during this run, from the draft">materialized</span>',
        PROVENANCE_STORED: '<span class="badge warn" title="no draft exists, so this is the '
                           'saved document drawn as it is">stored</span>',
        PROVENANCE_MISCITED: '<span class="badge err" title="a citation names something that is '
                             'not in the lines it points at">miscited</span>',
    }.get(c.provenance, '<span class="badge err">not produced</span>')

    if c.render_ok and c.before_svg:
        # The pair. Left is what a person left behind, right is what the host handed back,
        # and the sentence under them is the only thing a reviewer has to check: an
        # element that moved without being mentioned is, to the person who arranged it,
        # indistinguishable from their work being destroyed.
        moved = (f'<b class="bad">{len(c.moved)} moved</b> — {_esc(", ".join(c.moved[:4]))}'
                 if c.moved else '<b class="good">nothing moved</b>')
        changes = [f"<b>{c.held}</b> held in place", moved]
        if c.added:
            changes.append(f'added <code>{_esc(", ".join(c.added))}</code>')
        for gone in c.removed:
            hand = " (drawn by a person)" if gone.get("drawnBy") == "user" else ""
            lost = "".join(
                f' <span class="bad">— text lost: “{_esc(text)}”</span>'
                for text in gone.get("lostText") or ()
            )
            changes.append(
                f'removed <code>{_esc(gone["id"])}</code> '
                f'{_esc(gone["label"])}{hand}{lost}'
            )
        diagram = (
            '<div class="pair">'
            f'<figure><figcaption>before — as the person left it</figcaption>'
            f'<button class="diagram" type="button" data-open="{_esc(c.name)}-before" '
            f'data-half="before" title="Open before full size">{c.before_svg}</button>'
            f'{_editor_link(c.before_path, "Edit before")}</figure>'
            f'<figure><figcaption>after — one <code>diagram_update</code></figcaption>'
            f'<button class="diagram" type="button" data-open="{_esc(c.name)}" '
            f'data-half="after" title="Open after full size">{c.svg}</button>'
            f'{_editor_link(c.source_path, "Edit after")}</figure>'
            "</div>"
            f'<div class="scale-note">{" · ".join(changes)}</div>'
        )
    elif c.render_ok:
        # Scaling a 2,900px diagram into a 340px card puts a 16px composition diamond on
        # screen at under 2px, so the card is a thumbnail and the real look happens in the
        # overlay. Clicking anywhere on it opens the diagram at full size.
        width = _svg_width(c.svg)
        hint = f"{int(width)}px wide · click to open" if width else "click to open"
        diagram = (
            f'<button class="diagram" type="button" data-open="{_esc(c.name)}" '
            f'title="Open {_esc(c.name)} full size">{c.svg}</button>'
            f'<div class="scale-note">{hint}</div>'
        )
    else:
        diagram = f'<div class="diagram"><div class="render-err">render failed: {_esc(c.render_error)}</div></div>'

    # The ask that produced the edit, above everything else on the card. It is the one line
    # that explains why the two pictures differ, and a reviewer cannot judge whether the
    # right thing happened without it.
    ask = (
        f'<div class="ask"><span class="lbl">asked for</span>'
        f'<span class="q">{_esc(c.edit_request)}</span></div>'
        if c.edit_request else ""
    )

    # A pair puts a link under each half instead, because "Edit in GraphPilot" beside two
    # diagrams does not say which one it opens — the same ambiguity that made the zoom
    # button open the wrong half.
    open_in_editor = ""
    if c.source_path and not c.before_path:
        open_in_editor = _editor_link(c.source_path, "Edit in GraphPilot")

    if c.tags:
        tags = '<div class="tags">' + "".join(
            f'<span class="chip"><b>{_esc(k)}</b> {_esc(v)}</span>' for k, v in c.tags
        ) + "</div>"
    elif c.pool == "edited":
        # "no ## Tags block yet" is a prompt to go and write one, and there is nowhere to
        # write it: an edited example is a scenario, not a tagged corpus entry. Nagging
        # about a file that does not exist teaches a reviewer to ignore the line.
        tags = ""
    else:
        tags = '<div class="untagged">untagged — no ## Tags block yet</div>'

    errs = ""
    problems = c.errors + [f"[structural] {m}" for m in c.struct_issues]
    if problems:
        errs = '<ul class="errs">' + "".join(f"<li>{_esc(m)}</li>" for m in problems) + "</ul>"

    # The goal, not the ask. `request.original` is not an input to anything the page
    # renders, so showing it as the headline implied a prompt-to-diagram stage that
    # does not exist; the goal is what the diagram can actually be judged against.
    description = (
        f'<h4>Goal</h4><div class="goal">{_esc(c.goal)}</div>' if c.goal else ""
    )

    # Both source documents, carried inline so the page still works from a file:// URL
    # with no server. A reviewer who can only see the picture is judging whether it looks
    # tidy; the claim being reviewed is in the draft.
    sources, buttons = [], []
    for key, label, body in (
        ("draft", "Draft", c.draft_json),
        # The round trip in the order it happened: the draft the host was handed, the
        # diagram it was made from, the draft the host sent back, the diagram that
        # produced. A single "Diagram JSON" button beside two pictures does not say which
        # one it opens, and neither picture shows whether the host authored its change
        # correctly — only the submitted draft does.
        ("read-draft", "1 · Draft read", c.read_draft_json),
        ("before", "2 · Diagram before", c.before_json),
        ("submitted-draft", "3 · Draft submitted", c.submitted_draft_json),
        ("diagram", "4 · Diagram after" if c.before_json else "Diagram JSON", c.diagram_json),
        ("scenario", "Scenario (fixture)", c.scenario_json),
    ):
        if not body:
            continue
        source_id = f"src-{_slug(c.pool)}-{_slug(c.name)}-{key}"
        sources.append(
            f'<script type="application/json" id="{source_id}">{_script_safe(body)}</script>'
        )
        buttons.append(
            f'<button class="src-link" type="button" data-src="{source_id}" '
            f'data-title="{_esc(c.name)} · {label}">{label}</button>'
        )

    return (
        f'<article class="card" data-name="{_esc(c.name)}" '
        f'data-search="{_esc((c.name + " " + c.pool + " " + c.diagram_type).lower())}">'
        '<div class="card-head">'
        f'<div class="card-title"><span class="pool-tag">{_esc(c.pool)}/</span>{_esc(c.name)}</div>'
        f'<div class="badges">{valid_badge}{struct_badge}{faithful_badge}{legibility_badge}{counts_badge}{origin_badge}</div>'
        "</div>"
        f"{diagram}"
        '<div class="body">'
        f'{ask}{description}'
        f"{tags}{errs}"
        f'<div class="actions">{"".join(buttons)}{open_in_editor}</div>'
        f'{"".join(sources)}'
        "</div></article>"
    )


def _read(path: Path) -> str:
    """The file's text, or nothing. A missing source hides its button rather than failing."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _slug(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (text or "").lower())).strip("-") or "x"


def _script_safe(text: str) -> str:
    """Escape only what would end the script element early.

    A `<script>` block is CDATA, so ordinary HTML escaping would corrupt the JSON a
    reviewer reads. Only `</` can terminate it.
    """
    return text.replace("</", "<\\/")
