"""
Script for turning outline images into "effect" images for the Dungeon walls.
Generally, the outlines should be the same width as the shape files (10px) and be
offset outward from those shapes by 3px.

For an open shape (not a closed loop) that connects to a neighboring tile through one
or more of its canvas edges, pass ``--outer-sides`` with a comma-separated subset of
top,bottom,left,right naming which sides are true exterior (get shadow+bevel). Any side
not listed is treated as the shape's own connecting gap and gets no shadow/bevel, e.g.
``--outer-sides=bottom,left`` for an L-corner piece connecting to neighbors above and to
the right. Omit entirely for a closed shape (border flood fill), like the original
outer.png.
"""

import argparse

import numpy as np
from PIL import Image, ImageFilter

REFERENCE_SIZE = 1500
OUTER_SHADOW_BLUR = 9.0
OUTER_SHADOW_MAX_ALPHA = 84
CORE_WIDTH = 3
CORE_ALPHA = 254
BEVEL_WIDTH = 10.0
BEVEL_FADE_DISTANCE = 4.5

BEVEL_MAX_ALPHA = 84
LIGHT_AZIMUTH_DEGREES = 60.0
LIGHT_ELEVATION_DEGREES = 45.0


def _scale(value, size):
    return value * (size / REFERENCE_SIZE)


def _distance_transform(mask, background=None, max_steps=None):
    """
    Approximate distance from background.

    ``background`` restricts which side counts as "outside" for the erosion.
    """

    if max_steps is None:
        max_steps = int(np.ceil(BEVEL_WIDTH)) + 2

    remaining = mask.astype(bool)
    if background is not None:
        remaining = remaining | ~background

    dist = np.zeros(mask.shape, dtype=np.float32)
    step = 0
    while remaining.any() and step < max_steps:
        step += 1
        shifted = np.ones_like(remaining)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            s = np.roll(remaining, (dy, dx), axis=(0, 1))
            if dy == 1:
                s[0, :] = remaining[0, :]
            elif dy == -1:
                s[-1, :] = remaining[-1, :]
            if dx == 1:
                s[:, 0] = remaining[:, 0]
            elif dx == -1:
                s[:, -1] = remaining[:, -1]
            shifted &= s
        newly_eroded = remaining & ~shifted
        dist[newly_eroded & mask] = step
        remaining = shifted
    dist[remaining & mask] = max_steps

    return dist


def _flood_fill_from_border(free):
    """
    Connected component of ``free`` reachable from the image border (4-connected).
    """

    reached = np.zeros_like(free)
    frontier = np.zeros_like(free)
    frontier[0, :] = free[0, :]
    frontier[-1, :] = free[-1, :]
    frontier[:, 0] = free[:, 0]
    frontier[:, -1] = free[:, -1]
    reached |= frontier

    while frontier.any():
        grown = np.zeros_like(frontier)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            s = np.roll(frontier, (dy, dx), axis=(0, 1))
            if dy == 1:
                s[0, :] = False
            elif dy == -1:
                s[-1, :] = False
            if dx == 1:
                s[:, 0] = False
            elif dx == -1:
                s[:, -1] = False
            grown |= s
        grown &= free & ~reached
        if not grown.any():
            break
        reached |= grown
        frontier = grown

    return reached


_SIDE_NAMES = ("top", "bottom", "left", "right")


def _compute_exterior_background(mask, outer_sides):
    """
    Which background pixels count as true "outside" vs. the shape's own interior gap.

    ``outer_sides`` is ``None`` (closed-shape flood fill from the image border - correct
    for a shape whose interior, if any, is fully enclosed, like a picture-frame
    outline) or an iterable of canvas sides from ``_SIDE_NAMES``.

    For an *open* shape - a tile piece that isn't a closed loop, meant to connect to a
    neighboring tile through one or more of its canvas edges - a plain border flood fill
    can't tell the connecting gap apart from true exterior, since both are reachable from
    the image border without obstruction. Instead, each declared outer side casts rays
    inward (parallel to that edge's normal): a background pixel counts as real exterior
    if it has clear line-of-sight - unblocked by mask - to *any* declared outer side.
    Background that only has line-of-sight to non-outer (connecting) sides is the gap,
    and gets no shadow/bevel. A pixel exactly between two mask edges on a non-outer axis
    (e.g. sandwiched left/right when only top/bottom are outer) is therefore correctly
    excluded even though it's technically reachable from the border through that gap.
    """

    background = ~mask
    if outer_sides is None:
        return _flood_fill_from_border(background)

    outer_sides = set(outer_sides)
    unknown = outer_sides - set(_SIDE_NAMES)
    if unknown:
        raise ValueError(f"Unknown outer side(s) {sorted(unknown)!r}, expected from {_SIDE_NAMES}")

    visible = np.zeros_like(mask)
    if "top" in outer_sides:
        visible |= ~np.logical_or.accumulate(mask, axis=0)
    if "bottom" in outer_sides:
        visible |= ~np.logical_or.accumulate(mask[::-1, :], axis=0)[::-1, :]
    if "left" in outer_sides:
        visible |= ~np.logical_or.accumulate(mask, axis=1)
    if "right" in outer_sides:
        visible |= ~np.logical_or.accumulate(mask[:, ::-1], axis=1)[:, ::-1]

    return background & visible


