from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, NamedTuple

from constants import DIRECTIVE_PATTERN
from utils import log

WUBRG = ("white", "blue", "black", "red", "green")
LETTER_TO_COLOR = dict(zip("wubrg", WUBRG))
NAME_TO_COLOR = {**LETTER_TO_COLOR, **{name: name for name in WUBRG}}
PAIR_ORDER = (
    ("white", "blue"), ("blue", "black"), ("black", "red"), ("red", "green"), ("green", "white"),
    ("white", "black"), ("blue", "red"), ("black", "green"), ("red", "white"), ("green", "blue"),
)  # fmt: skip
BASIC_LAND_TYPES = {"plains": "white", "island": "blue", "swamp": "black", "mountain": "red", "forest": "green"}
ANY_COLOR = re.compile(r"any (?:one )?(?:color|type)|any combination of colors|color identity")
MANA_SYMBOL = re.compile(r"\{([^{}]*)\}")
AUTO_TAG = re.compile(r"\{\s*auto\s*(?::\s*([^{}]*?))?\s*\}", re.IGNORECASE)


class Colors(NamedTuple):
    names: tuple[str, ...] = ()
    hybrid: bool = False


NO_COLORS = Colors()


@dataclass(frozen=True)
class Tint:
    slug: str
    halves: tuple[str, str] | None = None

    def side(self, index: int) -> str:
        return self.halves[index] if self.halves else self.slug


def ordered(colors: Iterable[str]) -> tuple[str, ...]:
    colors = set(colors)
    if len(colors) == 2:
        return next(pair for pair in PAIR_ORDER if set(pair) == colors)
    return tuple(sorted(colors, key=WUBRG.index))


def symbol_colors(symbol: str) -> set[str]:
    found = set()
    for part in symbol.strip().lower().split("/"):
        if part in LETTER_TO_COLOR:
            found.add(LETTER_TO_COLOR[part])
        elif len(part) == 2 and "p" in part and part.replace("p", "", 1) in LETTER_TO_COLOR:
            found.add(LETTER_TO_COLOR[part.replace("p", "", 1)])
    return found


def _is_hybrid(symbol: str) -> bool:
    return len([part for part in symbol.lower().split("/") if part and part != "p"]) >= 2


def mana_colors(text: str) -> Colors:
    symbols = re.sub(r"[{}]+", " ", DIRECTIVE_PATTERN.sub("", text or "")).lower().split()
    colors: set[str] = set()
    all_hybrid = True
    for symbol in symbols:
        found = symbol_colors(symbol)
        colors |= found
        all_hybrid &= not found or _is_hybrid(symbol)
    names = ordered(colors)
    return Colors(names, len(names) == 2 and all_hybrid)


def rules_colors(text: str) -> Colors:
    colors: set[str] = set()
    for symbol in re.findall(r"\{([^{}]*)\}", DIRECTIVE_PATTERN.sub("", text or "")):
        colors |= symbol_colors(symbol)
    names = ordered(colors)
    return Colors(names, len(names) == 2)


def land_colors(rules: str, subtypes: Iterable[str]) -> Colors:
    text, subtypes = rules.lower(), set(subtypes)
    colors = {color for name, color in BASIC_LAND_TYPES.items() if name in subtypes or re.search(rf"\b{name}\b", text)}
    for clause in re.findall(r"\badd\b([^.\n]*)", text):
        for symbol in re.findall(r"\{([^{}]*)\}", clause):
            colors |= symbol_colors(symbol)
        if ANY_COLOR.search(clause):
            colors |= set(WUBRG)
    names = ordered(colors)
    return Colors(names, len(names) == 2)


def parse_hint(value: str | None) -> Colors | None:
    if value is None or not value.strip():
        return None
    colors = set()
    for word in re.split(r"[\s,/]+", value.lower()):
        if word in NAME_TO_COLOR:
            colors.add(NAME_TO_COLOR[word])
        elif word and word not in ("c", "colorless", "none"):
            log(f"Unknown color '{word}' in an {{auto}} frame hint.")
    names = ordered(colors)
    return Colors(names, "/" in value and len(names) == 2)


def tint_of(colors: Colors) -> Tint | None:
    if not colors.names:
        return None
    if len(colors.names) == 1:
        return Tint(colors.names[0])
    if len(colors.names) == 2 and colors.hybrid:
        return Tint("multicolor", colors.names)
    return Tint("multicolor")


def stamp_tint(tint: Tint, accent: Tint | None, colors: Colors, devoid: bool) -> Tint:
    """Crowns and holo stamps use the card's own colors; colorless things keep their body tint."""
    if accent is None or devoid:
        return tint
    if len(colors.names) == 2:
        return Tint("multicolor", colors.names)
    return accent
