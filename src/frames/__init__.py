"""
Automatic completion of the Frame(s) column. See frames/README in the design notes.

This is an experimental feature designed heavily using Claude Code.
It's opt-in: The previous system involved manually inserting frame paths, and doing that
will override any frame defaults.
"""

from __future__ import annotations

import os
import sys
from dataclasses import replace

# This package's modules import each other with bare names (from colors import ..., not from .colors
# import ...), matching the rest of the codebase's convention of bare imports off of src/. That only
# works once this directory is itself on sys.path, which running `python main.py` from src/ doesn't do
# for a subpackage, so it's added here before anything else in the package is imported.
_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
if _PACKAGE_DIR not in sys.path:
    sys.path.insert(0, _PACKAGE_DIR)

import report
from card import Card, read_partner
from colors import AUTO_TAG, parse_hint
from layouts import LAYOUTS
from rows import HINT_KEY, layout_of

from constants import (
    CARD_CATEGORY,
    CARD_FRAME_LAYOUT_EXTRAS,
    CARD_FRAMES,
    CARD_TITLE,
)

_warned_layouts: set[str] = set()


def fill_frames(metadata: dict, card_lookup: dict | None = None) -> bool:
    """
    Fill `metadata[CARD_FRAMES]` in place if it's empty. Must run after the frame layout has been
    normalized and its extras parsed, and before the card object is constructed.
    Returns True if frames were generated.
    """
    cell = str(metadata.get(CARD_FRAMES, "") or "")
    tag = AUTO_TAG.search(cell)
    if tag:
        metadata[HINT_KEY] = tag.group(1) or ""
    remainder = AUTO_TAG.sub("", cell).strip()
    if remainder == "{skip}":
        metadata[CARD_FRAMES] = ""
        return False
    if remainder:
        if tag:
            metadata[CARD_FRAMES] = remainder
        return False
    if not metadata.get(CARD_TITLE) or "{skip}" in str(metadata.get(CARD_CATEGORY, "") or ""):
        return False
    layout_name = layout_of(metadata)
    layout = LAYOUTS.get(layout_name)
    if layout is None:
        if layout_name not in _warned_layouts:
            _warned_layouts.add(layout_name)
            report.warning(f"Frame auto-selection doesn't support the '{layout_name}' layout. Leaving Frame(s) blank.")
        return False
    extras = metadata.setdefault(CARD_FRAME_LAYOUT_EXTRAS, [])
    card = Card(metadata, layout_name, layout, extras, parse_hint(tag.group(1)) if tag else None, card_lookup or {})
    card = replace(card, partner=read_partner(card, LAYOUTS))
    try:
        frames = layout.builder(card)
    except Exception as error:  # one bad card must never abort the batch
        report.error(f"{card.label} auto-fill crashed: {error}. Frame(s) left blank.")
        return False
    if not frames:
        report.error(f"{card.label} could NOT be auto-filled: no frames exist for this color/layout combination.")
        return False
    # A Vehicle P/T plate is dark, so its P/T text must be white.
    if any("power_toughness/vehicle" in line for line in frames) and "vehicle" not in extras:
        extras.append("vehicle")
    metadata[CARD_FRAMES] = "\n".join(frames)
    return True
