from __future__ import annotations

from dataclasses import dataclass

USE_SNOW_FRAMES = True
USE_ENCHANTMENT_FRAMES = True
REGULAR_MASK = "regular/mask"
STANDARD_LAYERS = (
    "frame_overlays",
    "land_symbol",
    "pip",
    "rules_accent",
    "holo",
    "modal_reminder",
    "pinline_accent",
    "crown",
    "power_toughness",
)
TRANSFORM_LAYERS = (
    "frame_overlays",
    "land_symbol",
    "rules_accent",
    "holo",
    "modal_reminder",
    "pinline_accent",
    "crown",
    "power_toughness",
    "arrow",
    "pip",
)


@dataclass(frozen=True)
class FrameFamily:
    """
    One set of frame images. Each field that names a folder names exactly one; nothing is searched
    for elsewhere. A field left as None means the family has no such image.
    """

    root: str
    pt: str | None = None
    crown: str | None = None
    enchantment_crown: str | None = None
    companion_crown: str | None = None
    holo: str | None = None  # per-color folder, or one flat image
    snow: str | None = None
    enchantment: str | None = None
    devoid: str | None = None
    land: str | None = None
    snow_land: str | None = None
    land_symbols: str | None = None
    pip: str | None = None
    pip_fill: str | None = None
    arrow: str | None = None
    colorless_root: str | None = None
    reminder_mask: str | None = None
    artifact_pinlines: bool = False
    horizontal: bool = False
    masks: str | None = None
    pt_color: str | None = None
    order: tuple[str, ...] | None = None

    @property
    def layers(self) -> tuple[str, ...]:
        return self.order or (TRANSFORM_LAYERS if self.arrow else STANDARD_LAYERS)

    @property
    def shaped_mask_dir(self) -> str:
        return self.masks or f"{self.root}/mask"

    @property
    def half_mask_dir(self) -> str:
        return self.shaped_mask_dir if self.horizontal else REGULAR_MASK
