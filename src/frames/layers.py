from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import assets
import paint
import report
from card import Card, Face, describe
from colors import Tint
from frame_family import USE_ENCHANTMENT_FRAMES, USE_SNOW_FRAMES, FrameFamily

REGULAR_SNOW = "regular/snow"
REGULAR_CROWN_COVER = "regular/legendary_crown/cover"


def snow_root(family: FrameFamily, face: Face) -> str | None:
    return family.snow if USE_SNOW_FRAMES and face.snow else None


def enchantment_root(family: FrameFamily, face: Face) -> str | None:
    return family.enchantment if USE_ENCHANTMENT_FRAMES and face.enchantment else None


def body_roots(family: FrameFamily, face: Face) -> list[str]:
    if face.tint.slug == "colorless" and family.colorless_root:
        return [family.colorless_root]
    return [root for root in (snow_root(family, face), enchantment_root(family, face), family.root) if root]


def land_roots(family: FrameFamily, face: Face) -> list[str]:
    snow = [family.snow_land] if snow_root(family, face) and family.snow_land else []
    return [*snow, *([family.land] if family.land else [])]


def frame_source(family: FrameFamily, face: Face) -> tuple[list[str], Tint]:
    """The folders and exact tint that reproduce `face`'s body frame, for repainting part of a card."""
    if face.land:
        return land_roots(family, face), face.accent or Tint("colorless")
    tint = Tint("artifact") if face.tint.slug == "vehicle" else face.tint
    return body_roots(family, face), tint


def is_plain_dual_color(face: Face) -> bool:
    """Exactly two colors framed as ordinary multicolor (gold): not hybrid, not a land, not Devoid."""
    return (
        len(face.colors) == 2
        and face.tint.slug == "multicolor"
        and face.tint.halves is None
        and not face.land
        and not face.devoid
    )


@dataclass(frozen=True)
class Build:
    card: Card
    family: FrameFamily
    face: Face

    @property
    def extras(self) -> list[str]:
        return self.card.extras

    @property
    def label(self) -> str:
        return self.card.label

    @property
    def rare(self) -> bool:
        return self.card.is_rare

    @property
    def partner(self) -> Face | None:
        return self.card.partner

    @property
    def roots(self) -> list[str]:
        return body_roots(self.family, self.face)

    @property
    def half_mask(self) -> str:
        return self.family.half_mask_dir

    @property
    def shaped_mask(self) -> str:
        return self.family.shaped_mask_dir


@dataclass(frozen=True)
class LayerSpec:
    applies: Callable[[Build], bool]
    draw: Callable[[Build], list[str]]
    missing: str = ""  # if it applies but draws nothing, warn that this is missing


LAYERS: dict[str, LayerSpec] = {}


def layer(name: str, *, applies: Callable[[Build], bool] = lambda build: True, missing: str = ""):
    def register(draw: Callable[[Build], list[str]]):
        LAYERS[name] = LayerSpec(applies, draw, missing)
        return draw

    return register


def _body_artifact_token(b: Build) -> list[str]:
    if not (b.face.artifact and b.face.accent and not b.face.land and b.family.artifact_pinlines):
        return []
    region = assets.find_mask(b.shaped_mask, "pinline")
    base = paint.solid(b.roots, "artifact")
    pinlines = paint.paint_region(b.roots, b.face.accent, b.half_mask, region) if region else []
    return base + pinlines if base and pinlines else []


def _body_land(b: Build) -> list[str]:
    if not b.face.land:
        return []
    roots = land_roots(b.family, b.face)
    if b.face.accent:
        return paint.paint(roots, b.face.accent, b.half_mask)
    colorless = assets.find_slug(roots[:1], ["colorless"])
    return [colorless] if colorless else []


def _body_devoid(b: Build) -> list[str]:
    if not (b.face.devoid and b.family.devoid and b.face.accent):
        return []
    return paint.paint([b.family.devoid], b.face.accent, b.half_mask)


def _body_plain(b: Build) -> list[str]:
    return paint.paint(b.roots, b.face.tint, b.half_mask)


