"""Is the drawn diagram actually readable?

Measured **from the SVG that was produced**, not from a model of what the layout should
have done. A model agrees with itself; only the drawn output can disagree.

Three ways a string fails a reader, all counted the same way — find where the text was
actually placed, then ask whether it landed somewhere it can be read:

* **clipped** — outside the node that owns it, so the node's own text spills past its edge
* **buried** — inside a node it does not belong to, so it reads as that node's content
* **collided** — overlapping another string, so both are unreadable

This lived in the review gallery, computed for a page nobody but a reviewer sees. The
author of a diagram delegates layout entirely — *"you supply the semantics, GraphPilot
supplies the notation, layout, validation"* — and then got no word on whether the one
thing they delegated had worked. Three cold hosts said so independently. It is a service
now so `diagram_create` can say.
"""

import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping

from services.diagrams.catalog.constants import CHAR_WIDTH_RATIO, FONT_SIZE, feature_compartments
from services.shared.operation_problem import operation_warning

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Offender:
    """One string a reader cannot read, and what it clashed with."""

    kind: str
    text: str
    collides_with: str = ""


@dataclass(frozen=True)
class Legibility:
    """The counts, and the strings behind them.

    Both halves matter, and they answer different questions. The counts say whether the
    renderer is improving across a corpus; the offenders say **which label to look at**,
    which is the only question the author of one diagram has. Reporting the first without
    the second sent a host to parse the SVG by hand to find its three collisions.
    """

    counts: Counter
    offenders: List[Offender] = field(default_factory=list)

    @property
    def illegible(self) -> int:
        return sum(value for key, value in self.counts.items() if key != "texts")

    @property
    def texts(self) -> int:
        return self.counts.get("texts", 0)

_TEXT_TAG = re.compile(r"<text\b([^>]*)>([^<]*)</text>")
_ATTR_X = re.compile(r'\bx="([\d.\-]+)"')
_ATTR_Y = re.compile(r'\by="([\d.\-]+)"')
_ATTR_SIZE = re.compile(r'font-size="([\d.]+)"')
_ATTR_ANCHOR = re.compile(r'text-anchor="(\w+)"')

#: A compartment heading is drawn by the renderer, not authored, so it is always "owned"
#: by the block it sits in. Treating it as foreign would report every BDD block as buried.
_COMPARTMENT_HEADINGS = {
    "value properties", "part properties", "reference properties", "constraint properties",
    "flow properties", "operations", "constraints", "literals", "receptions",
    "extension points",
}


def text_boxes(svg: str) -> List[Dict[str, float]]:
    """Where each drawn string actually sits, in diagram coordinates."""
    boxes: List[Dict[str, Any]] = []
    for match in _TEXT_TAG.finditer(svg):
        attrs, content = match.group(1), match.group(2)
        if not content.strip():
            continue
        x_match, y_match = _ATTR_X.search(attrs), _ATTR_Y.search(attrs)
        if not x_match or not y_match:
            continue
        x, y = float(x_match.group(1)), float(y_match.group(1))
        size_match = _ATTR_SIZE.search(attrs)
        size = float(size_match.group(1)) if size_match else float(FONT_SIZE)
        width = len(content) * size * CHAR_WIDTH_RATIO
        anchor_match = _ATTR_ANCHOR.search(attrs)
        anchor = anchor_match.group(1) if anchor_match else "start"
        left = x - width / 2 if anchor == "middle" else (x - width if anchor == "end" else x)
        boxes.append({
            "text": content.strip(), "left": left, "right": left + width,
            "top": y - size * 0.8, "bottom": y + size * 0.25,
        })
    return boxes


def _owns(text: str, owned: set) -> bool:
    """Is this drawn string part of the node's own content?

    The renderer wraps, truncates and escapes, so an exact match is far too strict — a
    drawn string is usually a fragment. Getting this wrong inflates the count: an edge
    label landing on a block is the *label* being misplaced, not the block clipping.
    """
    value = text.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&").strip(" \u2026")
    if not value or value.startswith("\u00ab") or value.lower() in _COMPARTMENT_HEADINGS:
        return True
    return any(value in item or item.startswith(value) or value.startswith(item[:24])
               for item in owned)


