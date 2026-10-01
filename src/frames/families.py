from __future__ import annotations

from dataclasses import replace

from frame_family import FrameFamily

CROWN = "regular/legendary_crown"
REGULAR_CROWNS = {
    "crown": CROWN,
    "enchantment_crown": f"{CROWN}/enchantment",
    "companion_crown": f"{CROWN}/companion",
}
REGULAR_SOURCES = {"pt": "regular/power_toughness", "holo": "regular/holo", **REGULAR_CROWNS}


def with_sources(**overrides: str | None) -> dict[str, str | None]:
    return {**REGULAR_SOURCES, **overrides}


TRANSFORM = "regular/transform"
TRANSFORM_BACK_PT = f"{TRANSFORM}/back/power_toughness"
TRANSFORM_LEFT_CROWN = f"{TRANSFORM}/legendary_crown/left"
TRANSFORM_RIGHT_CROWN = f"{TRANSFORM}/legendary_crown/right"
MODAL_CROWN = "modal/legendary_crown"

REGULAR = FrameFamily(
    "regular",
    snow="regular/snow",
    enchantment="regular/enchantment",
    devoid="regular/devoid",
    land="regular/land",
    snow_land="regular/snow/land",
    land_symbols="regular/land/symbol",
    pip="regular/color_identity_pip",
    **REGULAR_SOURCES,
)
EDIFICE = replace(REGULAR, pt_color="white")
TRANSFORM_FRONT = FrameFamily(
    f"{TRANSFORM}/front",
    snow=f"{TRANSFORM}/front/snow",
    enchantment=f"{TRANSFORM}/front/enchantment",
    land=REGULAR.land,
    snow_land=REGULAR.snow_land,
    pip=REGULAR.pip,
    arrow=f"{TRANSFORM}/up_arrow_left",
    **with_sources(crown=TRANSFORM_LEFT_CROWN),
)
TRANSFORM_BACK = FrameFamily(
    f"{TRANSFORM}/back",
    snow=f"{TRANSFORM}/back/snow",
    enchantment=f"{TRANSFORM}/back/enchantment",
    land=REGULAR.land,
    snow_land=REGULAR.snow_land,
    pip=REGULAR.pip,
    arrow=f"{TRANSFORM}/down_arrow_right",
    **with_sources(pt=TRANSFORM_BACK_PT, crown=TRANSFORM_RIGHT_CROWN, holo=None),
)
BATTLE = FrameFamily("battle", holo="battle/holo", pip="battle/color_identity_pip", horizontal=True)
BATTLE_TRANSFORM = FrameFamily("battle/transform", holo="battle/transform/holo", horizontal=True)
PLANESWALKER = FrameFamily("planeswalker", holo="planeswalker/holo")
SAGA_PIP = "saga/color_identity_pip"
SAGA = FrameFamily(
    "saga",
    enchantment="saga/enchantment",
    holo="saga/holo",
    pip=SAGA_PIP,
    pip_fill=f"{SAGA_PIP}/regular",
    **REGULAR_CROWNS,
)
TRANSFORM_SAGA = FrameFamily(
    "saga/transform/front",
    enchantment="saga/transform/front/enchantment",
    holo="saga/transform/holo",
    pip=SAGA.pip,
    pip_fill=SAGA.pip_fill,
    arrow="saga/transform/up_arrow_left",
    masks="saga/mask",
    **(REGULAR_CROWNS | {"crown": TRANSFORM_LEFT_CROWN}),
)
CLASS = FrameFamily(
    "class",
    enchantment="class/enchantment",
    holo="class/holo",
    pip="class/color_identity_pip",
    **REGULAR_CROWNS,
)
ADVENTURE = FrameFamily("adventure", enchantment="adventure/enchantment", **REGULAR_SOURCES)
OMEN = FrameFamily("omen", enchantment="omen/enchantment", **REGULAR_SOURCES)
PREPARE = FrameFamily("prepare", enchantment="prepare/enchantment", **with_sources(holo="prepare/holo"))
CONSPIRACY = FrameFamily("conspiracy")
ROOM = FrameFamily("room", snow="room/snow", enchantment="room/enchantment", holo="room/holo", horizontal=True)
SPLIT = FrameFamily("split", horizontal=True)

TOKEN_PT = "token/power_toughness"


def token(folder: str) -> FrameFamily:
    return FrameFamily(
        f"token/{folder}",
        pt=TOKEN_PT,
        crown=f"{CROWN}/floating",
        artifact_pinlines=True,
    )


MELD_ROOT = f"{TRANSFORM}/back/meld"


def meld(section: str, **sources: str) -> FrameFamily:
    return FrameFamily(f"{MELD_ROOT}/{section}", horizontal=True, masks=f"{MELD_ROOT}/mask", **sources)


MELD_TOP = meld(
    "top",
    crown=f"{MELD_ROOT}/top/legendary_crown",
    enchantment_crown=f"{MELD_ROOT}/top/legendary_crown/enchantment",
    companion_crown=f"{MELD_ROOT}/top/legendary_crown/companion",
)
MELD_MIDDLE = meld("middle")
MELD_BOTTOM = meld(
    "bottom",
    pt=f"{MELD_ROOT}/bottom/power_toughness",
    pip=f"{MELD_ROOT}/bottom/color_identity_pip",
)
MODAL_FRONT = FrameFamily(
    "modal/front",
    colorless_root="modal/simple/front",
    snow="modal/front/snow",
    enchantment="modal/front/enchantment",
    land="modal/front/land",
    snow_land="modal/front/snow/land",
    pip=REGULAR.pip,
    masks="modal/mask",
    reminder_mask="reminder",
    **with_sources(crown=MODAL_CROWN),
)
MODAL_BACK = FrameFamily(
    "modal/back",
    colorless_root="modal/simple/back",
    snow="modal/back/snow",
    enchantment="modal/back/enchantment",
    land="modal/back/land",
    snow_land="modal/back/snow/land",
    pip=REGULAR.pip,
    masks="modal/mask",
    reminder_mask="reminder",
    **with_sources(crown=MODAL_CROWN, pt=TRANSFORM_BACK_PT),
)
SHORT_MODAL_FRONT = FrameFamily(
    "modal/short/front",
    pip=REGULAR.pip,
    masks="modal/short/mask",
    reminder_mask="reminder",
    **with_sources(crown=MODAL_CROWN),
)
SHORT_MODAL_BACK = FrameFamily(
    "modal/short/back",
    pip=REGULAR.pip,
    masks="modal/short/mask",
    reminder_mask="reminder",
    **with_sources(crown=MODAL_CROWN, pt=TRANSFORM_BACK_PT),
)