BODY_STRATEGIES = (_body_artifact_token, _body_land, _body_devoid, _body_plain)


def paint_body(b: Build) -> list[str]:
    return next((lines for lines in (strategy(b) for strategy in BODY_STRATEGIES) if lines), [])


def body_is_artifact_frame(b: Build) -> bool:
    return not b.face.land and (b.face.accent is None or b.family.artifact_pinlines)


def enchantment_overlay(b: Build, mask: str) -> list[str]:
    face = b.face
    if not (face.enchantment and enchantment_root(b.family, face)) or face.vehicle:
        return []
    if not (snow_root(b.family, face) or (face.land and not face.artifact)):
        return []
    tint = face.accent if face.land else face.tint
    if tint is None:
        return []
    return paint.paint_region([enchantment_root(b.family, face)], tint, b.half_mask, mask)


def artifact_overlay(b: Build) -> str | None:
    face = b.face
    if not (face.artifact or face.vehicle) or body_is_artifact_frame(b):
        return None
    roots = [root for root in (enchantment_root(b.family, face), snow_root(b.family, face), b.family.root) if root]
    return assets.find_root_first(roots, ["artifact"])


def vehicle_overlay(b: Build) -> str | None:
    if not b.face.vehicle:
        return None
    frame = assets.find_slug([b.family.root], ["vehicle"])
    if frame is None or frame == paint.slug_path(b.roots, b.face.tint.slug):
        return None
    return frame


@layer("frame_overlays")
def frame_overlays(b: Build) -> list[str]:
    mask = assets.find_mask(b.shaped_mask, "frame")
    if not mask or b.face.devoid:
        return []
    vehicle = vehicle_overlay(b)
    artifact = artifact_overlay(b) if vehicle is None else None
    lines = enchantment_overlay(b, mask)
    for frame in (artifact, vehicle):
        if frame:
            lines += [mask, frame]
    return lines


@layer("land_symbol", applies=lambda b: b.face.bare_basic_land and bool(b.family.land_symbols))
def land_symbol(b: Build) -> list[str]:
    slug = b.face.accent.side(0) if b.face.accent else "colorless"
    path = assets.find_slug([b.family.land_symbols], [slug])
    return [path] if path else []


def _pip_applies(b: Build) -> bool:
    return "pip" in b.extras and bool(b.family.pip) and not b.face.land and b.face.accent is not None


@layer("pip", applies=_pip_applies, missing="color identity pip")
def pip(b: Build) -> list[str]:
    base = assets.first([f"{b.family.pip}/base"])
    fill = paint.paint([b.family.pip_fill or b.family.pip], b.face.accent, f"{b.family.pip}/mask")
    return [base, *fill] if base and fill else []


@layer("rules_accent", applies=lambda b: is_plain_dual_color(b.face))
def rules_accent(b: Build) -> list[str]:
    rules = assets.find_mask(b.shaped_mask, "rules")
    return paint.left_overlay(b.roots, b.face.colors, b.half_mask, rules) if rules else []


def _holo_applies(b: Build) -> bool:
    return b.rare and bool(b.family.holo)


def holo_lines(b: Build) -> list[str]:
    return paint.holo_stamp(b.family.holo, b.face.stamp, b.half_mask) if _holo_applies(b) else []


@layer("holo", applies=_holo_applies, missing="holo stamp")
def holo(b: Build) -> list[str]:
    return holo_lines(b)


def _reminder_applies(b: Build) -> bool:
    if not b.family.reminder_mask:
        return False
    own = frame_source(b.family, b.face)
    other = frame_source(b.family, b.partner) if b.partner else own
    return other != own or bool(holo_lines(b))


@layer("modal_reminder", applies=_reminder_applies, missing="modal reminder-area frame")
def modal_reminder(b: Build) -> list[str]:
    region = assets.find_mask(b.shaped_mask, b.family.reminder_mask or "")
    if not region:
        return []
    roots, tint = frame_source(b.family, b.partner or b.face)
    return paint.paint_region(roots, tint, b.half_mask, region)


