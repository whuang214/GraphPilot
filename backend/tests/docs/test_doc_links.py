"""Every relative link in the active documentation resolves to a file that exists.

The whole documentation strategy is "one owner per topic — link, don't restate". That
makes a link a load-bearing structure rather than a convenience, and **nothing had ever
checked that one resolves.** The final audit found three broken ones by accident: the
status board pointed at a `plan.md` deleted when its program closed, and the `corpus-run`
skill twice linked to the document it calls canonical using a path that only worked from
the repository root.

Scope is the active set plus the tracked agent files. `docs/06-research/` and
`docs/07-history/` are excluded on purpose: history is frozen and must never be edited,
and research describes designs that were considered rather than shipped — 37 of its links
point at documents the restructure moved, and repairing them would mean editing frozen
records to describe a system they were never about.
"""

import re
import subprocess
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

ROOT = Path(settings.BASE_DIR).parent
EXCLUDED = {"node_modules", "06-research", "07-history", "review_galleries", "dist"}

#: `[text](target)` — skipping absolute URLs and pure anchors.
LINK = re.compile(r"\]\((?!https?://|mailto:|#)([^)#\s]+)")


def _tracked_paths():
    listing = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    return {ROOT / name for name in listing.split("\0") if name}


def _active_documents():
    for path in sorted(_tracked_paths()):
        relative = path.relative_to(ROOT)
        if (path.suffix == ".md" and EXCLUDED.isdisjoint(relative.parts)
                and not any(part.startswith(".") for part in relative.parts[:-1])):
            yield path


class DocumentLinkTests(SimpleTestCase):
    def test_every_relative_link_resolves(self):
        broken = []
        published = _tracked_paths()
        published.update(parent for path in tuple(published) for parent in path.parents
                         if parent == ROOT or ROOT in parent.parents)
        for path in _active_documents():
            text = path.read_text(encoding="utf-8", errors="replace")
            for target in LINK.findall(text):
                resolved = (path.parent / target).resolve()
                if not resolved.exists() or resolved not in published:
                    broken.append(f"{path.relative_to(ROOT).as_posix()} -> {target}")

        self.assertEqual(broken, [], "an active link points outside the published repository")

    def test_the_walk_actually_reaches_the_documents(self):
        """Guard the instrument: an over-eager exclude list makes the check vacuous."""
        found = {p.relative_to(ROOT).as_posix() for p in _active_documents()}

        for required in ("README.md", "AGENTS.md", "docs/README.md",
                         "docs/05-delivery/01-current-state.md",
                         "docs/04-development/01-environment.md",
                         "docs/04-development/06-delivery-workflow.md"):
            with self.subTest(document=required):
                self.assertIn(required, found)
        self.assertGreater(len(found), 30)

    def test_the_pattern_finds_links(self):
        """And that the regex matches the shapes this repository actually writes."""
        sample = "see [`a`](docs/x.md) and [b](../y.md#frag) but not [c](https://z) or [d](#top)"

        self.assertEqual(LINK.findall(sample), ["docs/x.md", "../y.md"])