def measure(diagram: Mapping[str, Any], svg: str) -> "Legibility":
    """Count text clipped by its own node, buried under a foreign one, or overlapping.

    Returns a `Legibility`: `counts` is a `Counter` with `texts` (how many strings were
    drawn) plus one entry per failure kind, and `offenders` names the strings themselves.
    A `counts` empty beyond `texts` means every string is readable.

    The signature said `-> Counter` and the sentence above said the same, for as long as
    both have existed. It is the `counts` field that is a `Counter`; the return has never
    been one. A caller trusting either would reach for `.most_common` and get an
    `AttributeError`, and a type checker would agree with the annotation rather than the
    code — which is the whole reason to write one down.
    """
    from services.diagrams.rendering.diagram_render_service import CONTAINER_SEMANTIC_TYPES

    by_id = {node["id"]: node for node in diagram.get("nodes") or []}
    placed = []
    for node in by_id.values():
        # Child coordinates are relative to the parent, so a nested node has to be walked
        # up to absolute before its box can be compared with a drawn string.
        x, y = node["position"]["x"], node["position"]["y"]
        parent, seen = node.get("parentId"), set()
        while parent and parent in by_id and parent not in seen:
            seen.add(parent)
            x += by_id[parent]["position"]["x"]
            y += by_id[parent]["position"]["y"]
            parent = by_id[parent].get("parentId")
        data = node.get("data") or {}
        if data.get("semanticType") in CONTAINER_SEMANTIC_TYPES:
            continue  # a label over a boundary is normal
        owned = {str(data.get("label", "")).strip()}
        for heading, items in feature_compartments(data.get("features")):
            owned.add(heading)
            owned.update(items)
        # A use case draws its extension points inside itself, same as a compartment row.
        owned.update(str(point).strip() for point in (data.get("extensionPoints") or []))
        placed.append({
            "owned": {v for v in owned if v}, "left": x, "top": y,
            "right": x + (node.get("width") or 0), "bottom": y + (node.get("height") or 0),
        })

    texts = text_boxes(svg)
    tally: Counter = Counter(texts=len(texts))
    offenders: List[Offender] = []

    def note(kind: str, text: str, other: str = "") -> None:
        tally[kind] += 1
        offenders.append(Offender(kind=kind, text=text, collides_with=other))

    for box in texts:
        cx, cy = (box["left"] + box["right"]) / 2, (box["top"] + box["bottom"]) / 2
        inside = next((n for n in placed
                       if n["left"] <= cx <= n["right"] and n["top"] <= cy <= n["bottom"]), None)
        if inside is None:
            # A string can overflow so far that its own midpoint leaves the node, and
            # matching on the midpoint alone let the *worst* cases through uncounted. If
            # some node it overlaps claims the text as its own, that node is its owner and
            # the text is outside it by definition.
            inside = next(
                (n for n in placed
                 if box["left"] < n["right"] and n["left"] < box["right"]
                 and box["top"] < n["bottom"] and n["top"] < box["bottom"]
                 and _owns(box["text"], n["owned"])),
                None,
            )
            if inside is not None:
                note("clipped", box["text"])
            continue
        if not _owns(box["text"], inside["owned"]):
            note("buried", box["text"])
        elif (box["left"] < inside["left"] - 1 or box["right"] > inside["right"] + 1
              or box["top"] < inside["top"] - 1 or box["bottom"] > inside["bottom"] + 1):
            note("clipped", box["text"])

    for index, first in enumerate(texts):
        for second in texts[index + 1:]:
            if (first["left"] < second["right"] - 1 and second["left"] < first["right"] - 1
                    and first["top"] < second["bottom"] - 1 and second["top"] < first["bottom"] - 1):
                note("collided", first["text"], second["text"])
                break
    return Legibility(counts=tally, offenders=offenders)


def warning_for(diagram: Mapping[str, Any], svg_path: Path) -> List[Dict[str, Any]]:
    """Tell the author when the picture came out hard to read.

    The division of labour is that a host supplies semantics and GraphPilot supplies
    layout — so an author who delegates layout entirely and is told nothing about whether
    it worked has no way to judge the one thing they delegated. Three cold hosts said
    exactly that, one having shipped a 26-node diagram against `operationWarnings: []`.

    A warning, never a refusal: the diagram is correct, and how many elements belong in
    one picture is the author's call to make with the information in front of them.

    Lives here rather than in the create service because both create and update need it.
    It was `_legibility_warning` there, and the update service imported it by that private
    name — an implementation detail doing the job of a contract, with nothing saying the
    two services had agreed on it. This module already owns `measure` and `describe`; the
    sentence they produce for a host belongs beside them.
    """
    try:
        result = measure(diagram, svg_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, KeyError, TypeError, ValueError):
        # Legibility is advice. Failing to compute it must not cost a saved diagram.
        logger.debug("Could not measure legibility for %s", svg_path, exc_info=True)
        return []
    message = describe(result)
    if not message:
        return []
    return [operation_warning(
        "hard_to_read",
        message,
        retryable=False,
        illegible=result.illegible,
        textCount=result.texts,
        # The strings themselves, so a host does not have to read the SVG to find them.
        labels=[
            {"kind": o.kind, "text": o.text, **({"collidesWith": o.collides_with}
                                                if o.collides_with else {})}
            for o in result.offenders[:20]
        ],
    )]