def _build_bevel_layer(mask_array, bevel_width, fade_distance, max_alpha, background=None):
    """
    Directional highlight/shadow band a few pixels inside the mask edge.

    ``background`` restricts which side of the mask counts as "outside" (see
    ``_distance_transform``).

    Builds a rounded height ramp from the edge (0) inward (1) and lights its surface
    normal from a fixed direction to decide highlight-vs-shadow and how strongly, then
    applies a *separately* calibrated distance falloff for the alpha envelope. Two
    corrections beyond a naive normal-map bevel.
    """

    normal_max_steps = int(np.ceil(bevel_width)) + 2
    normal_dist = _distance_transform(mask_array, background=background, max_steps=normal_max_steps)
    fade_dist = _distance_transform(mask_array, background=background, max_steps=int(np.ceil(fade_distance * 4)) + 2)

    height = np.clip(normal_dist / bevel_width, 0, 1)
    height = np.sin(height * (np.pi / 2))  # rounded ramp, matches a convex bevel profile

    height_img = Image.fromarray((height * 255).astype(np.uint8), mode="L")
    smooth_radius = max(1.0, bevel_width / 3.0)
    height = np.array(height_img.filter(ImageFilter.GaussianBlur(smooth_radius)), dtype=np.float32) / 255.0

    gy, gx = np.gradient(height)

    on_plateau = normal_dist >= bevel_width

    gy = np.where(on_plateau, 0.0, gy)
    gx = np.where(on_plateau, 0.0, gx)

    gain = 6.0
    gx, gy = gx * gain, gy * gain
    normal_z = 1.0
    norm = np.sqrt(gx**2 + gy**2 + normal_z**2)
    nx, ny, nz = -gx / norm, -gy / norm, normal_z / norm

    az = np.radians(LIGHT_AZIMUTH_DEGREES)
    el = np.radians(LIGHT_ELEVATION_DEGREES)
    lx, ly, lz = np.cos(el) * np.cos(az), -np.cos(el) * np.sin(az), np.sin(el)

    tilt = nx * lx + ny * ly + (nz - 1.0) * lz  # relative to a flat surface's own nz*lz baseline
    brightness = np.clip(tilt * 2.5, -1, 1)  # extra gain so the peak reaches full max_alpha

    in_band = fade_dist > 0
    peak_dist = 1.5
    fade = np.exp(-np.abs(fade_dist - peak_dist) / fade_distance)
    alpha = np.abs(brightness) * max_alpha * fade * in_band
    color = np.where(brightness >= 0, 255, 0)
    return color.astype(np.uint8), alpha.astype(np.uint8)


