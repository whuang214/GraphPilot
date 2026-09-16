"""Offline tests for ``render_example_gallery``.

Prove the batch-review gallery plumbing: the management command writes **one**
self-contained HTML contact sheet over the real example pool, and the pure helpers
compute vocabulary coverage and render cards. No key /
network / Graphviz needed (``drawsvg`` only), so this runs in ``manage.py test``.
"""

import json
import re
import tempfile
from io import StringIO
from unittest import mock
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from operations.management.commands.render_example_gallery import (
    PROVENANCE_FAILED,
    PROVENANCE_MATERIALIZED,
    PROVENANCE_STORED,
    ExampleCard,
    _blueprints_dir,
    _coverage,
    _inline_svg,
    _render_card,
)
from services.diagrams.catalog.diagram_types import (
    SUPPORTED_DIAGRAM_TYPES,
    get_type_profile,
)


def _card(**over) -> ExampleCard:
    base = dict(
        diagram_type="activity_diagram", pool="answers", name="demo",
        svg="<svg><rect /></svg>", goal="Draw a flow.", tags=[("source", "reference")],
        review_status="approved", node_count=3, edge_count=2, valid=True,
        errors=[], struct_issues=[], render_ok=True, render_error="",
    )
    base.update(over)
    return ExampleCard(**base)


class CardDescriptionTests(SimpleTestCase):
    """A card describes the diagram's goal, and offers the draft rather than a view of it.

    There used to be a `prompt.md` per example, then a Prompt button rendering
    `request.original` out of the draft. Both are gone, for the same reason: **the ask is
    not an input to anything.** A diagram is materialized from elements, relationships and
    evidence, so putting the original request at the top of the card implied a
    prompt-to-diagram stage that does not exist, and the Prompt pane was a second view of
    a document already one button away.

    `goal` replaces it because a reviewer has to know what the diagram set out to show in
    order to judge whether it does.
    """

    def test_the_card_shows_the_goal(self):
        html = _render_card(_card(goal="Show how a payment reaches a recipient."))

        self.assertIn("Show how a payment reaches a recipient.", html)
        self.assertIn(">Goal</h4>", html)

    def test_the_card_never_offers_a_prompt(self):
        html = _render_card(_card(goal="Anything."))

        self.assertNotIn(">Prompt</h4>", html)
        self.assertNotIn(">Prompt</button>", html)

    def test_a_card_with_no_goal_simply_omits_the_description(self):
        html = _render_card(_card(goal=""))

        self.assertNotIn(">Goal</h4>", html)
        self.assertIn("<article", html)

    def test_the_only_source_panes_are_the_draft_and_the_diagram(self):
        """Both are JSON, which is why the page no longer carries a Markdown renderer."""
        html = _render_card(_card(
            goal="A goal.", draft_json='{"a": 1}', diagram_json='{"b": 2}',
        ))

        self.assertIn(">Draft</button>", html)
        self.assertIn(">Diagram JSON</button>", html)
        self.assertNotIn("x-markdown", html)
        self.assertNotIn("data-kind", html)


class CoverageTests(SimpleTestCase):
    def test_reports_missing_semantic_types(self):
        diagrams = [{
            "nodes": [
                {"data": {"semanticType": "initialNode"}},
                {"data": {"semanticType": "opaqueAction"}},
                {"data": {"semanticType": "activityFinalNode"}},
            ],
            "edges": [{"data": {"semanticType": "controlFlow"}}],
        }]
        cov = _coverage("activity_diagram", diagrams)
        self.assertTrue(cov.has_gap)
        self.assertIn("forkNode", cov.node_missing)
        self.assertIn("joinNode", cov.node_missing)
        self.assertNotIn("controlFlow", cov.edge_missing)  # control flow is present

    def test_no_gap_when_all_present(self):
        profile = get_type_profile("activity_diagram")
        nodes = [
            {"data": {"semanticType": semantic_type}}
            for semantic_type in profile.allowed_node_semantic_types
        ]
        edges = [
            {"data": {"semanticType": semantic_type}}
            for semantic_type in profile.allowed_edge_semantic_types
        ]
        diagrams = [{"nodes": nodes, "edges": edges}]
        cov = _coverage("activity_diagram", diagrams)
        self.assertFalse(cov.has_gap)
        self.assertEqual(cov.node_missing, [])
        self.assertEqual(cov.edge_missing, [])