def pinline_roots(b: Build) -> list[str]:
    return land_roots(b.family, b.face) if b.face.land else b.roots


def _pinline_accent_applies(b: Build) -> bool:
    splits_with_holo = bool(holo_lines(b)) and b.face.accent is not None and b.face.accent.halves is not None
    return is_plain_dual_color(b.face) or splits_with_holo


@layer("pinline_accent", applies=_pinline_accent_applies)
def pinline_accent(b: Build) -> list[str]:
    region = None
    if holo_lines(b):
        region = assets.find_mask(b.shaped_mask, "pinline_holo")
    region = region or assets.find_mask(b.shaped_mask, "pinline")
    return paint.left_overlay(pinline_roots(b), b.face.colors, b.half_mask, region) if region else []


def _crown_frames(b: Build, folder: str) -> list[str]:
    return paint.paint([folder], b.face.stamp, b.half_mask)


def crown_parts(b: Build) -> list[list[str]]:
    """The base crown (Legendary), the Legendary Enchantment extra, then the Companion extra."""
    face, family = b.face, b.family
    parts: list[list[str]] = []
    if face.legendary and family.crown:
        base = _crown_frames(b, family.crown)
        if not base:
            report.warning(f"No legendary crown found in {family.crown}; drawing the frame without one.")
        parts.append(base)
    if face.legendary and face.enchantment and family.enchantment_crown:
        parts.append(_crown_frames(b, family.enchantment_crown))
    if face.companion and family.companion_crown:
        parts.append(_crown_frames(b, family.companion_crown))
    return [part for part in parts if part]


def _crown_applies(b: Build) -> bool:
    face, family = b.face, b.family
    base = face.legendary and family.crown
    enchantment = face.legendary and face.enchantment and family.enchantment_crown
    companion = face.companion and family.companion_crown
    return bool(base or enchantment or companion)


def crown_cover(crown_dir: str) -> str | None:
    """The crown folder's own cover; transform's left/ and right/ folders also look in their parent."""
    candidates = [f"{crown_dir}/cover"]
    parent, _, name = crown_dir.rpartition("/")
    if name in ("left", "right"):
        candidates.append(f"{parent}/cover")
    return assets.first([*candidates, REGULAR_CROWN_COVER])


@layer("crown", applies=_crown_applies)
def crown(b: Build) -> list[str]:
    parts = crown_parts(b)
    if not parts:
        return []
    cover = crown_cover(parts[0][0].rsplit("/", 1)[0])
    return ([cover] if cover else []) + [line for part in parts for line in part]


def plate_slug(family: FrameFamily, face: Face) -> str:
    if family.pt_color:
        return family.pt_color
    if face.vehicle:
        return "vehicle"
    if face.land:
        return face.accent.side(1) if face.accent else "colorless"
    return face.tint.side(1)


@layer(
    "power_toughness",
    applies=lambda b: bool(b.face.power_toughness and b.family.pt),
    missing="power/toughness plate",
)
def power_toughness(b: Build) -> list[str]:
    return paint.solid([b.family.pt], plate_slug(b.family, b.face))


@layer("arrow", applies=lambda b: bool(b.family.arrow), missing="transform arrow")
def arrow(b: Build) -> list[str]:
    path = assets.first([b.family.arrow or ""])
    return [path] if path else []


def compose(b: Build) -> list[str]:
    body = paint_body(b)
    if not body:
        folders = [*(land_roots(b.family, b.face) if b.face.land else []), *b.roots]
        report.error(
            f"{b.label} could NOT be auto-filled: no '{b.family.root}' frame exists for "
            f"'{describe(b.face)}' (looked in: {', '.join(folders)}). Frame(s) left blank."
        )
        return []
    lines = list(body)
    for name in b.family.layers:
        spec = LAYERS[name]
        if not spec.applies(b):
            continue
        drawn = spec.draw(b)
        if not drawn and spec.missing:
            report.warning(
                f"{b.label} is missing its {spec.missing}: none exists in '{b.family.root}' for '{describe(b.face)}'."
            )
        lines += drawn
    return lines
