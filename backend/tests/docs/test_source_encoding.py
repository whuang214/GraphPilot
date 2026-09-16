"""No committed source file carries a byte-order mark or mojibake.

`AGENTS.md` has warned about this since it was written: Windows PowerShell 5.1 writes a BOM
with `-Encoding UTF8`, and a `Get-Content`/`Set-Content` round-trip turns an em dash into
three bytes of Latin-1 wreckage. It corrupted source and documentation three times in one
session before anyone noticed.

Nothing enforced it, and the reason it survives is that nothing breaks. Python imports a
BOM'd module happily and the suite stays green — `test_note_placement.py` had carried one
for long enough that no commit remembers, and it surfaced only when an audit script tried
to `ast.parse` the raw bytes. A convention that is only ever written down is a convention
that drifts.

Two details this test learned by getting them wrong. It walks **git-tracked files only**,
because the first version policed `.playwright-cli/` captures that are gitignored tool
output and nobody's to fix. And the corruption signatures are built from escapes rather
than typed literally, because the first version flagged itself for quoting the bytes it
looks for.
"""

import re
import subprocess
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

ROOT = Path(settings.BASE_DIR).parent
#: Everything a person edits by hand.
#:
#: `.example` and `.txt` were missing, which left `backend/.env.example` unscanned — a
#: hand-edited file, in the one directory where the instruction is literally "copy this
#: and edit it", and the file an operator's own `.env` is cloned from. The set is defined
#: by who edits the file, not by whether the interpreter would notice.
SUFFIXES = {
    ".py", ".md", ".json", ".ts", ".tsx", ".css", ".html", ".yaml", ".yml",
    ".example", ".txt",
}

#: What UTF-8 looks like after being read as Latin-1 and written back. Spelled with escapes
#: so this file does not contain the thing it forbids.
#:
#: The mangled-guillemet case was added after `elementCatalog.ts` was found carrying a
#: corrupted `«keyword»` — for long enough that no commit remembers, with this check green
#: the whole time. An em dash is the character that gets mangled most often and it is not
#: the only one: guillemets are all over the notation code, because every stereotype is
#: drawn in them.
#:
#: Written as escapes, like everything else here. The paragraph above deliberately shows
#: the *intact* characters and never the broken ones — quoting the corruption is how the
#: first version of this file flagged itself, and how this line did too, one edit ago.
_MOJIBAKE = re.compile(
    "\u00e2\u20ac|\u00c3\u00a2|\u00c2[\u00ab\u00bb\u00a0]"
)

#: `AGENTS.md` has to show the corrupted characters to explain them. It is the only file
#: allowed to, and naming it here is cheaper than teaching the check about prose.
ALLOWED = {"AGENTS.md"}


def _tracked():
    """Every committed file we are responsible for the bytes of."""
    listing = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split("\0")
    for name in listing:
        if not name:
            continue
        path = ROOT / name
        if path.suffix in SUFFIXES and path.is_file():
            yield path


class SourceEncodingTests(SimpleTestCase):
    def test_no_file_carries_a_byte_order_mark(self):
        """Invisible, harmless to the interpreter, and it breaks every tool that reads the
        bytes rather than importing them."""
        marked = [
            p.relative_to(ROOT).as_posix()
            for p in _tracked()
            if p.read_bytes().startswith(b"\xef\xbb\xbf")
        ]

        self.assertEqual(marked, [], "written by PowerShell -Encoding UTF8; strip the BOM")

    def test_no_file_carries_mojibake(self):
        corrupted = [
            p.relative_to(ROOT).as_posix()
            for p in _tracked()
            if p.name not in ALLOWED
            and _MOJIBAKE.search(p.read_text(encoding="utf-8", errors="replace"))
        ]

        self.assertEqual(corrupted, [], "a UTF-8 round-trip mangled these; re-edit them")

    def test_the_check_can_actually_see_a_bad_file(self):
        """A guard nobody has watched fail is a guard nobody knows works — and both of the
        assertions above passed, wrongly, in their first version."""
        self.assertTrue(b"\xef\xbb\xbf".startswith(b"\xef\xbb\xbf"))
        self.assertTrue(_MOJIBAKE.search("an em dash \u00e2\u20ac\u201d mangled"))
        self.assertTrue(_MOJIBAKE.search("a \u00c2\u00abkeyword\u00c2\u00bb mangled"))
        self.assertIsNone(_MOJIBAKE.search("an em dash — intact"))
        self.assertIsNone(_MOJIBAKE.search("a «keyword» intact"))

    def test_the_walk_reaches_the_files_it_claims_to(self):
        """The detectors above were watched failing; the *selection* never was.

        Both checks pass vacuously for any file `_tracked` does not yield, and for two
        years it did not yield `.env.example` — no suffix in the set matched it. A
        detector that works on a file it never opens is the same broken instrument as one
        that cannot detect anything.
        """
        scanned = {p.relative_to(ROOT).as_posix() for p in _tracked()}

        for expected in ("AGENTS.md", "backend/.env.example", "requirements.txt",
                         "backend/graphpilot/settings.py", "frontend/src/index.css"):
            with self.subTest(path=expected):
                self.assertIn(expected, scanned)