class CardRenderTests(SimpleTestCase):
    def test_a_card_shows_its_diagram_prompt_and_chips(self):
        html = _render_card(_card(tags=[("authority", "conceptual"), ("cites", "0")]))
        self.assertIn("<svg>", html)
        self.assertIn("Draw a flow.", html)
        self.assertIn("conceptual", html)
        self.assertIn("badge ok", html)  # valid + structural ok

    def test_the_badge_says_whether_the_pipeline_built_this_picture(self):
        """A card the pipeline built is evidence about the current code. A card read off
        disk is only evidence that a file parses, and the page must not conflate them."""
        self.assertIn(">materialized<", _render_card(_card(provenance=PROVENANCE_MATERIALIZED)))
        self.assertIn(">stored<", _render_card(_card(provenance=PROVENANCE_STORED)))
        self.assertIn(">not produced<", _render_card(_card(provenance=PROVENANCE_FAILED)))

    def test_invalid_card_shows_errors(self):
        html = _render_card(_card(valid=False, errors=["boom"]))
        self.assertIn(">invalid<", html)
        self.assertIn("boom", html)

    def test_structural_issues_flagged(self):
        html = _render_card(_card(struct_issues=["two starts"]))
        self.assertIn("structural", html)
        self.assertIn("two starts", html)

    def test_render_failure_shown(self):
        html = _render_card(_card(render_ok=False, render_error="bad svg", svg=""))
        self.assertIn("render failed", html)
        self.assertIn("bad svg", html)

    def test_untagged_card_marked(self):
        html = _render_card(_card(tags=[], review_status="none"))
        self.assertIn("untagged", html)

    def test_the_goal_is_html_escaped(self):
        html = _render_card(_card(goal="a <b> & c"))
        self.assertIn("a &lt;b&gt; &amp; c", html)


class InlineSvgTests(SimpleTestCase):
    def test_strips_xml_prolog(self):
        svg = '<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="x"></svg>'
        self.assertTrue(_inline_svg(svg).startswith("<svg"))


