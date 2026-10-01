from __future__ import annotations

from dataclasses import replace

import paint
import report
from card import Card, Face, describe, read_face
from colors import Colors, Tint, ordered, tint_of
from layers import Build, body_roots, compose


def warn_if_no_color_source(card: Card, face: Face) -> None:
    if card.layout.needs_color_hint and card.hint is None and face.accent is None and not face.artifact:
        report.warning(
            f"{card.label} has no color source; using colorless. Put e.g. {{auto: white}} in its Frame(s) cell."
        )


def build_standard(card: Card) -> list[str]:
    face = read_face(card, 0)
    warn_if_no_color_source(card, face)
    return compose(Build(card, card.layout.family, face))


def _adventure_book(card: Card, body: Face) -> list[str]:
    spell = read_face(card, 1)
    if spell.accent is None or spell.tint == body.tint:
        return []
    return paint.masked(
        body_roots(card.layout.family, spell), spell.tint.slug, card.layout.family.shaped_mask_dir, "book_left"
    )


def build_adventure(card: Card) -> list[str]:
    lines = build_standard(card)
    return lines + _adventure_book(card, read_face(card, 0)) if lines else []


def build_halves(card: Card) -> list[str]:
    family = card.layout.family
    faces = [read_face(card, index) for index in (0, 1)]
    lines: list[str] = []
    for side, face in zip(("left", "right"), faces):
        painted = paint.paint_half(body_roots(family, face), face.tint, family.half_mask_dir, side)
        if not painted:
            report.error(
                f"{card.label} could NOT be auto-filled: no '{family.root}' {side}-half frame exists for "
                f"'{describe(face)}'."
            )
            return []
        lines += painted
    if card.is_rare and family.holo:
        lines += paint.holo_stamp(family.holo, faces[0].stamp, family.half_mask_dir)
    return lines


def build_fuse(card: Card) -> list[str]:
    lines = build_halves(card)
    if not lines:
        return []
    union = Colors(ordered(color for index in (0, 1) for color in read_face(card, index).colors))
    bar = tint_of(union) or Tint("colorless")
    return lines + paint.solid(["split/fuse"], bar.slug)


def _room_tint(left: Face, right: Face) -> Tint:
    slugs = (left.tint.slug, right.tint.slug)
    if "multicolor" in slugs:
        return Tint("multicolor")
    if slugs[0] == slugs[1]:
        return Tint(slugs[0])
    return Tint("multicolor", slugs)


def build_room(card: Card) -> list[str]:
    family = card.layout.family
    left, right = read_face(card, 0), read_face(card, 1)
    merged = replace(left, snow=left.snow or right.snow, enchantment=left.enchantment or right.enchantment)
    lines = paint.paint(body_roots(family, merged), _room_tint(left, right), family.half_mask_dir)
    if not lines:
        report.error(
            f"{card.label} could NOT be auto-filled: no '{family.root}' frame exists for "
            f"'{describe(left)}' + '{describe(right)}'."
        )
        return []
    if card.is_rare and family.holo:
        lines += paint.holo_stamp(family.holo, left.stamp, family.half_mask_dir)
    return lines