def generate_effect(shape_img: Image.Image, size: int, outer_sides=None) -> Image.Image:
    """
    Build a wall "effect" image from a wall "shape" mask.

    Parameters
    ----------
    shape_img : Image.Image
        The source shape mask (any mode; only alpha/opacity is used to find the outline).

    size : int
        Reference edge length used to scale blur radii and bevel width. Pass the tile's
        pixel size (e.g. 1500 for the original 80x80-tile canvas, or a proportionally
        scaled-down value for smaller tiles).

    outer_sides : iterable of str, optional
        ``None`` (default) for a closed shape, or a subset of ``"top"``, ``"bottom"``,
        ``"left"``, ``"right"`` - see ``_compute_exterior_background``. Needed for open
        (non-closed-loop) shapes that connect to a neighboring tile through one or more
        of their canvas edges.

    Returns
    -------
    Image.Image
        RGBA image the same size as ``shape_img``, containing the shadow + bevel + core.
    """

    shape_img = shape_img.convert("RGBA")
    alpha = np.array(shape_img.getchannel("A"), dtype=np.uint8)
    mask = alpha > 127

    blur_radius = _scale(OUTER_SHADOW_BLUR, size)
    core_width = max(1, round(_scale(CORE_WIDTH, size)))
    bevel_width = max(1.0, _scale(BEVEL_WIDTH, size))
    fade_distance = max(1.0, _scale(BEVEL_FADE_DISTANCE, size))
    shadow_max_alpha = OUTER_SHADOW_MAX_ALPHA
    core_alpha = CORE_ALPHA
    bevel_max_alpha = BEVEL_MAX_ALPHA

    exterior_bg = _compute_exterior_background(mask, outer_sides)

    # 1. Outer soft shadow: blur the mask
    exterior_mask_img = Image.fromarray((~exterior_bg * 255).astype(np.uint8), mode="L")
    shadow_alpha = np.array(exterior_mask_img.filter(ImageFilter.GaussianBlur(blur_radius)), dtype=np.float32)
    shadow_alpha = np.clip(shadow_alpha / 127.0 * shadow_max_alpha, 0, shadow_max_alpha)
    shadow_alpha = np.where(exterior_bg, shadow_alpha, 0)

    # 2. Core: solid black, within `core_width` px of the exterior contour
    outer_outline_dist = _distance_transform(mask, background=exterior_bg)
    is_core = mask & (outer_outline_dist > 0) & (outer_outline_dist <= core_width)
    core_alpha_arr = np.where(is_core, core_alpha, 0).astype(np.float32)

    # 3. Inner bevel: directional light/shade band just inside the exterior contour
    bevel_color, bevel_alpha_u8 = _build_bevel_layer(
        mask, bevel_width, fade_distance, bevel_max_alpha, background=exterior_bg
    )
    bevel_alpha = bevel_alpha_u8.astype(np.float32)
    bevel_alpha = np.where(is_core, 0, bevel_alpha)  # don't paint bevel over the core line

    h, w = mask.shape
    premult = np.zeros((h, w, 3), dtype=np.float32)
    out_alpha = np.zeros((h, w), dtype=np.float32)

    def composite_over(color_rgb, src_alpha):
        nonlocal out_alpha
        a = src_alpha / 255.0
        for c in range(3):
            premult[..., c] = color_rgb[c] * a + premult[..., c] * (1 - a)
        out_alpha = src_alpha + out_alpha * (1 - a)

    composite_over((0, 0, 0), shadow_alpha)
    bevel_rgb_stack = np.stack([bevel_color, bevel_color, bevel_color], axis=-1).astype(np.float32)
    a = bevel_alpha / 255.0
    for c in range(3):
        premult[..., c] = bevel_rgb_stack[..., c] * a + premult[..., c] * (1 - a)
    out_alpha = bevel_alpha + out_alpha * (1 - a)
    composite_over((0, 0, 0), core_alpha_arr)

    safe_alpha = np.where(out_alpha > 0, out_alpha, 1)
    straight_rgb = np.clip(premult / (safe_alpha[..., None] / 255.0), 0, 255)
    straight_rgb = np.where(out_alpha[..., None] > 0, straight_rgb, 0)

    out = np.concatenate([straight_rgb, out_alpha[..., None]], axis=-1)
    out = np.clip(out, 0, 255).astype(np.uint8)
    return Image.fromarray(out, mode="RGBA")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("shape_path", help="Path to the source shape mask PNG")
    parser.add_argument("output_path", help="Path to write the generated effect PNG")
    parser.add_argument(
        "--size",
        type=int,
        default=REFERENCE_SIZE,
        help=f"Reference edge length for scaling (default {REFERENCE_SIZE}, matching the "
        "original 80x80-tile canvas; scale proportionally for smaller tiles, e.g. "
        f"{REFERENCE_SIZE} * 75/80 for 75x75 tiles)",
    )
    parser.add_argument(
        "--outer-sides",
        default=None,
        help="For an open (non-closed-loop) shape, comma-separated list of which canvas "
        "sides are true exterior (get shadow+bevel), from top,bottom,left,right - any "
        "side not listed is treated as the shape's own connecting gap to a neighboring "
        "tile and gets no shadow/bevel. E.g. --outer-sides=bottom,left for an L-shaped "
        "corner piece connecting to neighbors above and to the right. Omit entirely for "
        "a closed shape like the original outer.png (border flood fill).",
    )
    args = parser.parse_args()

    outer_sides = args.outer_sides.split(",") if args.outer_sides else None

    shape_img = Image.open(args.shape_path)
    effect_img = generate_effect(shape_img, args.size, outer_sides=outer_sides)
    effect_img.save(args.output_path)
    print(f"Wrote {args.output_path} ({effect_img.size[0]}x{effect_img.size[1]})")


if __name__ == "__main__":
    main()