class SourceViewerTests(SimpleTestCase):
    """A card carries the documents behind it, not only the picture.

    Reviewing a rendered diagram answers "does this look tidy". The claim being reviewed
    — which elements the host said exist, what it cited, what it admitted it was unsure
    of — is in the draft, and a notation rule can only be checked in the canonical JSON.
    """

    def _page(self, *args):
        with tempfile.TemporaryDirectory() as out_root:
            call_command("render_example_gallery", "--out", out_root, "--no-open",
                         *args, stdout=StringIO())
            run = next(Path(out_root).iterdir())
            return (run / "index.html").read_text(encoding="utf-8")

    def test_a_curated_card_offers_its_draft_and_its_diagram(self):
        page = self._page("--types", "bdd_diagram")
        for label in (">Draft<", ">Diagram JSON<"):
            self.assertIn(label, page)
        self.assertIn('type="application/json"', page)
        # Both panes are JSON now, so the page carries no Markdown renderer.
        self.assertNotIn('x-markdown', page)
        self.assertNotIn('>Prompt<', page)

    def test_the_payloads_are_the_documents_they_claim_to_be(self):
        page = self._page("--types", "bdd_diagram")
        payloads = {
            match.group(1): match.group(2)
            for match in re.finditer(
                r'<script type="application/[^"]+" id="(src-[^"]+)">(.*?)</script>', page, re.S
            )
        }
        drafts = [body for key, body in payloads.items() if key.endswith("-draft")]
        diagrams = [body for key, body in payloads.items() if key.endswith("-diagram")]
        self.assertTrue(drafts and diagrams)
        for body in drafts:
            parsed = json.loads(body)
            self.assertEqual(parsed["kind"], "diagramDraft")
            self.assertIn("requests", parsed)
        for body in diagrams:
            parsed = json.loads(body)
            # `origin` is built by materialization; a draft never carries one.
            self.assertTrue(all(node.get("origin") for node in parsed["nodes"]))

    def test_a_closing_tag_inside_a_payload_cannot_end_the_script_early(self):
        """`</` is the one sequence that terminates a script element."""
        page = self._page("--types", "bdd_diagram")
        for block in re.findall(r'<script type="application/[^"]+" id="src-[^"]+">(.*?)</script>',
                                page, re.S):
            self.assertNotIn("</", block)

    def test_the_type_filter_applies_to_every_pool(self):
        """A page narrowed to one type must not show a card of another, from anywhere."""
        page = self._page("--types", "bdd_diagram")
        self.assertIn("bdd_diagram", page)
        self.assertNotIn("use_case_diagram", page)
        self.assertNotIn("activity_diagram", page)

    def test_a_generated_card_names_the_repository_it_came_from(self):
        page = self._page("--pools", "generated")
        self.assertIn("<b>repository</b>", page)

    def test_an_example_without_a_draft_is_marked_stored_not_silently_drawn(self):
        """Nothing can rebuild it, and a page that hides that is claiming more than it knows.

        The nine corpus diagrams are in this state: they were generated before
        `diagram_create` kept the draft, so the saved document is all there is.
        """
        page = self._page("--pools", "generated")
        if not (_blueprints_dir() / "bdd_diagram" / "examples" / "generated").exists():
            self.skipTest("no generated pool on disk")
        drafted = list((_blueprints_dir()).glob("*/examples/generated/*/draft.json"))
        if drafted:
            self.assertIn(">materialized<", page)
        else:
            self.assertIn(">stored<", page)


class RegenTests(SimpleTestCase):
    """`--regen` rewrites what a draft produces, and never the draft."""

    def test_regen_eval_is_idempotent_on_a_clean_tree(self):
        """The property that makes it usable: running it changes nothing unless the
        transform changed. Without it every run produces a diff and "no diff" stops being
        evidence of anything — which it did, until `createdAt` was carried forward.
        """
        before = {
            path: path.read_bytes()
            for path in _blueprints_dir().glob("*/examples/answers/*/output.gp.json")
        }
        self.assertTrue(before)

        call_command("render_example_gallery", "--regen", "eval", "--pools", "answers",
                     "--out", tempfile.mkdtemp(), "--no-open", stdout=StringIO())

        unchanged = [p for p, data in before.items() if p.read_bytes() == data]
        self.assertEqual(len(unchanged), len(before),
                         "regen eval rewrote a file it should have left alone")

    def test_regen_never_writes_a_draft(self):
        """A draft is source. Regenerating one would regenerate the answer from itself."""
        before = {
            path: path.read_bytes()
            for path in _blueprints_dir().glob("*/examples/*/*/draft.json")
        }
        self.assertTrue(before)

        call_command("render_example_gallery", "--regen", "eval",
                     "--out", tempfile.mkdtemp(), "--no-open", stdout=StringIO())

        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data, f"{path.parent.name}'s draft was rewritten")

    def test_regen_generated_needs_a_corpus_and_says_so(self):
        with tempfile.TemporaryDirectory() as out:
            with self.assertRaises(CommandError) as caught:
                call_command("render_example_gallery", "--regen", "generated",
                             "--corpus", str(Path(out) / "nowhere"),
                             "--out", out, "--no-open", stdout=StringIO())
        self.assertIn("corpus-run", str(caught.exception))


