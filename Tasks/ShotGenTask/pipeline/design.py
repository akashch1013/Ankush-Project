"""Design tokens, font registration and text measurement.

All typography decisions come from design/tokens.json (measured from the
approved Opening V04 sample). Text is measured with the same TTF files that are
embedded in the PDF, so a fit test is a real fit test.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .paths import DESIGN, FONTS

REQUIRED_GLYPHS = "−×÷→—–‘’“”…°√∛²³ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,;:!?()[]-+=<>/'\""


@lru_cache(maxsize=1)
def tokens() -> dict:
    return json.loads((DESIGN / "tokens.json").read_text(encoding="utf-8"))


def theme(name: str) -> dict:
    themes = tokens()["themes"]
    if name not in themes:
        raise SystemExit(f"Unknown theme '{name}'. Known: {', '.join(k for k in themes if not k.startswith('_'))}")
    return themes[name]


def hex_rgb(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))


_registered = False


def register_fonts() -> None:
    """Register the four Source fonts with ReportLab (embedded as subsets on output)."""
    global _registered
    if _registered:
        return
    for name, filename in tokens()["fonts"].items():
        path = FONTS / filename
        if not path.exists():
            raise SystemExit(f"Missing font file {path}. See fonts/README.md.")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    _registered = True


def missing_glyphs(font_name: str, text: str) -> list[str]:
    """Characters in `text` that the font cannot draw (would render as boxes)."""
    register_fonts()
    face = pdfmetrics.getFont(font_name).face
    cmap = face.charToGlyph
    return sorted({ch for ch in text if not ch.isspace() and ord(ch) not in cmap})


def width(text: str, font: str, size: float) -> float:
    register_fonts()
    return pdfmetrics.stringWidth(text, font, size)


class TextTooWide(Exception):
    pass


def wrap_greedy(text: str, font: str, size: float, max_width: float) -> list[str]:
    """Break text into lines no wider than max_width. Never hyphenates or squeezes.
    Breaks only at ordinary spaces, so no-break spaces in the source stay intact."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = [w for w in re.split(r"[ \t]+", paragraph) if w]
        current = ""
        for word in words:
            if width(word, font, size) > max_width + 0.01:
                raise TextTooWide(f"Word '{word}' is wider than {max_width:.1f} pt at {size} pt")
            trial = word if not current else f"{current} {word}"
            if width(trial, font, size) <= max_width + 0.01:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def wrap_balanced(text: str, font: str, size: float, max_width: float, min_width: float = 60.0) -> list[str]:
    """Wrap into the fewest lines possible at max_width, then narrow the measure
    until the line count would grow. Produces the even, centred line shapes seen
    in the sample balloons."""
    best = wrap_greedy(text, font, size, max_width)
    target = len(best)
    lo, hi = min_width, max_width
    for _ in range(24):
        mid = (lo + hi) / 2
        try:
            trial = wrap_greedy(text, font, size, mid)
        except TextTooWide:
            lo = mid
            continue
        if len(trial) <= target:
            best, hi = trial, mid
        else:
            lo = mid
    return best


def widest(lines: list[str], font: str, size: float) -> float:
    return max((width(line, font, size) for line in lines), default=0.0)