def _clip(text: str, width: int = 44) -> str:
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 1] + "\u2026"


def describe(result: Legibility) -> str:
    """Name the strings, say the layout is ours, and send the judgement to the person.

    Naming the strings is the half that has always worked — the first version reported
    *"3 of 160 labels are hard to read"* and left the author to find them by parsing the
    SVG. A host praised the named version for making the decision a ten-second one.

    Advising a fix is the half that never has. Three attempts, three falsified:

    1. *"shorten your labels"* — every collision it flagged was between two strings
       **GraphPilot places**, which shortening an element label does not move.
    2. *"fewer elements is the lever left"* — one host shortened two guards instead and
       the collision cleared; another removed a node as instructed and watched the
       collision move to the next pair.
    3. *"a shorter string is a smaller box… failing that, it is crowding"* — a host
       pulled both in order. The first changed nothing. The second took the collisions
       from one to two.

    The pattern is not bad wording, it is a category error. **Placement is entirely
    GraphPilot's**: the layout engine positions nodes and the renderer positions end
    labels. A host authors semantics and never a coordinate, so a collision is our defect
    and it holds no lever at all — only the side effect that different text is a
    different box size, which perturbs our layout into some other arrangement.

    Acting on that side effect costs the diagram's meaning. The host that cleared its
    collisions did it by flattening every guard to `yes`/`no` and demoting a decision to
    a note, and reported the trade honestly. That is the model being damaged to patch the
    rendering.

    So this asks for nothing. It reports, and points at the editor — where someone can
    see the picture and drag a label in seconds.
    """
    if not result.illegible:
        return ""
    kinds = {
        "clipped": "spills outside its own element",
        "buried": "sits on an element it does not belong to",
        "collided": "overlaps",
    }
    lines = []
    for offender in result.offenders[:6]:
        described = kinds.get(offender.kind, offender.kind)
        if offender.kind == "collided" and offender.collides_with:
            lines.append(f"{_clip(offender.text)!r} {described} {_clip(offender.collides_with)!r}")
        else:
            lines.append(f"{_clip(offender.text)!r} {described}")
    more = result.illegible - len(lines)
    listed = "; ".join(lines) + (f"; and {more} more" if more > 0 else "")

    # The advice is per-offender, not a law about legibility. Two hosts read the second
    # branch below as one: one shortened its labels on the strength of the first message,
    # watched it work (137 labels to 117, five collisions to one), and was then told by
    # the second that shortening "will not move them". Both sentences were locally true
    # and the pair was incoherent, because each was phrased as a general rule.
    #
    # A third case was missing entirely. A host drew two compositions whose ends both
    # carried the role `memberships`, truthfully, because both are named that in the
    # source — and got a collision between two *identical* strings on a twelve-element
    # diagram, advised that fewer elements was its only lever. The lever was to
    # distinguish the two role names, which this already knows about: `collides_with`
    # holds the same text.
    # No levers. Three attempts at naming one have now been falsified by hosts, and the
    # reason is structural rather than editorial: **GraphPilot owns placement.** Node
    # coordinates come from the layout engine and end labels are positioned by the
    # renderer, so a collision is our defect. A host's only influence is that changing
    # its text changes a box size and perturbs our layout into some other arrangement —
    # indirect, unpredictable, and it costs the diagram's meaning.
    #
    # Run 5 measured that cost. One host pulled both advertised levers in order:
    # shortening the guards changed nothing, and removing a decision node took the
    # collisions from one to two. It cleared them on the fourth try by reducing every
    # guard to `yes`/`no` and demoting a real decision to a note — it damaged the model
    # to fix our rendering, and said so. Three of its six `diagram_create` calls went on
    # this; across the run, every wasted call was a legibility retry and no draft was
    # ever refused on its merits.
    #
    # So the message stops assigning work. It names the strings, says whose problem it
    # is, and sends the judgement to the one participant who can see the picture.
    return (
        f"{result.illegible} of {result.texts} labels are hard to read — {listed}. "
        "**This is a warning, not a refusal, and not yours to fix.** GraphPilot places "
        "every node and every end label, so overlapping text is a limitation of its "
        "layout, not a mistake in your draft. Do not reword, drop or restructure "
        "anything to clear it: that changes what the diagram says, and has made this "
        "worse as often as better. Tell the user, give them the editor link, and let "
        "them move the labels — it takes them seconds and they can see the result. "
        "Recreate the diagram only if its *content* is wrong."
    )
