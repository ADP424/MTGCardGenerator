from __future__ import annotations

from typing import Iterable

import assets
from colors import Tint

SLUG_FALLBACKS = {
    "colorless": ("colorless", "artifact"),
    "artifact": ("artifact", "colorless"),
    "vehicle": ("vehicle", "artifact", "colorless"),
}
ROOT_FIRST_SLUGS = {"vehicle"}


def slug_path(roots: Iterable[str], slug: str) -> str | None:
    roots = list(roots)
    slugs = SLUG_FALLBACKS.get(slug, (slug,))
    if slug in ROOT_FIRST_SLUGS:
        return assets.find_root_first(roots, slugs)
    return assets.find_slug(roots, slugs)


def solid(roots: Iterable[str], slug: str) -> list[str]:
    path = slug_path(roots, slug)
    return [path] if path else []


def masked(roots: Iterable[str], slug: str, mask_dir: str, mask_name: str) -> list[str]:
    frame, mask = slug_path(roots, slug), assets.find_mask(mask_dir, mask_name)
    return [mask, frame] if frame and mask else []


def left_overlay(roots: Iterable[str], halves: tuple[str, str], mask_dir: str, region: str | None = None) -> list[str]:
    left, right = halves
    base, overlay = slug_path(roots, right), slug_path(roots, left)
    left_mask = assets.find_mask(mask_dir, "left")
    if not (base and overlay and left_mask):
        return []
    limit = [region] if region else []
    return [*limit, base, left_mask, *limit, overlay]


def paint(roots: Iterable[str], tint: Tint, mask_dir: str) -> list[str]:
    if tint.halves:
        layered = left_overlay(roots, tint.halves, mask_dir)
        if layered:
            return layered
        tint = Tint("multicolor")
    return solid(roots, tint.slug)


def paint_region(roots: Iterable[str], tint: Tint, mask_dir: str, region: str) -> list[str]:
    """Exact slugs only: a colorless non-artifact card never picks up an artifact frame here."""
    if tint.halves:
        layered = left_overlay(roots, tint.halves, mask_dir, region)
        if layered:
            return layered
        tint = Tint("multicolor")
    frame = assets.find_slug(roots, [tint.slug])
    return [region, frame] if frame else []


def paint_half(roots: Iterable[str], tint: Tint, mask_dir: str, side: str) -> list[str]:
    if tint.halves:
        left, right = tint.halves
        pair = masked(roots, left, mask_dir, f"{side}_left") + masked(roots, right, mask_dir, f"{side}_right")
        if len(pair) == 4:
            return pair
        tint = Tint("multicolor")
    return masked(roots, tint.slug, mask_dir, side)


def holo_stamp(folder: str, tint: Tint, mask_dir: str) -> list[str]:
    per_color = paint([folder], tint, mask_dir)
    if per_color:
        return per_color
    flat = assets.first([folder])
    return [flat] if flat else []
