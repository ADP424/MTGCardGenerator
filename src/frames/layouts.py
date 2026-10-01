from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from builders import (
    build_adventure,
    build_fuse,
    build_halves,
    build_room,
    build_standard,
)
from card import Card
from families import (
    ADVENTURE,
    BATTLE,
    BATTLE_TRANSFORM,
    CLASS,
    CONSPIRACY,
    EDIFICE,
    MELD_BOTTOM,
    MELD_MIDDLE,
    MELD_TOP,
    MODAL_BACK,
    MODAL_FRONT,
    OMEN,
    PLANESWALKER,
    PREPARE,
    REGULAR,
    ROOM,
    SAGA,
    SHORT_MODAL_BACK,
    SHORT_MODAL_FRONT,
    SPLIT,
    TRANSFORM_BACK,
    TRANSFORM_FRONT,
    TRANSFORM_SAGA,
    token,
)
from frame_family import FrameFamily


@dataclass(frozen=True)
class Layout:
    family: FrameFamily
    builder: Callable[[Card], list[str]] = build_standard
    two_face: bool = False  # Mana Cost / Type cells have one line per face
    first_line_cost: bool = False  # Mana Cost's first line is the card's cost; later lines are ability costs
    colors_from_rules: bool = False  # colors come only from mana symbols in the rules text (conspiracies)
    needs_color_hint: bool = False  # no mana cost to read: requires an {auto: ...} hint for its colors
    names_front: bool = False  # the Transform Frontside cell names this card's front
    partner_layout: str | None = None  # layout of the other side, found by a backside naming this card


MELD = {"top": MELD_TOP, "middle": MELD_MIDDLE, "bottom": MELD_BOTTOM}
LAYOUTS: dict[str, Layout] = {
    "regular": Layout(REGULAR),
    "regular split rules text": Layout(REGULAR),
    "edifice": Layout(EDIFICE),
    "transform frontside": Layout(TRANSFORM_FRONT),
    "transform backside": Layout(TRANSFORM_BACK, names_front=True),
    "battle": Layout(BATTLE),
    "transform battle": Layout(BATTLE_TRANSFORM),
    "planeswalker": Layout(PLANESWALKER, first_line_cost=True),
    "saga": Layout(SAGA),
    "transform saga": Layout(TRANSFORM_SAGA),
    "class": Layout(CLASS, first_line_cost=True),
    "adventure": Layout(ADVENTURE, builder=build_adventure, two_face=True),
    "omen": Layout(OMEN, two_face=True),
    "prepare": Layout(PREPARE, two_face=True),
    "conspiracy": Layout(CONSPIRACY, colors_from_rules=True),
    "room": Layout(ROOM, builder=build_room, two_face=True),
    "split": Layout(SPLIT, builder=build_halves, two_face=True),
    "fuse": Layout(SPLIT, builder=build_fuse, two_face=True),
    "token": Layout(token("regular"), needs_color_hint=True),
    "short token": Layout(token("short"), needs_color_hint=True),
    "tall token": Layout(token("tall"), needs_color_hint=True),
    "textless token": Layout(token("textless"), needs_color_hint=True),
    **{f"meld backside {section}": Layout(family, needs_color_hint=True) for section, family in MELD.items()},
    "modal frontside": Layout(MODAL_FRONT, partner_layout="modal backside"),
    "modal backside": Layout(MODAL_BACK, names_front=True, partner_layout="modal frontside"),
    "short modal frontside": Layout(SHORT_MODAL_FRONT, partner_layout="short modal backside"),
    "short modal backside": Layout(SHORT_MODAL_BACK, names_front=True, partner_layout="short modal frontside"),
}
