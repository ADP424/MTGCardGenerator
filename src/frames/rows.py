from __future__ import annotations

import re

from colors import AUTO_TAG, Colors, parse_hint

from constants import (
    CARD_ADDITIONAL_TITLES,
    CARD_DESCRIPTOR,
    CARD_FRAME_LAYOUT,
    CARD_FRAMES,
    CARD_FRONTSIDE,
    CARD_TITLE,
    FRAME_LAYOUT_EXTRAS_LIST,
)
from utils import get_card_key

HINT_KEY = "Auto Frame Hint"


def strip_layout_extras(layout: str) -> str:
    """Remove extras tokens (pip, white, light, rotate45, ...) the same way main.py does, so a raw,
    not-yet-normalized Frame Layout cell compares the same as one that already went through it."""
    for pattern in FRAME_LAYOUT_EXTRAS_LIST:
        for extra in re.findall(pattern, layout):
            layout = layout.replace(extra, "")
    return layout.strip()


def layout_of(row: dict) -> str:
    """A row's true layout name, with any extras tokens stripped. Safe to call whether or not the row's
    own Frame Layout cell has already been normalized by main.py."""
    return strip_layout_extras(str(row.get(CARD_FRAME_LAYOUT, "") or "").strip().lower())


def frontside_of(row: dict) -> str:
    return str(row.get(CARD_FRONTSIDE, "") or "").strip()


def card_key(row: dict) -> str:
    return get_card_key(row.get(CARD_TITLE, ""), row.get(CARD_ADDITIONAL_TITLES, ""), row.get(CARD_DESCRIPTOR, ""))


def row_by_key(lookup: dict, key: str) -> dict | None:
    return next((row for row in lookup.values() if card_key(row) == key), None)


def hint_of(row: dict) -> Colors | None:
    if HINT_KEY in row:
        return parse_hint(row[HINT_KEY])
    tag = AUTO_TAG.search(str(row.get(CARD_FRAMES, "") or ""))
    return parse_hint(tag.group(1)) if tag else None
