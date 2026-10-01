from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping

import report
from colors import (
    NO_COLORS,
    Colors,
    Tint,
    land_colors,
    mana_colors,
    rules_colors,
    stamp_tint,
    tint_of,
)
from rows import card_key, frontside_of, hint_of, layout_of, row_by_key

from constants import (
    CARD_FRAME_LAYOUT_EXTRAS,
    CARD_MANA_COST,
    CARD_POWER_TOUGHNESS,
    CARD_RARITY,
    CARD_RULES_TEXT,
    CARD_SUBTYPES,
    CARD_SUPERTYPES,
    CARD_TITLE,
    CARD_TYPES,
    DIRECTIVE_PATTERN,
)

if TYPE_CHECKING:
    from layouts import Layout

COMPANION = re.compile(r"\bcompanion\s*(?:\{-\}|[—–-])", re.IGNORECASE)
RARE_RARITIES = {"rare", "mythic"}


@dataclass(frozen=True)
class Card:
    metadata: dict
    layout_name: str
    layout: Layout
    extras: list[str]
    hint: Colors | None  # from an {auto: ...} tag
    lookup: dict  # card key -> row, for finding the other side
    partner: Face | None = None  # the other side of a modal, if any

    @property
    def title(self) -> str:
        return str(self.metadata.get(CARD_TITLE, "") or "")

    @property
    def label(self) -> str:
        return f"'{self.title}' ({self.layout_name})"

    @property
    def is_rare(self) -> bool:
        rarity = DIRECTIVE_PATTERN.sub("", str(self.metadata.get(CARD_RARITY, "") or ""))
        return bool(RARE_RARITIES & _words(rarity))


@dataclass(frozen=True)
class Text:
    types: frozenset[str]
    supertypes: frozenset[str]
    subtypes: frozenset[str]
    cost: str
    rules: str
    power_toughness: str


@dataclass(frozen=True)
class Face:
    tint: Tint  # what the body is painted as
    accent: Tint | None  # the card's actual colors (cost, or produced mana for a land), if any
    stamp: Tint  # what crowns and holo stamps are painted as
    colors: tuple[str, ...]
    land: bool
    bare_basic_land: bool
    artifact: bool
    vehicle: bool
    snow: bool
    enchantment: bool
    legendary: bool
    companion: bool
    devoid: bool
    power_toughness: str


def describe(face: Face) -> str:
    flags = [
        name
        for name, present in (
            ("land", face.land),
            ("artifact", face.artifact),
            ("vehicle", face.vehicle),
            ("enchantment", face.enchantment),
            ("snow", face.snow),
        )
        if present
    ]
    return " ".join(["/".join(face.colors) or "colorless", *flags])


def _words(text: str) -> frozenset[str]:
    return frozenset(re.findall(r"[a-z]+", text.lower()))


def _line(text: str, index: int, fallback: bool = False) -> str:
    lines = text.split("\n")
    if index < len(lines):
        return lines[index]
    return lines[0] if fallback else ""


def partner_row(card: Card) -> dict | None:
    """The other side's row: a backside's front (named by its Transform Frontside), or the backside
    whose Transform Frontside names this card."""
    if card.layout.names_front:
        key = frontside_of(card.metadata)
        return row_by_key(card.lookup, key) if key else None
    if card.layout.partner_layout:
        own_key = card_key(card.metadata)
        return next(
            (
                row
                for row in card.lookup.values()
                if layout_of(row) == card.layout.partner_layout and frontside_of(row) == own_key
            ),
            None,
        )
    return None


def read_partner(card: Card, layouts: Mapping[str, Layout]) -> Face | None:
    name = card.layout.partner_layout
    if name is None:
        return None
    row = partner_row(card)
    if row is None:
        report.warning(f"Could not find the other side of {card.label}; its reminder area won't be matched.")
        return None
    partner = Card(
        row,
        name,
        layouts[name],
        list(row.get(CARD_FRAME_LAYOUT_EXTRAS) or []),
        hint_of(row),
        card.lookup,
    )
    return read_face(partner, 0)