class BrowserTests(SimpleTestCase):
    """The command opens a browser for a person, and must not for anything else.

    `--open` defaults to on because a gallery nobody looks at has not been reviewed. That
    is wrong for every non-human caller: these tests write to a temp directory that is
    deleted the moment they finish, so before this guard existed every suite run left a
    handful of browser tabs pointing at files that no longer existed.
    """

    def test_a_captured_stdout_never_opens_a_browser(self):
        with tempfile.TemporaryDirectory() as out_root:
            with mock.patch("webbrowser.open") as opener:
                call_command(
                    "render_example_gallery",
                    "--types", "bdd_diagram",
                    "--out", out_root,
                    stdout=StringIO(),
                )
        opener.assert_not_called()

    def test_no_open_is_honoured_even_from_a_terminal(self):
        with tempfile.TemporaryDirectory() as out_root:
            stream = StringIO()
            stream.isatty = lambda: True  # pretend a person is watching
            with mock.patch("webbrowser.open") as opener:
                call_command(
                    "render_example_gallery",
                    "--types", "bdd_diagram",
                    "--out", out_root,
                    "--no-open",
                    stdout=stream,
                )
        opener.assert_not_called()


class CommandTests(SimpleTestCase):
    def test_writes_single_contact_sheet_over_real_pool(self):
        with tempfile.TemporaryDirectory() as out:
            stdout = StringIO()
            call_command("render_example_gallery", "--out", out, stdout=stdout)
            indexes = list(Path(out).glob("*/index.html"))
            self.assertEqual(len(indexes), 1)
            content = indexes[0].read_text(encoding="utf-8")
        self.assertIn("review gallery", content)
        self.assertIn("Vocabulary coverage", content)
        self.assertIn('<article class="card"', content)
        self.assertIn('class="chip"', content)
        self.assertIn("examples).", stdout.getvalue())

    def test_the_pools_are_grouped_and_filterable(self):
        """Grouping by diagram type first buried the pools worth reviewing.

        The nine generated diagrams split three ways behind twelve answers each, and the
        three worked examples one at a time. A reviewer arrives with one question, and the
        question maps to a pool — so the pool is the heading.

        The header used to hold a jump link per pool. A jump still leaves thirty-six
        answers between the reviewer and what they came for, and scrolling past them is
        exactly how the newest pool became invisible to the person who asked for it. They
        are filters now: choosing a pool hides the others.
        """
        with tempfile.TemporaryDirectory() as out:
            call_command("render_example_gallery", "--out", out, "--no-open", stdout=StringIO())
            content = list(Path(out).glob("*/index.html"))[0].read_text(encoding="utf-8")

        for pool in ("edited", "training", "generated", "answers"):
            self.assertIn(f'<section class="pool-section" data-pool="{pool}"', content)
            self.assertIn(f'data-filter="pool" data-value="{pool}"', content)
        for kind in ("activity_diagram", "use_case_diagram", "bdd_diagram"):
            self.assertIn(f'data-filter="type" data-value="{kind}"', content)
            self.assertIn(f'<div class="type-block" data-type="{kind}"', content)

        # Reviewed most often first; answers are guarded by a test on every run.
        order = [content.index(f'data-pool="{p}"')
                 for p in ("edited", "training", "generated", "answers")]
        self.assertEqual(order, sorted(order))

    def test_the_reference_panels_do_not_push_the_cards_below_the_fold(self):
        """Legibility and vocabulary coverage are reference a reviewer consults, not the
        thing they came for. Open by default they pushed the first pool off the screen,
        which is how a newly added pool went unnoticed."""
        with tempfile.TemporaryDirectory() as out:
            call_command("render_example_gallery", "--out", out, "--no-open", stdout=StringIO())
            content = list(Path(out).glob("*/index.html"))[0].read_text(encoding="utf-8")

        self.assertIn('<details class="panels">', content)
        self.assertNotIn('<details class="panels" open>', content)
        self.assertLess(
            content.index('<details class="panels">'),
            content.index('<section class="pool-section"'),
        )

    def test_an_edited_card_offers_both_halves_and_the_ask(self):
        """A single "Diagram JSON" button beside two diagrams does not say which one it
        opens, and the pictures alone do not show that a `description` nobody mentioned
        came through untouched — only the documents do.

        Every button has to name a payload that exists, or it opens an empty panel.
        """
        with tempfile.TemporaryDirectory() as out:
            call_command("render_example_gallery", "--out", out, "--no-open", stdout=StringIO())
            content = list(Path(out).glob("*/index.html"))[0].read_text(encoding="utf-8")

        card = content[content.index('data-name="catalogue-ends"'):]
        card = card[: card.index("</article>")]

        buttons = re.findall(r'data-src="([^"]+)"[^>]*>([^<]+)<', card)
        self.assertEqual(
            [label for _, label in buttons],
            ["1 · Draft read", "2 · Diagram before", "3 · Draft submitted",
             "4 · Diagram after", "Scenario (fixture)"],
        )
        for source_id, label in buttons:
            with self.subTest(button=label):
                self.assertIn(f'<script type="application/json" id="{source_id}">', card)

        # The ask that produced the edit, on the card rather than buried in the scenario.
        self.assertIn("A product has at least one variant", card)
        self.assertIn('class="ask"', card)
        # And the two payloads are genuinely different documents. Sliced from the script
        # tag rather than from the id: the id appears first in the button's `data-src`,
        # and slicing from there reads whichever payload happens to come next.
        def payload(key):
            opening = f'<script type="application/json" id="src-edited-catalogue-ends-{key}">'
            start = card.index(opening) + len(opening)
            return card[start: card.index("</script>", start)]

        self.assertNotIn("suppliedBy", payload("before"))
        self.assertIn("suppliedBy", payload("diagram"))
        # And the two drafts, which are the documents the product actually exchanges.
        self.assertNotIn("suppliedBy", payload("read-draft"))
        self.assertIn("suppliedBy", payload("submitted-draft"))
        self.assertIn('"basis"', payload("submitted-draft"))

    def test_the_type_filter_covers_every_registered_diagram_type(self):
        """There will be more diagram types than three.

        Adding one must put it in the filter, in its own section and in the search index
        without anybody editing the gallery — so this asserts the chips *are* the
        registered types rather than a list that happens to match today.
        """
        with tempfile.TemporaryDirectory() as out:
            call_command("render_example_gallery", "--out", out, "--no-open", stdout=StringIO())
            content = list(Path(out).glob("*/index.html"))[0].read_text(encoding="utf-8")

        chips = set(re.findall(r'data-filter="type" data-value="([^"]+)"', content))
        blocks = set(re.findall(r'<div class="type-block" data-type="([^"]+)"', content))

        self.assertEqual(chips, set(SUPPORTED_DIAGRAM_TYPES))
        self.assertEqual(blocks, set(SUPPORTED_DIAGRAM_TYPES))

    def test_the_filter_bar_cannot_grow_without_limit(self):
        """The header is sticky. Three types wrap to one line; a dozen would wrap to four
        and push the first pool of cards under the fold — which is precisely how a whole
        pool went unnoticed once. It scrolls past a fixed share of the viewport instead."""
        with tempfile.TemporaryDirectory() as out:
            call_command("render_example_gallery", "--out", out, "--no-open", stdout=StringIO())
            content = list(Path(out).glob("*/index.html"))[0].read_text(encoding="utf-8")

        rule = re.search(r"\.filters \.chips \{([^}]+)\}", content)
        self.assertIsNotNone(rule, "the chip strip has no sizing rule")
        self.assertRegex(rule.group(1), r"max-height:\s*\d+")
        self.assertIn("overflow-y: auto", rule.group(1))

        # And the way out of a filter is not inside the part that scrolls.
        chips = content.index('<div class="chips">')
        controls = content.index('<div class="controls">')
        self.assertLess(chips, controls)
        self.assertGreater(content.index('id="search"'), controls)
        self.assertGreater(content.index('id="reset"'), controls)

    def test_a_pair_is_scaled_to_fit_rather_than_cropped(self):
        """`.diagram` clips at 320px, which is right for a thumbnail you click into and
        wrong for a pair: the change an edit makes is almost never at the *top* of a
        drawing, so both halves showed the same unchanged header and all six cards looked
        identical. Six cards whose entire purpose is to show a difference, showing none.
        """
        with tempfile.TemporaryDirectory() as out:
            call_command("render_example_gallery", "--out", out, "--no-open", stdout=StringIO())
            content = list(Path(out).glob("*/index.html"))[0].read_text(encoding="utf-8")

        rule = re.search(r"\.pair \.diagram svg \{([^}]+)\}", content)
        self.assertIsNotNone(rule, "no sizing rule for a pair's diagrams")
        self.assertIn("max-height", rule.group(1))
        self.assertRegex(
            content, r"\.pair \.diagram \{[^}]*overflow: visible",
            "a pair that clips hides the very thing it exists to show",
        )

    def test_an_edited_card_does_not_nag_about_a_tags_block(self):
        """There is nowhere to write one: an edited example is a scenario, not a tagged
        corpus entry, and a prompt pointing at a file that cannot exist gets ignored —
        along with the rest of the line it sits on."""
        with tempfile.TemporaryDirectory() as out:
            call_command("render_example_gallery", "--out", out, "--no-open", stdout=StringIO())
            content = list(Path(out).glob("*/index.html"))[0].read_text(encoding="utf-8")

        card = content[content.index('data-name="catalogue-ends"'):]
        self.assertNotIn("untagged", card[: card.index("</article>")])

    def test_a_card_carries_what_the_name_search_matches_on(self):
        with tempfile.TemporaryDirectory() as out:
            call_command("render_example_gallery", "--out", out, "--no-open", stdout=StringIO())
            content = list(Path(out).glob("*/index.html"))[0].read_text(encoding="utf-8")

        self.assertIn('data-search="checkout-refunds edited bdd_diagram"', content)

    def test_type_and_pool_filters(self):
        with tempfile.TemporaryDirectory() as out:
            call_command(
                "render_example_gallery",
                "--types", "activity_diagram", "--pools", "answers",
                "--out", out, stdout=StringIO(),
            )
            content = list(Path(out).glob("*/index.html"))[0].read_text(encoding="utf-8")
        self.assertIn("activity_diagram", content)
        self.assertNotIn("use_case_diagram", content)

    def test_sole_layout_engine_renders_without_mutating_sources(self):
        source = (
            Path(__file__).resolve().parents[2]
            / "assets/blueprints/activity_diagram/examples/answers/01-ecommerce-checkout/output.gp.json"
        )
        before = source.read_bytes()
        with tempfile.TemporaryDirectory() as out:
            call_command(
                "render_example_gallery",
                "--types",
                "activity_diagram",
                "--pools",
                "answers",
                "--out",
                out,
                stdout=StringIO(),
            )
            content = list(Path(out).glob("*/index.html"))[0].read_text(encoding="utf-8")
        self.assertIn("layout pygraphviz-dot", content)
        self.assertEqual(source.read_bytes(), before)

    def test_unknown_type_is_rejected(self):
        with tempfile.TemporaryDirectory() as out:
            with self.assertRaises(CommandError):
                call_command("render_example_gallery", "--types", "unknown", "--out", out)

    def test_unknown_pool_is_rejected(self):
        with tempfile.TemporaryDirectory() as out:
            with self.assertRaises(CommandError):
                call_command("render_example_gallery", "--pools", "unknown", "--out", out)