def read_text(card: Card, index: int) -> Text:
    cells = {
        key: str(card.metadata.get(key, "") or "")
        for key in (CARD_TYPES, CARD_SUPERTYPES, CARD_SUBTYPES, CARD_MANA_COST, CARD_RULES_TEXT, CARD_POWER_TOUGHNESS)
    }
    layout = card.layout

    def face_cell(key: str) -> str:
        return _line(cells[key], index, fallback=True) if layout.two_face else cells[key]

    if layout.two_face:
        cost = _line(cells[CARD_MANA_COST], index)
    elif layout.first_line_cost:
        cost = _line(cells[CARD_MANA_COST], 0)
    else:
        cost = cells[CARD_MANA_COST]
    pt = "" if index > 0 else DIRECTIVE_PATTERN.sub("", _line(cells[CARD_POWER_TOUGHNESS], 0)).strip()
    return Text(
        types=_words(face_cell(CARD_TYPES)),
        supertypes=_words(face_cell(CARD_SUPERTYPES)),
        subtypes=_words(face_cell(CARD_SUBTYPES)),
        cost=cost,
        rules=cells[CARD_RULES_TEXT],
        power_toughness="" if "{skip}" in pt else pt,
    )


def _hint_colors(card: Card, text: Text) -> Colors | None:
    return card.hint


def _rules_colors(card: Card, text: Text) -> Colors | None:
    return rules_colors(text.rules) if card.layout.colors_from_rules else None


def _land_colors(card: Card, text: Text) -> Colors | None:
    return land_colors(text.rules, text.subtypes) if "land" in text.types else None


def _cost_colors(card: Card, text: Text) -> Colors | None:
    colors = mana_colors(text.cost)
    return colors if colors.names else None


def _indicator_colors(card: Card, text: Text) -> Colors | None:
    """A cost-less back with the `pip` extra has a color indicator we can't read, so it takes its front's colors."""
    if not (card.layout.names_front and "pip" in card.extras and not text.cost.strip()):
        return None
    front = partner_row(card)
    if front is None:
        return None
    hint = hint_of(front)
    return hint if hint is not None else mana_colors(str(front.get(CARD_MANA_COST, "") or ""))


COLOR_SOURCES = (_hint_colors, _rules_colors, _land_colors, _cost_colors, _indicator_colors)


def resolve_colors(card: Card, text: Text) -> Colors:
    for source in COLOR_SOURCES:
        found = source(card, text)
        if found is not None:
            return found
    return NO_COLORS


def has_companion(card: Card, text: Text) -> bool:
    if COMPANION.search(text.rules):
        return True
    front = partner_row(card) if card.layout.names_front else None
    return front is not None and bool(COMPANION.search(str(front.get(CARD_RULES_TEXT, "") or "")))


def _face_from(text: Text, colors: Colors, companion: bool) -> Face:
    land = "land" in text.types
    artifact = "artifact" in text.types
    vehicle = "vehicle" in text.subtypes or "vehicle" in text.types
    devoid = bool(colors.names) and not land and bool(re.search(r"(?im)^\s*devoid\b", text.rules))
    accent = tint_of(colors)
    if land:
        tint = Tint("land")
    elif accent and not devoid:
        tint = accent
    elif vehicle:
        tint = Tint("vehicle")
    elif artifact:
        tint = Tint("artifact")
    else:
        tint = Tint("colorless")
    return Face(
        tint=tint,
        accent=accent,
        stamp=stamp_tint(tint, accent, colors, devoid),
        colors=colors.names,
        land=land,
        bare_basic_land=land and "basic" in text.supertypes and not text.rules.strip(),
        artifact=artifact,
        vehicle=vehicle,
        snow="snow" in text.supertypes,
        enchantment="enchantment" in text.types,
        legendary="legendary" in text.supertypes,
        companion=companion,
        devoid=devoid,
        power_toughness=text.power_toughness,
    )


def read_face(card: Card, index: int) -> Face:
    text = read_text(card, index)
    return _face_from(text, resolve_colors(card, text), has_companion(card, text))
