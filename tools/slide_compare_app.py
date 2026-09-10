#!/usr/bin/env python3
"""
slide_compare_app.py
====================
Visual diff tool for slide templates vs. app-generated text overlays.

Pipeline: detect glyphs -> auto-group into text blocks (confidence scored) ->
apply the user's manual edits -> resolve manual links -> auto-match the rest ->
measure X / Y / font-size offsets per matched component.

Operator controls
  * Detection sensitivity slider   low = fewer false positives.
  * Edit boxes... window: delete / split boxes, build new boxes from selected
    glyphs (click, marquee-drag, or shift-click a run), and link boxes across
    the two images. Edits mirror to both images by default; turn mirroring off
    to edit one side and link manually. Every edit survives Re-analyze.

Dependencies:
    pip install numpy opencv-python pillow
"""

import math
import os
import sys

import cv2
import numpy as np

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    from PIL import Image, ImageDraw, ImageFont, ImageTk
except Exception as exc:  # pragma: no cover
    sys.exit(f"This tool needs tkinter and pillow: {exc}")


# ==========================================================================
#  Settings
# ==========================================================================
class Settings:
    def __init__(self):
        self.text_color = None
        self.bg_color = None
        self.sensitivity = 50
        self.color_tol = 60.0
        self.adaptive_c = 10
        self.min_glyph_px = 7
        self.min_glyph_area = 16
        self.min_glyphs_per_block = 2
        self.conf_threshold = 0.45
        self.adaptive_block = None
        self.alpha_thresh = 128
        self.alpha_text_max_cover = 0.35
        self.template_alpha_mode = "auto"
        self.app_alpha_mode = "auto"
        self.min_glyph_frac = 0.008
        self.max_glyph_frac = 0.25
        self.max_glyph_aspect = 12.0
        self.max_glyph_mult = 3.0
        self.join_x = 1.4
        self.join_y = 0.8
        self.match_max_dist = None
        self.x_tol = 2.0
        self.y_tol = 2.0
        self.font_tol = 0.04


def apply_sensitivity(s):
    f = max(0.0, min(1.0, (s.sensitivity - 1) / 99.0))

    def lerp(a, b):
        return a + (b - a) * f

    s.color_tol = lerp(28.0, 95.0)
    s.adaptive_c = int(round(lerp(16, 4)))
    s.min_glyph_px = int(round(lerp(11, 5)))
    s.min_glyph_area = int(round(lerp(45, 6)))
    s.min_glyphs_per_block = max(1, int(round(lerp(4, 1))))
    s.conf_threshold = lerp(0.80, 0.12)
    return s


def parse_color(text):
    text = (text or "").strip()
    if not text:
        return None
    parts = [int(p) for p in text.replace(" ", "").split(",")]
    if len(parts) != 3:
        raise ValueError("colour must be 'R,G,B'")
    r, g, b = parts
    return (b, g, r)


# ==========================================================================
#  Low-level helpers
# ==========================================================================
def _rect(w, h):
    return cv2.getStructuringElement(cv2.MORPH_RECT, (max(1, int(w)), max(1, int(h))))


def _clip01(v):
    return float(max(0.0, min(1.0, v)))


def _tri(x, lo, plo, phi, hi):
    if x <= lo or x >= hi:
        return 0.0
    if x < plo:
        return (x - lo) / (plo - lo)
    if x <= phi:
        return 1.0
    return (hi - x) / (hi - phi)


def _iou_box(a, b):
    ox = max(0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
    oy = max(0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
    inter = ox * oy
    union = a[2] * a[3] + b[2] * b[3] - inter
    return inter / union if union > 0 else 0.0


def load_rgba(path):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(path)
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR), None
    if img.shape[2] == 4:
        return img[:, :, :3].copy(), img[:, :, 3].copy()
    return img[:, :, :3].copy(), None


def _estimate_bg_color(bgr, opaque):
    ring = (opaque > 0) & (cv2.erode(opaque, _rect(15, 15)) == 0)
    if int(ring.sum()) > 50:
        return np.median(bgr[ring].reshape(-1, 3), axis=0)
    if int((opaque > 0).sum()) > 0:
        return np.median(bgr[opaque > 0].reshape(-1, 3), axis=0)
    return np.array([255.0, 255.0, 255.0])


# ==========================================================================
#  Detection
# ==========================================================================
def build_text_mask(bgr, alpha, s, role):
    h, w = bgr.shape[:2]
    if alpha is None:
        opaque, transparent = np.full((h, w), 255, np.uint8), False
    else:
        opaque = np.where(alpha >= s.alpha_thresh, 255, 0).astype(np.uint8)
        transparent = int(alpha.min()) < s.alpha_thresh
    frac = float((opaque > 0).mean())

    forced = getattr(s, f"{role}_alpha_mode")
    if forced == "text":
        alpha_is_text = True
    elif forced == "shape":
        alpha_is_text = False
    else:
        alpha_is_text = transparent and 0.0005 < frac < s.alpha_text_max_cover
    if alpha_is_text:
        return opaque.copy(), None

    if alpha is not None and transparent:
        bg = s.bg_color if s.bg_color is not None else _estimate_bg_color(bgr, opaque)
        a = (alpha.astype(np.float32) / 255.0)[..., None]
        comp = (bgr.astype(np.float32) * a + np.float32(bg)[None, None, :] * (1.0 - a)).astype(np.uint8)
        valid = cv2.erode(opaque, _rect(3, 3))
    else:
        comp, valid = bgr, opaque

    gray = cv2.cvtColor(comp, cv2.COLOR_BGR2GRAY)
    if s.text_color is not None:
        d = np.linalg.norm(comp.astype(np.float32) - np.float32(s.text_color), axis=2)
        mask = np.where(d <= s.color_tol, 255, 0).astype(np.uint8)
    else:
        block = s.adaptive_block or max(15, (min(h, w) // 25) | 1)
        if block % 2 == 0:
            block += 1
        inv = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block, s.adaptive_c
        )
        nrm = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block, s.adaptive_c)
        mask = inv if inv.mean() <= nrm.mean() else nrm
        if s.bg_color is not None:
            d = np.linalg.norm(comp.astype(np.float32) - np.float32(s.bg_color), axis=2)
            mask = cv2.bitwise_and(mask, np.where(d > s.color_tol, 255, 0).astype(np.uint8))

    mask = cv2.bitwise_and(mask, valid)
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, _rect(2, 2)), gray


def detect_glyphs(mask, gray, s, H, W):
    h_min = max(s.min_glyph_px, int(round(H * s.min_glyph_frac)))
    h_max = int(round(H * s.max_glyph_frac))
    n, labels, st, ct = cv2.connectedComponentsWithStats(mask, 8)
    raw = []
    for i in range(1, n):
        x, y, ww, hh, area = (int(st[i, k]) for k in range(5))
        if hh < h_min or hh > h_max or ww < 1 or ww > hh * s.max_glyph_aspect:
            continue
        if area < s.min_glyph_area:
            continue
        fill = area / float(ww * hh)
        if fill < 0.04:
            continue
        if x <= 0 or y <= 0 or x + ww >= W or y + hh >= H:
            continue
        contrast = None
        if gray is not None:
            x0, y0 = max(0, x - 3), max(0, y - 3)
            x1, y1 = min(W, x + ww + 3), min(H, y + hh + 3)
            sl, sg = labels[y0:y1, x0:x1], gray[y0:y1, x0:x1].astype(np.float32)
            fg, bg = sg[sl == i], sg[sl == 0]
            if fg.size and bg.size:
                contrast = float(abs(np.median(fg) - np.median(bg)))
        raw.append(dict(x=x, y=y, w=ww, h=hh, cx=float(ct[i, 0]), cy=float(ct[i, 1]), fill=fill, contrast=contrast))
    if not raw:
        return [], 0.0
    hs = np.array([g["h"] for g in raw], np.float32)
    med = float(np.median(hs))
    band = hs[(hs > 0.5 * med) & (hs < 2.0 * med)]
    mh = float(np.median(band)) if band.size else med
    return [g for g in raw if g["h"] <= s.max_glyph_mult * mh], mh


def block_confidence(gl, mh):
    n = len(gl)
    hs = np.array([g["h"] for g in gl], np.float32)
    fills = np.array([g["fill"] for g in gl], np.float32)
    cons = [g["contrast"] for g in gl if g["contrast"] is not None]
    s_n = _clip01((n / 4.0) ** 0.5)
    cv = float(np.std(hs) / (np.mean(hs) + 1e-6)) if n >= 2 else 0.15
    s_h = _clip01(1.25 - cv / 0.5)
    order = sorted(gl, key=lambda g: g["cy"])
    lines = [[order[0]]]
    for g in order[1:]:
        (lines.append([g]) if g["cy"] - lines[-1][-1]["cy"] > 0.7 * mh else lines[-1].append(g))
    base_std = np.mean([float(np.std([g["y"] + g["h"] for g in ln])) for ln in lines])
    s_base = _clip01(1.1 - (base_std / max(1.0, mh)) / 0.30)
    s_fill = _tri(float(np.mean(fills)), 0.05, 0.14, 0.72, 0.92)
    s_con = 1.0 if not cons else _clip01(float(np.mean(cons)) / 40.0)
    x0 = min(g["x"] for g in gl)
    y0 = min(g["y"] for g in gl)
    x1 = max(g["x"] + g["w"] for g in gl)
    y1 = max(g["y"] + g["h"] for g in gl)
    cov = sum(g["w"] * g["h"] for g in gl) / max(1, (x1 - x0) * (y1 - y0))
    s_cov = _clip01(cov / 0.15) * (1.0 if cov < 0.9 else 0.3)
    parts = dict(contrast=s_con, height=s_h, baseline=s_base, count=s_n, fill=s_fill, coverage=s_cov)
    conf = 0.27 * s_con + 0.22 * s_h + 0.17 * s_base + 0.12 * s_n + 0.12 * s_fill + 0.10 * s_cov
    return _clip01(conf), parts


def make_block(glyphs, mh, manual=False):
    x0 = min(g["x"] for g in glyphs)
    y0 = min(g["y"] for g in glyphs)
    x1 = max(g["x"] + g["w"] for g in glyphs)
    y1 = max(g["y"] + g["h"] for g in glyphs)
    ghs = np.array([g["h"] for g in glyphs], np.float32)
    gh = float(np.percentile(ghs, 75)) if len(ghs) >= 3 else float(ghs.max())
    conf, parts = block_confidence(glyphs, mh if mh > 0 else max(1.0, gh))
    return dict(
        x=int(x0),
        y=int(y0),
        w=int(x1 - x0),
        h=int(y1 - y0),
        cx=x0 + (x1 - x0) / 2.0,
        cy=y0 + (y1 - y0) / 2.0,
        glyph_h=gh,
        n_glyphs=len(glyphs),
        confidence=conf,
        score_parts=parts,
        glyphs=list(glyphs),
        manual=manual,
    )


def _merge_close_boxes(boxes, gx, gy):
    boxes = [dict(b) for b in boxes]
    changed = True
    while changed:
        changed, out = False, []
        for b in boxes:
            hit = None
            for o in out:
                if (
                    b["x"] - gx <= o["x"] + o["w"]
                    and o["x"] - gx <= b["x"] + b["w"]
                    and b["y"] - gy <= o["y"] + o["h"]
                    and o["y"] - gy <= b["y"] + b["h"]
                ):
                    hit = o
                    break
            if hit is None:
                out.append(b)
            else:
                nx, ny = min(hit["x"], b["x"]), min(hit["y"], b["y"])
                hit["w"] = max(hit["x"] + hit["w"], b["x"] + b["w"]) - nx
                hit["h"] = max(hit["y"] + hit["h"], b["y"] + b["h"]) - ny
                hit["x"], hit["y"], changed = nx, ny, True
        boxes = out
    return boxes


def group_blocks(glyphs, mh, shape, s):
    H, W = shape
    if not glyphs or mh <= 0:
        return []
    clean = np.zeros((H, W), np.uint8)
    for g in glyphs:
        clean[g["y"] : g["y"] + g["h"], g["x"] : g["x"] + g["w"]] = 255
    gx, gy = max(1, round(s.join_x * mh)), max(1, round(s.join_y * mh))
    merged = cv2.dilate(clean, _rect(gx, gy))
    n, _, st, _ = cv2.connectedComponentsWithStats((merged > 0).astype(np.uint8), 8)
    boxes = [dict(x=int(st[i, 0]), y=int(st[i, 1]), w=int(st[i, 2]), h=int(st[i, 3])) for i in range(1, n)]
    boxes = _merge_close_boxes(boxes, gx // 2, gy // 2)
    out = []
    for b in boxes:
        inside = [g for g in glyphs if b["x"] <= g["cx"] <= b["x"] + b["w"] and b["y"] <= g["cy"] <= b["y"] + b["h"]]
        if len(inside) < s.min_glyphs_per_block:
            continue
        xs0 = min(g["x"] for g in inside)
        ys0 = min(g["y"] for g in inside)
        if (
            max(g["x"] + g["w"] for g in inside) - xs0 < mh * 0.3
            or max(g["y"] + g["h"] for g in inside) - ys0 < mh * 0.3
        ):
            continue
        blk = make_block(inside, mh, manual=False)
        if blk["confidence"] < s.conf_threshold:
            continue
        out.append(blk)
    out.sort(key=lambda bl: (round(bl["cy"] / max(1.0, mh)), bl["x"]))
    return out


def order_glyphs(glyphs, mh):
    if not glyphs:
        return []
    gl = sorted(glyphs, key=lambda g: g["cy"])
    lines, cur = [], [gl[0]]
    for g in gl[1:]:
        (lines.append(cur) or (cur := [g])) if g["cy"] - cur[-1]["cy"] > 0.7 * mh else cur.append(g)
    lines.append(cur)
    out = []
    for ln in lines:
        out.extend(sorted(ln, key=lambda g: g["x"]))
    return out


# ==========================================================================
#  Split geometry
# ==========================================================================
def axis_gaps(glyphs, axis):
    if axis == "x":
        iv = sorted((g["x"], g["x"] + g["w"]) for g in glyphs)
    else:
        iv = sorted((g["y"], g["y"] + g["h"]) for g in glyphs)
    merged = []
    for lo, hi in iv:
        if merged and lo <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    gaps = [
        dict(center=(a[1] + b[0]) / 2.0, size=b[0] - a[1], lo=a[1], hi=b[0])
        for a, b in zip(merged, merged[1:])
        if b[0] > a[1]
    ]
    ext = (merged[0][0], merged[-1][1]) if merged else (0, 0)
    return sorted(gaps, key=lambda gp: gp["size"], reverse=True), ext


def snap_to_gap(pos, gaps):
    if not gaps:
        return pos
    inside = [g for g in gaps if g["lo"] <= pos <= g["hi"]]
    return inside[0]["center"] if inside else min(gaps, key=lambda g: abs(g["center"] - pos))["center"]


def guess_split_axis(glyphs, mh):
    best, best_rel = "y", -1.0
    for axis in ("y", "x"):
        g, _ = axis_gaps(glyphs, axis)
        rel = (g[0]["size"] / mh) if g else 0.0
        if rel > best_rel:
            best, best_rel = axis, rel
    return best


def suggest_cuts(glyphs, axis, mh):
    gaps, _ = axis_gaps(glyphs, axis)
    if not gaps:
        return []
    thr = max(float(np.median([g["size"] for g in gaps])) * 1.8, 0.55 * mh if axis == "y" else 1.1 * mh, 3.0)
    return sorted(g["center"] for g in gaps if g["size"] >= thr) or [gaps[0]["center"]]


def split_glyphs(glyphs, axis, cuts):
    if not cuts:
        return [list(glyphs)]
    cuts = sorted(cuts)
    key = (lambda g: g["cx"]) if axis == "x" else (lambda g: g["cy"])
    buckets = [[] for _ in range(len(cuts) + 1)]
    for g in glyphs:
        p, i = key(g), 0
        while i < len(cuts) and p >= cuts[i]:
            i += 1
        buckets[i].append(g)
    return [b for b in buckets if b]


def split_block(block, axis, cuts, mh):
    gl = block.get("glyphs")
    if not gl:
        return [block]
    parts = split_glyphs(gl, axis, cuts)
    return [make_block(p, mh, manual=True) for p in parts] if len(parts) >= 2 else [block]


# ==========================================================================
#  Manual edits (delete / create) + linking
# ==========================================================================
def _spec(block):
    return {"anchor": (block["cx"], block["cy"]), "bbox": (block["x"], block["y"], block["w"], block["h"])}


def glyph_spec(g):
    return {"cx": g["cx"], "cy": g["cy"], "x": g["x"], "y": g["y"], "w": g["w"], "h": g["h"]}


def find_target(blocks, spec):
    ax, ay = spec["anchor"]
    bb = spec["bbox"]
    best, best_score = None, 0.0
    for k, b in enumerate(blocks):
        score = _iou_box(bb, (b["x"], b["y"], b["w"], b["h"]))
        if b["x"] <= ax <= b["x"] + b["w"] and b["y"] <= ay <= b["y"] + b["h"]:
            score += 0.3
        if score > best_score:
            best, best_score = k, score
    return best if best_score >= 0.15 else None


def resolve_glyphs(pool, specs, mh):
    out, used = [], set()
    for sp in specs:
        bb = (sp["x"], sp["y"], sp["w"], sp["h"])
        best, best_score = None, 0.0
        for k, g in enumerate(pool):
            if k in used:
                continue
            score = _iou_box(bb, (g["x"], g["y"], g["w"], g["h"]))
            if math.hypot(g["cx"] - sp["cx"], g["cy"] - sp["cy"]) < 0.5 * mh:
                score += 1.0
            if score > best_score:
                best, best_score = k, score
        if best is not None and best_score >= 0.25:
            used.add(best)
            out.append(pool[best])
    return out


def apply_ops(result, ops):
    info = {
        "template": (list(result.t_blocks), result.t_glyphs_all, result.t_mh),
        "app": (list(result.a_blocks), result.a_glyphs_all, result.a_mh),
    }
    for op in ops:
        blocks, pool, mh = info[op["role"]]
        if op["kind"] == "split":
            i = find_target(blocks, op)
            if i is not None:
                blocks[i : i + 1] = split_block(blocks[i], op["axis"], op["cuts"], mh)
        elif op["kind"] == "delete":
            i = find_target(blocks, op)
            if i is not None:
                blocks.pop(i)
        elif op["kind"] == "create":
            gs = resolve_glyphs(pool, op["glyphs"], mh)
            if not gs:
                continue
            chosen = {id(g) for g in gs}
            rebuilt = []
            for b in blocks:
                remain = [g for g in b["glyphs"] if id(g) not in chosen]
                if not remain:
                    continue
                rebuilt.append(
                    b if len(remain) == len(b["glyphs"]) else make_block(remain, mh, manual=b.get("manual", False))
                )
            rebuilt.append(make_block(gs, mh, manual=True))
            blocks[:] = rebuilt
        info[op["role"]] = (blocks, pool, mh)
    for role in ("template", "app"):
        blocks, _, mh = info[role]
        blocks.sort(key=lambda bl: (round(bl["cy"] / max(1.0, mh)), bl["x"]))
    result.t_blocks, result.a_blocks = info["template"][0], info["app"][0]


def match_blocks(tb, ab, max_dist):
    cand = []
    for i, t in enumerate(tb):
        for j, a in enumerate(ab):
            d = math.hypot(t["cx"] - a["cx"], t["cy"] - a["cy"])
            if d > max_dist:
                continue
            if min(t["glyph_h"], a["glyph_h"]) / max(t["glyph_h"], a["glyph_h"]) < 0.4:
                continue
            cand.append((d, i, j))
    cand.sort()
    ut, ua, pairs = set(), set(), []
    for _, i, j in cand:
        if i in ut or j in ua:
            continue
        ut.add(i)
        ua.add(j)
        pairs.append((i, j))
    return pairs


def match_with_links(tb, ab, links, max_dist):
    used_t, used_a, forced = set(), set(), []
    for L in links:
        ti = find_target(tb, L["t"])
        aj = find_target(ab, L["a"])
        if ti is None or aj is None or ti in used_t or aj in used_a:
            continue
        used_t.add(ti)
        used_a.add(aj)
        forced.append((ti, aj))
    rem_t = [i for i in range(len(tb)) if i not in used_t]
    rem_a = [j for j in range(len(ab)) if j not in used_a]
    auto = [(rem_t[i], rem_a[j]) for i, j in match_blocks([tb[i] for i in rem_t], [ab[j] for j in rem_a], max_dist)]
    pairs = forced + auto
    taken_t = {p[0] for p in pairs}
    taken_a = {p[1] for p in pairs}
    return (
        pairs,
        [i for i in range(len(tb)) if i not in taken_t],
        [j for j in range(len(ab)) if j not in taken_a],
        set(range(len(forced))),
    )


def analyze_pair(t, a):
    dx = {"left": a["x"] - t["x"], "center": a["cx"] - t["cx"], "right": (a["x"] + a["w"]) - (t["x"] + t["w"])}
    dy = {"top": a["y"] - t["y"], "center": a["cy"] - t["cy"], "bottom": (a["y"] + a["h"]) - (t["y"] + t["h"])}
    ha = min(dx, key=lambda k: abs(dx[k]))
    va = min(dy, key=lambda k: abs(dy[k]))
    fr = a["glyph_h"] / t["glyph_h"] if t["glyph_h"] else float("nan")
    return dict(
        dx=dx,
        dy=dy,
        halign=ha,
        valign=va,
        x_off=float(dx[ha]),
        y_off=float(dy[va]),
        font_ratio=fr,
        width_ratio=a["w"] / t["w"] if t["w"] else float("nan"),
    )


def anchor_x(box, a):
    return {"left": box["x"], "center": box["cx"], "right": box["x"] + box["w"]}[a]


def anchor_y(box, a):
    return {"top": box["y"], "center": box["cy"], "bottom": box["y"] + box["h"]}[a]


class Result:
    pass


def _as_bgr_alpha(src):
    return src if isinstance(src, tuple) else load_rgba(src)


def analyze_images(t_src, a_src, s, edit_actions=None):
    apply_sensitivity(s)
    t_bgr, t_alpha = _as_bgr_alpha(t_src)
    a_bgr, a_alpha = _as_bgr_alpha(a_src)
    if t_bgr.shape[:2] != a_bgr.shape[:2]:
        a_bgr = cv2.resize(a_bgr, (t_bgr.shape[1], t_bgr.shape[0]))
        if a_alpha is not None:
            a_alpha = cv2.resize(a_alpha, (t_bgr.shape[1], t_bgr.shape[0]))
    H, W = t_bgr.shape[:2]

    r = Result()
    r.t_bgr, r.a_bgr = t_bgr, a_bgr
    r.t_mask, t_gray = build_text_mask(t_bgr, t_alpha, s, "template")
    r.a_mask, a_gray = build_text_mask(a_bgr, a_alpha, s, "app")
    r.t_glyphs_all, r.t_mh = detect_glyphs(r.t_mask, t_gray, s, H, W)
    r.a_glyphs_all, r.a_mh = detect_glyphs(r.a_mask, a_gray, s, H, W)
    r.t_order = order_glyphs(r.t_glyphs_all, max(1.0, r.t_mh))
    r.a_order = order_glyphs(r.a_glyphs_all, max(1.0, r.a_mh))
    r.t_blocks = group_blocks(r.t_glyphs_all, r.t_mh, (H, W), s)
    r.a_blocks = group_blocks(r.a_glyphs_all, r.a_mh, (H, W), s)

    ops, links = [], []
    for act in edit_actions or []:
        ops.extend(act.get("ops", []))
        links.extend(act.get("links", []))
    if ops:
        apply_ops(r, ops)

    max_dist = s.match_max_dist or 0.15 * math.hypot(W, H)
    r.pairs, r.unmatched_t, r.unmatched_a, r.linked_pairs = match_with_links(r.t_blocks, r.a_blocks, links, max_dist)
    r.analyses = {k: analyze_pair(r.t_blocks[i], r.a_blocks[j]) for k, (i, j) in enumerate(r.pairs)}
    r.settings = s
    return r


# ==========================================================================
#  Rendering (review window)
# ==========================================================================
CYAN, MAGENTA, RED, GREEN, ORANGE = ((255, 255, 0), (255, 0, 255), (255, 80, 80), (80, 220, 80), (255, 170, 40))


def _font(size):
    for name in ("DejaVuSans.ttf", "Arial.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _text(draw, xy, txt, font, fill=(255, 255, 255)):
    x, y = xy
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        draw.text((x + ox, y + oy), txt, font=font, fill=(0, 0, 0))
    draw.text((x, y), txt, font=font, fill=fill)


def _arrow(draw, p0, p1, fill, width=2):
    draw.line([p0, p1], fill=fill, width=width)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for da in (math.radians(150), math.radians(-150)):
        draw.line([p1, (p1[0] + 12 * math.cos(ang + da), p1[1] + 12 * math.sin(ang + da))], fill=fill, width=width)


def _bgr2pil(bgr):
    return Image.fromarray(cv2.cvtColor(np.ascontiguousarray(bgr), cv2.COLOR_BGR2RGB))


def _resize(bgr, scale):
    if abs(scale - 1.0) < 1e-3:
        return bgr
    interp = cv2.INTER_NEAREST if scale >= 1 else cv2.INTER_AREA
    return cv2.resize(
        bgr, (max(1, round(bgr.shape[1] * scale)), max(1, round(bgr.shape[0] * scale))), interpolation=interp
    )


def _roi_for(*boxes, pad, shape):
    H, W = shape
    x0 = max(0, min(b["x"] for b in boxes) - pad)
    y0 = max(0, min(b["y"] for b in boxes) - pad)
    x1 = min(W, max(b["x"] + b["w"] for b in boxes) + pad)
    y1 = min(H, max(b["y"] + b["h"] for b in boxes) + pad)
    return x0, y0, x1, y1


def _darken_outside(region, box_local):
    out = (region.astype(np.float32) * 0.28).astype(np.uint8)
    x, y, w, h = box_local
    out[y : y + h, x : x + w] = region[y : y + h, x : x + w]
    return out


def _fit_scale(rw, rh, aw, ah, panels=1):
    return max(0.1, min(12.0, max(120, (aw - 40 - 16 * (panels - 1)) / panels) / rw, max(120, ah - 120) / rh))


def _compose_overlay(r, roi, isolate):
    x0, y0, x1, y1 = roi
    base = r.t_bgr[y0:y1, x0:x1].copy()
    if isolate:
        base = (base.astype(np.float32) * 0.28).astype(np.uint8)
    tm = r.t_mask[y0:y1, x0:x1] > 0
    am = r.a_mask[y0:y1, x0:x1] > 0
    base[tm & ~am] = (0, 0, 255)
    base[am & ~tm] = (0, 255, 0)
    base[tm & am] = (0, 255, 255)
    return base


def render_pair(r, key, mode, isolate, aw, ah, scale=None):
    i, j = r.pairs[key]
    t, a = r.t_blocks[i], r.a_blocks[j]
    res = r.analyses[key]
    H, W = r.t_bgr.shape[:2]
    pad = int(max(24, 0.9 * max(t["glyph_h"], a["glyph_h"])))
    x0, y0, x1, y1 = _roi_for(t, a, pad=pad, shape=(H, W))
    rw, rh = x1 - x0, y1 - y0
    tl = (t["x"] - x0, t["y"] - y0, t["w"], t["h"])
    al = (a["x"] - x0, a["y"] - y0, a["w"], a["h"])
    axt, axa = anchor_x(t, res["halign"]) - x0, anchor_x(a, res["halign"]) - x0
    ayt, aya = anchor_y(t, res["valign"]) - y0, anchor_y(a, res["valign"]) - y0
    overlay = mode == "overlay"
    if scale is None:
        scale = _fit_scale(rw, rh, aw, ah, 1 if overlay else 2)

    def S(v):
        return v * scale

    if overlay:
        panels = [
            (
                "OVERLAY, red=template  green=app  yellow=aligned",
                _compose_overlay(r, (x0, y0, x1, y1), isolate),
                True,
                True,
            )
        ]
    else:
        lt = r.t_bgr[y0:y1, x0:x1].copy()
        rt = r.a_bgr[y0:y1, x0:x1].copy()
        if isolate:
            lt, rt = _darken_outside(lt, tl), _darken_outside(rt, al)
        panels = [("TEMPLATE", lt, True, False), ("APP", rt, False, True)]

    sc = [_resize(p[1], scale) for p in panels]
    sw, sh, cols = sc[0].shape[1], sc[0].shape[0], len(panels)
    hh, fh, gap, bd = 30, 58, 16, 14
    canvas = np.full((bd + hh + sh + fh + bd, bd * 2 + sw * cols + gap * (cols - 1), 3), 32, np.uint8)
    for c, img in enumerate(sc):
        ox = bd + c * (sw + gap)
        canvas[bd + hh : bd + hh + sh, ox : ox + sw] = img
    pil = _bgr2pil(canvas)
    d = ImageDraw.Draw(pil)
    ft, fl, fb = _font(16), _font(13), _font(20)
    tags = ("[linked] " if key in r.linked_pairs else "") + (
        "[manual] " if (t.get("manual") or a.get("manual")) else ""
    )
    _text(
        d,
        (bd, bd + 4),
        f"Component #{key + 1} {tags}  template {t['w']}x{t['h']} (c{t['confidence']:.2f})"
        f"  app {a['w']}x{a['h']} (c{a['confidence']:.2f})",
        ft,
    )
    for c, (name, _, dt, da) in enumerate(panels):
        ox, oy = bd + c * (sw + gap), bd + hh
        _text(d, (ox + 4, oy + 4) if overlay else (ox + 4, oy - 18), name, fl)
        d.line([(ox + S(axt), oy), (ox + S(axt), oy + sh)], fill=CYAN, width=1)
        d.line([(ox + S(axa), oy), (ox + S(axa), oy + sh)], fill=MAGENTA, width=1)
        d.line([(ox, oy + S(ayt)), (ox + sw, oy + S(ayt))], fill=CYAN, width=1)
        d.line([(ox, oy + S(aya)), (ox + sw, oy + S(aya))], fill=MAGENTA, width=1)
        if dt:
            d.rectangle(
                [ox + S(tl[0]), oy + S(tl[1]), ox + S(tl[0] + tl[2]), oy + S(tl[1] + tl[3])], outline=CYAN, width=2
            )
        if da:
            d.rectangle(
                [ox + S(al[0]), oy + S(al[1]), ox + S(al[0] + al[2]), oy + S(al[1] + al[3])], outline=MAGENTA, width=2
            )
        if overlay and (res["x_off"] or res["y_off"]):
            sx, sy, mx, my = ox + S(axt), oy + S(ayt), ox + S(axa), oy + S(aya)
            _arrow(d, (sx, (sy + my) / 2), (mx, (sy + my) / 2), (255, 255, 255), 2)
            _arrow(d, (mx, sy), (mx, my), (255, 255, 255), 2)
            _text(d, ((sx + mx) / 2 - 20, (sy + my) / 2 - 22), f"ΔX {res['x_off']:+.1f}", fl)
            _text(d, (mx + 6, (sy + my) / 2 - 6), f"ΔY {res['y_off']:+.1f}", fl)
    fr = res["font_ratio"]
    xy_ok = abs(res["x_off"]) <= r.settings.x_tol and abs(res["y_off"]) <= r.settings.y_tol
    f_ok = abs(fr - 1.0) <= r.settings.font_tol
    fy = bd + hh + sh + 10
    _text(
        d,
        (bd, fy),
        f"ΔX = {res['x_off']:+.1f} px ({res['halign']})        " f"ΔY = {res['y_off']:+.1f} px ({res['valign']})",
        fb,
        fill=GREEN if xy_ok else RED,
    )
    fv = "ok" if f_ok else ("TOO BIG" if fr > 1 else "TOO SMALL")
    _text(
        d,
        (bd, fy + 26),
        f"FONT = {fr * 100:.1f}% of template ({fv})     " f"[cyan = template anchor, magenta = app anchor]",
        fl,
        fill=GREEN if f_ok else RED,
    )
    return pil


def render_single(r, which, idx, aw, ah, scale=None):
    bgr = r.t_bgr if which == "template" else r.a_bgr
    box = (r.t_blocks if which == "template" else r.a_blocks)[idx]
    H, W = bgr.shape[:2]
    pad = int(max(24, 0.9 * box["glyph_h"]))
    x0, y0, x1, y1 = _roi_for(box, pad=pad, shape=(H, W))
    region = _darken_outside(bgr[y0:y1, x0:x1].copy(), (box["x"] - x0, box["y"] - y0, box["w"], box["h"]))
    if scale is None:
        scale = _fit_scale(x1 - x0, y1 - y0, aw, ah, 1)
    scd = _resize(region, scale)
    canvas = np.full((scd.shape[0] + 90, scd.shape[1] + 28, 3), 32, np.uint8)
    canvas[60 : 60 + scd.shape[0], 14 : 14 + scd.shape[1]] = scd
    pil = _bgr2pil(canvas)
    d = ImageDraw.Draw(pil)
    _text(
        d,
        (14, 8),
        ("MISSING IN APP, template only" if which == "template" else "EXTRA IN APP, not in template"),
        _font(18),
        fill=RED,
    )
    _text(
        d,
        (14, 34),
        f"{'[manual] ' if box.get('manual') else ''}{which} box "
        f"{box['x']},{box['y']} {box['w']}x{box['h']}  "
        f"glyph_h={box['glyph_h']:.1f}  confidence={box['confidence']:.2f}",
        _font(13),
    )
    bl = (box["x"] - x0, box["y"] - y0, box["w"], box["h"])
    d.rectangle(
        [14 + bl[0] * scale, 60 + bl[1] * scale, 14 + (bl[0] + bl[2]) * scale, 60 + (bl[1] + bl[3]) * scale],
        outline=RED,
        width=2,
    )
    return pil


def render_overview(r, mode, aw, ah, scale=None):
    H, W = r.t_bgr.shape[:2]
    if mode == "overlay":
        base = r.t_bgr.copy()
        base[(r.t_mask > 0) & (r.a_mask == 0)] = (0, 0, 255)
        base[(r.a_mask > 0) & (r.t_mask == 0)] = (0, 255, 0)
        base[(r.t_mask > 0) & (r.a_mask > 0)] = (0, 255, 255)
        sc = scale or _fit_scale(W, H, aw, ah, 1)
        pil = _bgr2pil(_resize(base, sc))
        d = ImageDraw.Draw(pil)
        for k, (i, j) in enumerate(r.pairs, 1):
            for box, col in ((r.t_blocks[i], CYAN), (r.a_blocks[j], MAGENTA)):
                c = GREEN if (k - 1) in r.linked_pairs else (ORANGE if box.get("manual") else col)
                d.rectangle(
                    [box["x"] * sc, box["y"] * sc, (box["x"] + box["w"]) * sc, (box["y"] + box["h"]) * sc],
                    outline=c,
                    width=1,
                )
            t = r.t_blocks[i]
            tag = "L" if (k - 1) in r.linked_pairs else ""
            _text(d, (t["x"] * sc, max(0, t["y"] * sc - 16)), f"{tag}{k} c{t['confidence']:.2f}", _font(13))
        return pil
    sc = scale or _fit_scale(W, H, aw, ah, 2)
    out = []
    for bgr, blocks, col in ((r.t_bgr, r.t_blocks, RED), (r.a_bgr, r.a_blocks, GREEN)):
        pil = _bgr2pil(_resize(bgr, sc))
        d = ImageDraw.Draw(pil)
        for k, b in enumerate(blocks, 1):
            d.rectangle(
                [b["x"] * sc, b["y"] * sc, (b["x"] + b["w"]) * sc, (b["y"] + b["h"]) * sc],
                outline=ORANGE if b.get("manual") else col,
                width=2,
            )
            _text(d, (b["x"] * sc, max(0, b["y"] * sc - 16)), f"{k} c{b['confidence']:.2f}", _font(13))
        out.append(pil)
    gap = 16
    canvas = Image.new("RGB", (out[0].width * 2 + gap, out[0].height), (32, 32, 32))
    canvas.paste(out[0], (0, 0))
    canvas.paste(out[1], (out[0].width + gap, 0))
    return canvas


# ==========================================================================
#  Split-on-gaps dialog (used from the box editor)
# ==========================================================================
class SplitDialog(tk.Toplevel):
    def __init__(self, owner, images, candidates, on_apply):
        super().__init__(owner)
        self.images = images  # {"template": bgr, "app": bgr}
        self.candidates = candidates  # {role: (block, mh)}
        self.on_apply = on_apply
        self.title("Split box on character gaps")
        self.transient(owner)
        self.grab_set()
        self.minsize(470, 320)
        self.geometry("660x470")
        self._order = sorted(candidates, key=lambda r: -candidates[r][0]["n_glyphs"])
        self.mh = max(mh for _, mh in candidates.values()) or 12.0
        self.pad = max(10, int(0.5 * self.mh))
        self.axis = tk.StringVar(value=guess_split_axis(candidates[self._order[0]][0]["glyphs"], max(1.0, self.mh)))
        self.cuts, self.layout, self._drag = [], {}, None
        self._cfg_job, self._last = None, (0, 0)

        bar = ttk.Frame(self, padding=(8, 6))
        bar.pack(fill="x")
        ttk.Label(bar, text="Cut:").pack(side="left")
        ttk.Radiobutton(bar, text="Rows", value="y", variable=self.axis, command=self._on_axis).pack(side="left")
        ttk.Radiobutton(bar, text="Columns", value="x", variable=self.axis, command=self._on_axis).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(bar, text="Auto", width=6, command=self._auto).pack(side="left")
        ttk.Button(bar, text="Clear", width=6, command=lambda: (self.cuts.clear(), self._redraw())).pack(
            side="left", padx=4
        )
        self.canvas = tk.Canvas(self, background="#1b1b1b", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=(0, 4))
        self.canvas.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Button-1>", self._on_down)
        self.canvas.bind("<B1-Motion>", self._on_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_up)
        self.canvas.bind("<Button-3>", self._on_remove)
        self.canvas.bind("<Double-Button-1>", self._on_remove)
        bottom = ttk.Frame(self, padding=(8, 6))
        bottom.pack(fill="x")
        self.info = ttk.Label(bottom, text="")
        self.info.pack(side="left")
        self.ok = ttk.Button(bottom, text="Apply split", command=self._apply)
        self.ok.pack(side="right")
        ttk.Button(bottom, text="Cancel", command=self.destroy).pack(side="right", padx=4)
        self._suggest()
        self.after(30, self._relayout)

    def _span(self, b):
        return (b["y"], max(1, b["h"])) if self.axis.get() == "y" else (b["x"], max(1, b["w"]))

    def _suggest(self):
        for r in self._order:
            b, mh = self.candidates[r]
            centers = suggest_cuts(b["glyphs"], self.axis.get(), max(1.0, mh))
            if centers:
                lo, ext = self._span(b)
                self.cuts = [_clip01((c - lo) / ext) for c in centers]
                return
        self.cuts = []

    def _auto(self):
        self._suggest()
        self._redraw()

    def _on_axis(self):
        self._suggest()
        self._relayout()

    def _on_configure(self, e):
        if (e.width, e.height) == self._last or e.width < 40:
            return
        self._last = (e.width, e.height)
        if self._cfg_job:
            self.after_cancel(self._cfg_job)
        self._cfg_job = self.after(60, self._relayout)

    def _relayout(self):
        self._cfg_job = None
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 40 or h < 40:
            return self.after(50, self._relayout)
        roles = [r for r in ("template", "app") if r in self.candidates]
        axis, pad, gap, m = self.axis.get(), self.pad, 10, 8
        sp = {}
        for r in roles:
            b = self.candidates[r][0]
            lo, ext = self._span(b)
            sp[r] = (b, lo, ext, max(1, b["w"] if axis == "y" else b["h"]))
        sb = (h if axis == "y" else w) - 2 * m
        cb = (w if axis == "y" else h) - 2 * m - gap * (len(roles) - 1)
        self._lbox = max(
            8.0,
            min(
                sb / max(1 + 2 * pad / sp[r][2] for r in roles),
                cb / sum((sp[r][3] + 2 * pad) / sp[r][2] for r in roles),
            ),
        )
        sc = {r: max(0.02, min(40.0, self._lbox / sp[r][2])) for r in roles}
        self._s0 = m + max(pad * sc[r] for r in roles)
        base = np.full((h, w, 3), 27, np.uint8)
        cpos = m
        self.layout = {}
        for r in roles:
            b, lo, ext, cross = sp[r]
            z = sc[r]
            nx0, ny0 = b["x"] - pad, b["y"] - pad
            sx, sy = (cpos, self._s0 - pad * z) if axis == "y" else (self._s0 - pad * z, cpos)
            cpos += (cross + 2 * pad) * z + gap
            bgr = self.images[r]
            H0, W0 = bgr.shape[:2]
            cx0, cy0 = max(0, nx0), max(0, ny0)
            crop = bgr[cy0 : min(H0, b["y"] + b["h"] + pad) :, cx0 : min(W0, b["x"] + b["w"] + pad)]
            asx, asy = sx + (cx0 - nx0) * z, sy + (cy0 - ny0) * z
            self._paste(base, crop, asx, asy, z)
            self.layout[r] = dict(
                block=b, gaps=axis_gaps(b["glyphs"], axis)[0], scale=z, cx0=cx0, cy0=cy0, sx=asx, sy=asy, lo=lo, ext=ext
            )
        self._base = ImageTk.PhotoImage(_bgr2pil(base))
        self._redraw()

    @staticmethod
    def _paste(dst, crop, sx, sy, scale):
        if crop.size == 0:
            return
        rc = _resize(crop, scale)
        rh, rw = rc.shape[:2]
        x, y = int(round(sx)), int(round(sy))
        dx0, dy0 = max(0, x), max(0, y)
        dx1, dy1 = min(dst.shape[1], x + rw), min(dst.shape[0], y + rh)
        if dx0 < dx1 and dy0 < dy1:
            dst[dy0:dy1, dx0:dx1] = rc[dy0 - y : dy1 - y, dx0 - x : dx1 - x]

    def _to_screen(self, r, ix, iy):
        L = self.layout[r]
        return (L["sx"] + (ix - L["cx0"]) * L["scale"], L["sy"] + (iy - L["cy0"]) * L["scale"])

    def _disp_f(self, f):
        for r in self._order:
            L = self.layout.get(r)
            if not L or not L["gaps"]:
                continue
            pos = L["lo"] + f * L["ext"]
            ins = [g for g in L["gaps"] if g["lo"] <= pos <= g["hi"]]
            g = ins[0] if ins else min(L["gaps"], key=lambda gg: abs(gg["center"] - pos))
            return _clip01((g["center"] - L["lo"]) / L["ext"])
        return f

    def _role_cuts(self, r):
        L = self.layout[r]
        out = []
        for f in self.cuts:
            pos = L["lo"] + f * L["ext"]
            ins = [g for g in L["gaps"] if g["lo"] <= pos <= g["hi"]]
            if ins:
                out.append(ins[0]["center"])
            elif L["gaps"]:
                g = min(L["gaps"], key=lambda gg: abs(gg["center"] - pos))
                if abs(g["center"] - pos) <= 1.5 * self.mh:
                    out.append(g["center"])
        uniq = []
        for v in sorted(out):
            if not uniq or abs(v - uniq[-1]) > 2.0:
                uniq.append(v)
        return uniq

    def _parts(self, r):
        cuts = self._role_cuts(r)
        gl = self.layout[r]["block"]["glyphs"]
        return split_glyphs(gl, self.axis.get(), cuts) if cuts else [gl]

    def _evt(self, e):
        return e.y if self.axis.get() == "y" else e.x

    def _nearest(self, p):
        best, bd = None, 1e9
        for i, f in enumerate(self.cuts):
            d = abs(self._s0 + self._disp_f(f) * self._lbox - p)
            if d < bd:
                best, bd = i, d
        return best, bd

    def _on_down(self, e):
        if not self.layout:
            return
        p = self._evt(e)
        i, d = self._nearest(p)
        if i is not None and d <= 7:
            self._drag = i
            return
        f = _clip01((p - self._s0) / max(1e-6, self._lbox))
        if all(abs(f - g) > 0.015 for g in self.cuts):
            self.cuts.append(f)
            self._drag = len(self.cuts) - 1
        self._redraw()

    def _on_motion(self, e):
        if self._drag is not None:
            self.cuts[self._drag] = _clip01((self._evt(e) - self._s0) / max(1e-6, self._lbox))
            self._redraw()

    def _on_up(self, _):
        self._drag = None
        uniq = []
        for f in sorted(self.cuts):
            if not uniq or abs(f - uniq[-1]) > 0.015:
                uniq.append(f)
        self.cuts = uniq
        self._redraw()

    def _on_remove(self, e):
        if not self.layout:
            return
        i, d = self._nearest(self._evt(e))
        if i is not None and d <= 9:
            self.cuts.pop(i)
            self._redraw()

    def _redraw(self):
        if not self.layout:
            return
        c = self.canvas
        c.delete("all")
        c.create_image(0, 0, anchor="nw", image=self._base)
        ok, counts = False, []
        for r, L in self.layout.items():
            for g in L["block"]["glyphs"]:
                x0, y0 = self._to_screen(r, g["x"], g["y"])
                x1, y1 = self._to_screen(r, g["x"] + g["w"], g["y"] + g["h"])
                c.create_rectangle(x0, y0, x1, y1, outline="#5a5a5a")
            parts = self._parts(r)
            ok = ok or len(parts) >= 2
            counts.append(f"{r}: {len(parts)}")
            for n, gs in enumerate(parts, 1):
                sx0, sy0 = self._to_screen(r, min(g["x"] for g in gs), min(g["y"] for g in gs))
                sx1, sy1 = self._to_screen(r, max(g["x"] + g["w"] for g in gs), max(g["y"] + g["h"] for g in gs))
                c.create_rectangle(sx0, sy0, sx1, sy1, outline="#00e5ff", width=2)
                c.create_text(sx0 + 3, sy0 + 2, anchor="nw", text=str(n), fill="#00e5ff")
            lx, ly = self._to_screen(r, L["cx0"], L["cy0"])
            c.create_text(max(2, lx) + 2, max(2, ly) + 2, anchor="nw", text=r, fill="#a0a0a0")
        w, h = c.winfo_width(), c.winfo_height()
        for f in self.cuts:
            p = self._s0 + self._disp_f(f) * self._lbox
            if self.axis.get() == "y":
                c.create_line(0, p, w, p, fill="#ffd400", width=2)
                c.create_oval(w / 2 - 5, p - 5, w / 2 + 5, p + 5, fill="#ffd400", outline="")
            else:
                c.create_line(p, 0, p, h, fill="#ffd400", width=2)
                c.create_oval(p - 5, h / 2 - 5, p + 5, h / 2 + 5, fill="#ffd400", outline="")
        self.info.config(text="→ " + ",  ".join(counts))
        self.ok.config(state="normal" if ok else "disabled")

    def _apply(self):
        ops, primary = [], None
        for r in self._order:
            cuts = self._role_cuts(r)
            b = self.candidates[r][0]
            if not cuts or len(split_glyphs(b["glyphs"], self.axis.get(), cuts)) < 2:
                continue
            ops.append(dict(role=r, kind="split", axis=self.axis.get(), cuts=[float(x) for x in cuts], **_spec(b)))
            if primary is None:
                primary = (b, cuts)
        if not ops:
            return
        b, cuts = primary
        first = split_glyphs(b["glyphs"], self.axis.get(), cuts)[0]
        pt = (sum(g["cx"] for g in first) / len(first), sum(g["cy"] for g in first) / len(first))
        cb = self.on_apply
        self.destroy()
        cb(ops, pt)


# ==========================================================================
#  Box editor
# ==========================================================================
class BoxEditor(tk.Toplevel):
    def __init__(self, app, actions, on_done):
        super().__init__(app)
        self.app = app
        self.on_done = on_done
        self.actions = [dict(label=a["label"], ops=list(a["ops"]), links=list(a["links"])) for a in actions]
        self.title("Edit text boxes")
        self.transient(app)
        self.grab_set()
        self.minsize(900, 560)
        self.geometry("1180x720")

        # (bgr, alpha) pairs, so re-analysis keeps the alpha channel
        if app._imgs is None:
            app._imgs = (load_rgba(app.t_path), load_rgba(app.a_path))
        self.srcs = (app._imgs[0], app._imgs[1])
        self.imgs = {}  # display images, filled by _recompute()
        self.result = None

        self.tool = tk.StringVar(value="select")
        self.mirror = tk.BooleanVar(value=True)
        self.sel_box = None
        self.gsel = {"template": set(), "app": set()}
        self.gsel_anchor = {"template": None, "app": None}
        self.link_pending = None
        self.active_role = "template"
        self.zoom = None
        self.rubber = {}
        self._user_zoom = False
        self._cfg_job = None
        self._base = {}

        bar = ttk.Frame(self, padding=(8, 6))
        bar.pack(fill="x")
        ttk.Label(bar, text="Tool:").pack(side="left")
        for name, val in (("Select", "select"), ("New box", "box"), ("Link", "link")):
            ttk.Radiobutton(bar, text=name, value=val, variable=self.tool, command=self._on_tool).pack(side="left")
        ttk.Checkbutton(bar, text="Mirror edits to both images", variable=self.mirror).pack(side="left", padx=(10, 14))
        ttk.Button(bar, text="Delete box", command=self.delete_box).pack(side="left")
        ttk.Button(bar, text="Split box…", command=self.split_box).pack(side="left", padx=3)
        ttk.Button(bar, text="Create box", command=self.create_box).pack(side="left")
        ttk.Button(bar, text="Unlink", command=self.unlink_box).pack(side="left", padx=3)
        ttk.Button(bar, text="Undo", command=self.undo).pack(side="left", padx=(12, 0))
        ttk.Button(bar, text="Reset to auto", command=self.reset).pack(side="left", padx=3)
        ttk.Button(bar, text="Apply & Close", command=self.apply).pack(side="right")
        ttk.Button(bar, text="Cancel", command=self.destroy).pack(side="right", padx=4)
        for z, lbl in (("in", "＋"), ("out", "－"), ("fit", "Fit")):
            ttk.Button(bar, text=lbl, width=4 if z != "fit" else 5, command=lambda zz=z: self._zoom(zz)).pack(
                side="right"
            )

        pane = ttk.PanedWindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=6, pady=(0, 4))
        self.frames, self.canv = {}, {}
        for r in ("template", "app"):
            f = ttk.Frame(pane)
            pane.add(f, weight=1)
            ttk.Label(f, text=r.upper()).pack(anchor="w")
            c = tk.Canvas(f, background="#202020", highlightthickness=0)
            c.pack(fill="both", expand=True)
            c.bind("<ButtonPress-1>", lambda e, rr=r: self._press(rr, e))
            c.bind("<B1-Motion>", lambda e, rr=r: self._drag(rr, e))
            c.bind("<ButtonRelease-1>", lambda e, rr=r: self._release(rr, e))
            c.bind("<MouseWheel>", lambda e: self._wheel(e))
            c.bind("<Button-4>", lambda e: self._scroll(-1))
            c.bind("<Button-5>", lambda e: self._scroll(1))
            self.frames[r], self.canv[r] = f, c
        self.canv["template"].bind("<Configure>", self._on_configure)

        self.status = ttk.Label(self, text="", anchor="w", padding=4)
        self.status.pack(fill="x")
        self.bind("<Escape>", lambda e: self._clear_gsel())
        self.bind("<Delete>", lambda e: self.delete_box())
        self.after(30, self._init_view)

    # ----- lifecycle -----
    def _init_view(self):
        self._recompute()
        self._zoom("fit")

    def _on_configure(self, e):
        if e.width <= 60 or self._user_zoom or self.result is None:
            return
        if self._cfg_job:
            self.after_cancel(self._cfg_job)
        self._cfg_job = self.after(80, lambda: self._zoom("fit"))

    def _recompute(self):
        try:
            self.result = analyze_images(self.srcs[0], self.srcs[1], self.app.settings, self.actions)
        except Exception as exc:
            messagebox.showerror("Edit failed", str(exc), parent=self)
            if self.result is None:
                self.destroy()
            return
        self.imgs = {"template": self.result.t_bgr, "app": self.result.a_bgr}
        self.sel_box = None
        self.link_pending = None
        if self.zoom is not None:
            self._rebuild_base()
        self._redraw()

    def _rebuild_base(self):
        if not self.imgs or self.zoom is None:
            return
        self._base = {r: ImageTk.PhotoImage(_bgr2pil(_resize(self.imgs[r], self.zoom))) for r in ("template", "app")}

    def _zoom(self, how):
        if not self.imgs:
            return
        W = self.imgs["template"].shape[1]
        if how == "fit":
            cw = max(40, self.canv["template"].winfo_width())
            self.zoom = max(0.03, min(12.0, cw / W))
            self._user_zoom = False
        elif how == "in":
            self.zoom = min(16.0, (self.zoom or 1.0) * 1.25)
            self._user_zoom = True
        else:
            self.zoom = max(0.03, (self.zoom or 1.0) / 1.25)
            self._user_zoom = True
        self._rebuild_base()
        self._redraw()

    def _wheel(self, e):
        self._zoom("in" if e.delta > 0 else "out")

    def _scroll(self, d):
        for c in self.canv.values():
            c.yview_scroll(d, "units")

    # ----- model -----
    def _blocks(self, r):
        return self.result.t_blocks if r == "template" else self.result.a_blocks

    def _pool(self, r):
        return self.result.t_order if r == "template" else self.result.a_order

    def _mh(self, r):
        return self.result.t_mh if r == "template" else self.result.a_mh

    def _other(self, r):
        return "app" if r == "template" else "template"

    def _pair_index(self, role, idx):
        ri = 0 if role == "template" else 1
        for k, p in enumerate(self.result.pairs):
            if p[ri] == idx:
                return k
        return None

    def _push(self, label, ops=None, links=None):
        self.actions.append(dict(label=label, ops=ops or [], links=links or []))
        self._recompute()

    # ----- tool actions -----
    def _on_tool(self):
        self._clear_gsel(False)
        self.link_pending = None
        self._redraw()

    def delete_box(self):
        if not self.sel_box or self.result is None:
            return
        role, idx = self.sel_box
        b = self._blocks(role)[idx]
        bb = (b["x"], b["y"], b["w"], b["h"])
        ops = [dict(role=role, kind="delete", **_spec(b))]
        if self.mirror.get():
            ob = max(
                self._blocks(self._other(role)),
                key=lambda x: _iou_box(bb, (x["x"], x["y"], x["w"], x["h"])),
                default=None,
            )
            if ob and _iou_box(bb, (ob["x"], ob["y"], ob["w"], ob["h"])) > 0.25:
                ops.append(dict(role=self._other(role), kind="delete", **_spec(ob)))
        self._push("delete box", ops, [])

    def split_box(self):
        if not self.sel_box:
            messagebox.showinfo("Split", "Select a box first.", parent=self)
            return
        role, idx = self.sel_box
        b = self._blocks(role)[idx]
        cands = {}
        if b.get("glyphs") and len(b["glyphs"]) >= 2:
            cands[role] = (b, self._mh(role))
        pk = self._pair_index(role, idx)
        if pk is not None and self.mirror.get():
            other = self._other(role)
            oi = self.result.pairs[pk][1 if other == "app" else 0]
            ob = self._blocks(other)[oi]
            if ob.get("glyphs") and len(ob["glyphs"]) >= 2:
                cands[other] = (ob, self._mh(other))
        if not cands:
            messagebox.showinfo("Split", "Box has fewer than 2 glyphs.", parent=self)
            return
        SplitDialog(self, self.imgs, cands, lambda ops, pt: self._push("split box", ops, []))

    def create_box(self):
        if self.result is None:
            return
        role = self.active_role
        sel = sorted(self.gsel[role])
        if not sel:
            messagebox.showinfo(
                "Create box", "Select glyphs first (click, drag a box, " "or shift-click a run).", parent=self
            )
            return
        pool = self._pool(role)
        gs = [pool[i] for i in sel]
        mh = self._mh(role)
        ops = [dict(role=role, kind="create", glyphs=[glyph_spec(g) for g in gs])]
        links = []
        x0 = min(g["x"] for g in gs) - 0.5 * mh
        y0 = min(g["y"] for g in gs) - 0.5 * mh
        x1 = max(g["x"] + g["w"] for g in gs) + 0.5 * mh
        y1 = max(g["y"] + g["h"] for g in gs) + 0.5 * mh
        t_spec = dict(anchor=((x0 + x1) / 2, (y0 + y1) / 2), bbox=(int(x0), int(y0), int(x1 - x0), int(y1 - y0)))
        if self.mirror.get():
            other = self._other(role)
            og = [g for g in self._pool(other) if x0 <= g["cx"] <= x1 and y0 <= g["cy"] <= y1]
            if og:
                ops.append(dict(role=other, kind="create", glyphs=[glyph_spec(g) for g in og]))
                ox0 = min(g["x"] for g in og)
                oy0 = min(g["y"] for g in og)
                ox1 = max(g["x"] + g["w"] for g in og)
                oy1 = max(g["y"] + g["h"] for g in og)
                o_spec = dict(anchor=((ox0 + ox1) / 2, (oy0 + oy1) / 2), bbox=(ox0, oy0, ox1 - ox0, oy1 - oy0))
                links = [{"t": t_spec if role == "template" else o_spec, "a": o_spec if role == "template" else t_spec}]
        self._clear_gsel(False)
        self._push("create box", ops, links)

    def unlink_box(self):
        if not self.sel_box or self.result is None:
            return
        role, idx = self.sel_box
        k = self._pair_index(role, idx)
        if k is None or k not in self.result.linked_pairs:
            messagebox.showinfo("Unlink", "Selected box is not part of a manual link.", parent=self)
            return
        ti, aj = self.result.pairs[k]
        removed = 0
        for act in self.actions:
            keep = []
            for L in act["links"]:
                if find_target(self.result.t_blocks, L["t"]) == ti and find_target(self.result.a_blocks, L["a"]) == aj:
                    removed += 1
                else:
                    keep.append(L)
            act["links"] = keep
        if removed:
            self._recompute()

    def undo(self):
        if self.actions:
            self.actions.pop()
            self._recompute()

    def reset(self):
        if self.actions and messagebox.askyesno("Reset", "Discard all manual edits?", parent=self):
            self.actions = []
            self._recompute()

    def apply(self):
        out = [dict(label=a["label"], ops=a["ops"], links=a["links"]) for a in self.actions]
        cb = self.on_done
        self.destroy()
        cb(out)

    def _clear_gsel(self, redraw=True):
        for r in self.gsel:
            self.gsel[r].clear()
            self.gsel_anchor[r] = None
        if redraw and self.result is not None:
            self._redraw()

    # ----- canvas interaction -----
    def _img_xy(self, r, e):
        c = self.canv[r]
        return c.canvasx(e.x) / self.zoom, c.canvasy(e.y) / self.zoom

    def _glyph_at(self, r, ix, iy):
        for i, g in enumerate(self._pool(r)):
            if g["x"] <= ix <= g["x"] + g["w"] and g["y"] <= iy <= g["y"] + g["h"]:
                return i
        return None

    def _block_at(self, r, ix, iy):
        hit, blocks = None, self._blocks(r)
        for i, b in enumerate(blocks):
            if b["x"] <= ix <= b["x"] + b["w"] and b["y"] <= iy <= b["y"] + b["h"]:
                if hit is None or b["w"] * b["h"] < blocks[hit]["w"] * blocks[hit]["h"]:
                    hit = i
        return hit

    def _press(self, r, e):
        if self.result is None or self.zoom is None:
            return
        self.active_role = r
        ix, iy = self._img_xy(r, e)
        tool = self.tool.get()
        if tool == "select":
            bi = self._block_at(r, ix, iy)
            self.sel_box = (r, bi) if bi is not None else None
            self._redraw()
        elif tool == "link":
            bi = self._block_at(r, ix, iy)
            if bi is None:
                return
            if self.link_pending and self.link_pending[0] != r:
                pr, pi = self.link_pending
                tb = self._blocks("template")[pi if pr == "template" else bi]
                ab = self._blocks("app")[bi if r == "app" else pi]
                self.link_pending = None
                self._push("link boxes", links=[{"t": _spec(tb), "a": _spec(ab)}])
            else:
                self.link_pending = (r, bi)
                self.sel_box = (r, bi)
                self._redraw()
        elif tool == "box":
            gi = self._glyph_at(r, ix, iy)
            if e.state & 0x0001 and gi is not None and self.gsel_anchor[r] is not None:
                a, b = sorted((self.gsel_anchor[r], gi))
                self.gsel[r].update(range(a, b + 1))
                self._redraw()
            elif gi is not None and not (e.state & 0x0004):
                self.gsel[r].symmetric_difference_update({gi})
                self.gsel_anchor[r] = gi
                self._redraw()
            else:
                self.rubber[r] = (ix, iy, ix, iy, bool(e.state & 0x0004))

    def _drag(self, r, e):
        if self.tool.get() == "box" and r in self.rubber:
            x0, y0, _, _, sub = self.rubber[r]
            ix, iy = self._img_xy(r, e)
            self.rubber[r] = (x0, y0, ix, iy, sub)
            self._redraw()

    def _release(self, r, e):
        if self.tool.get() == "box" and r in self.rubber:
            x0, y0, x1, y1, sub = self.rubber.pop(r)
            x0, x1 = sorted((x0, x1))
            y0, y1 = sorted((y0, y1))
            if abs(x1 - x0) >= 3 or abs(y1 - y0) >= 3:
                for i, g in enumerate(self._pool(r)):
                    if x0 <= g["cx"] <= x1 and y0 <= g["cy"] <= y1:
                        (self.gsel[r].discard if sub else self.gsel[r].add)(i)
                if self.gsel[r] and not sub:
                    self.gsel_anchor[r] = min(self.gsel[r])
            self._redraw()

    # ----- drawing -----
    def _redraw(self):
        if self.result is None or self.zoom is None or not self._base:
            return
        Z = self.zoom
        linked_sorted = sorted(self.result.linked_pairs)
        for r in ("template", "app"):
            c = self.canv[r]
            c.delete("all")
            c.create_image(0, 0, anchor="nw", image=self._base[r])
            c.configure(scrollregion=(0, 0, self._base[r].width(), self._base[r].height()))
            if self.tool.get() == "box":
                for g in self._pool(r):
                    c.create_rectangle(
                        g["x"] * Z, g["y"] * Z, (g["x"] + g["w"]) * Z, (g["y"] + g["h"]) * Z, outline="#4d4d4d"
                    )
                for i in self.gsel[r]:
                    g = self._pool(r)[i]
                    c.create_rectangle(
                        g["x"] * Z,
                        g["y"] * Z,
                        (g["x"] + g["w"]) * Z,
                        (g["y"] + g["h"]) * Z,
                        outline="#ffd400",
                        width=2,
                        fill="#ffd400",
                        stipple="gray25",
                    )
            for i, b in enumerate(self._blocks(r)):
                k = self._pair_index(r, i)
                linked = k is not None and k in self.result.linked_pairs
                col = "#39d353" if linked else ("#ff8c00" if b.get("manual") else "#9a9a9a")
                wid = 2 if (b.get("manual") or linked) else 1
                if self.sel_box == (r, i) or self.link_pending == (r, i):
                    col, wid = "#ff3b30", 3
                c.create_rectangle(
                    b["x"] * Z, b["y"] * Z, (b["x"] + b["w"]) * Z, (b["y"] + b["h"]) * Z, outline=col, width=wid
                )
                tag = (
                    (f"L{linked_sorted.index(k) + 1} " if linked else "")
                    + (f"#{k + 1}" if k is not None else "·")
                    + (" M" if b.get("manual") else "")
                )
                c.create_text(b["x"] * Z + 2, max(0, b["y"] * Z - 12), anchor="nw", text=tag, fill=col)
            if r in self.rubber:
                x0, y0, x1, y1, _ = self.rubber[r]
                c.create_rectangle(x0 * Z, y0 * Z, x1 * Z, y1 * Z, outline="#ffd400", dash=(4, 3))
        r = self.result
        nman = sum(1 for b in r.t_blocks + r.a_blocks if b.get("manual"))
        hint = {
            "select": "click a box to select it",
            "box": "click / drag a box / shift-click a run, then 'Create box'",
            "link": "click a box on each image to link them",
        }[self.tool.get()]
        sel = f"   selected: {self.sel_box[0]} box" if self.sel_box else ""
        self.status.config(
            text=f"{len(r.t_blocks)} template / {len(r.a_blocks)} app boxes · "
            f"{len(r.pairs)} matched ({len(r.linked_pairs)} manual links) · "
            f"{nman} manual boxes · {len(self.actions)} edits{sel}  ,   {hint}"
        )


# ==========================================================================
#  Main review window
# ==========================================================================
class App(tk.Tk):
    def __init__(self, t_path=None, a_path=None):
        super().__init__()
        self.title("Slide Template vs. App, Text Diff Viewer")
        self.geometry("1460x940")
        self.settings = Settings()
        self.result = None
        self.entries = []
        self.edit_actions = []
        self.t_path, self.a_path = t_path, a_path
        self._imgs = None
        self.scale = None
        self._photo = None
        self._build_top()
        self._build_body()
        self._bind_keys()
        self._refresh_paths()
        if t_path and a_path:
            self.after(100, self.analyze)

    def _build_top(self):
        bar = ttk.Frame(self, padding=6)
        bar.pack(side="top", fill="x")
        ttk.Button(bar, text="Open Template…", command=lambda: self._pick("t_path")).pack(side="left")
        ttk.Button(bar, text="Open App…", command=lambda: self._pick("a_path")).pack(side="left", padx=(4, 12))
        self.lbl_t = ttk.Label(bar, text="template:,", width=26)
        self.lbl_t.pack(side="left")
        self.lbl_a = ttk.Label(bar, text="app:,", width=26)
        self.lbl_a.pack(side="left", padx=(4, 12))
        ttk.Label(bar, text="text colour R,G,B:").pack(side="left")
        self.e_color = ttk.Entry(bar, width=11)
        self.e_color.pack(side="left", padx=(2, 8))
        self.e_xtol = self._tol(bar, "x±", self.settings.x_tol)
        self.e_ytol = self._tol(bar, "y±", self.settings.y_tol)
        self.e_ftol = self._tol(bar, "font±", self.settings.font_tol)
        for role in ("template", "app"):
            ttk.Label(bar, text=f"{role} alpha:").pack(side="left")
            var = tk.StringVar(value="auto")
            setattr(self, f"alpha_{role}", var)
            ttk.OptionMenu(bar, var, "auto", "auto", "text", "shape").pack(side="left", padx=(0, 8))
        ttk.Button(bar, text="Analyze", command=self.analyze).pack(side="left", padx=8)

    def _tol(self, parent, label, value):
        ttk.Label(parent, text=label).pack(side="left")
        e = ttk.Entry(parent, width=5)
        e.insert(0, str(value))
        e.pack(side="left", padx=(2, 8))
        return e

    def _build_body(self):
        body = ttk.Frame(self)
        body.pack(side="top", fill="both", expand=True)
        side = ttk.Frame(body, padding=6, width=312)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        sens = ttk.LabelFrame(side, text="Detection sensitivity", padding=6)
        sens.pack(fill="x")
        self.sens_var = tk.IntVar(value=self.settings.sensitivity)
        self.sens_lbl = ttk.Label(sens, text=self._sens_text())
        self.sens_lbl.pack(anchor="w")
        self.sens_scale = ttk.Scale(
            sens,
            from_=1,
            to=100,
            orient="horizontal",
            variable=self.sens_var,
            command=lambda *_: self.sens_lbl.config(text=self._sens_text()),
        )
        self.sens_scale.pack(fill="x", pady=2)
        self.sens_scale.bind("<ButtonRelease-1>", lambda e: self.analyze())
        row = ttk.Frame(sens)
        row.pack(fill="x")
        ttk.Button(row, text="strict", width=7, command=lambda: self._set_sens(15)).pack(side="left")
        ttk.Button(row, text="Re-analyze", command=self.analyze).pack(side="left", padx=4)
        ttk.Button(row, text="loose", width=7, command=lambda: self._set_sens(85)).pack(side="left")

        ed = ttk.LabelFrame(side, text="Boxes & matching", padding=6)
        ed.pack(fill="x", pady=(8, 0))
        ttk.Button(ed, text="Edit boxes…", command=self.open_editor).pack(fill="x")
        ttk.Button(ed, text="Reset to auto", command=self.reset_edits).pack(fill="x", pady=(4, 0))
        self.edit_lbl = ttk.Label(ed, text="0 edits", foreground="#888")
        self.edit_lbl.pack(anchor="w", pady=(4, 0))

        ttk.Label(side, text="Differences", padding=(0, 8, 0, 0)).pack(anchor="w")
        lf = ttk.Frame(side)
        lf.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(lf, activestyle="dotbox", exportselection=False)
        sb = ttk.Scrollbar(lf, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=sb.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.listbox.bind("<<ListboxSelect>>", lambda e: self.render())

        opt = ttk.Frame(side, padding=(0, 8))
        opt.pack(fill="x")
        self.view_mode = tk.StringVar(value="side")
        ttk.Radiobutton(opt, text="Side by side", value="side", variable=self.view_mode, command=self.render).pack(
            anchor="w"
        )
        ttk.Radiobutton(
            opt, text="Overlay (one image)", value="overlay", variable=self.view_mode, command=self.render
        ).pack(anchor="w")
        self.isolate = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt, text="Isolate (hide everything else)", variable=self.isolate, command=self.render).pack(
            anchor="w", pady=(6, 0)
        )
        zf = ttk.Frame(side)
        zf.pack(fill="x")
        ttk.Button(zf, text="–", width=3, command=lambda: self._zoom(1 / 1.25)).pack(side="left")
        ttk.Button(zf, text="Fit", command=self._fit).pack(side="left", padx=4)
        ttk.Button(zf, text="+", width=3, command=lambda: self._zoom(1.25)).pack(side="left")

        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True)
        cf = ttk.Frame(right)
        cf.pack(side="top", fill="both", expand=True)
        self.canvas = tk.Canvas(cf, background="#202020", highlightthickness=0)
        hb = ttk.Scrollbar(cf, orient="horizontal", command=self.canvas.xview)
        vb = ttk.Scrollbar(cf, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hb.set, yscrollcommand=vb.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vb.grid(row=0, column=1, sticky="ns")
        hb.grid(row=1, column=0, sticky="ew")
        cf.rowconfigure(0, weight=1)
        cf.columnconfigure(0, weight=1)
        self.canvas.bind("<MouseWheel>", lambda e: self._zoom(1.1 if e.delta > 0 else 1 / 1.1))
        self.canvas.bind("<Button-4>", lambda e: self._zoom(1.1))
        self.canvas.bind("<Button-5>", lambda e: self._zoom(1 / 1.1))
        self.details = tk.Text(
            right, height=9, wrap="none", background="#111", foreground="#ddd", font=("TkFixedFont", 9)
        )
        self.details.pack(side="bottom", fill="x")
        self.status = ttk.Label(self, text="Open a template and an app image, then Analyze.", anchor="w", padding=4)
        self.status.pack(side="bottom", fill="x")

    def _bind_keys(self):
        self.bind("<Down>", lambda e: self._move(1))
        self.bind("<Up>", lambda e: self._move(-1))
        self.bind("o", lambda e: self._toggle_mode())
        self.bind("i", lambda e: (self.isolate.set(not self.isolate.get()), self.render()))
        self.bind("e", lambda e: self.open_editor())

    # ----- helpers -----
    def _sens_text(self):
        v = int(float(self.sens_var.get()))
        tag = "strict" if v < 34 else ("balanced" if v < 67 else "loose")
        return f"{v}/100  ({tag})"

    def _set_sens(self, v):
        self.sens_var.set(v)
        self.sens_lbl.config(text=self._sens_text())
        self.analyze()

    def _pick(self, attr):
        path = filedialog.askopenfilename(
            title=f"Select {'template' if attr == 't_path' else 'app'} image",
            filetypes=[("Images", "*.png *.tif *.tiff *.bmp *.jpg *.jpeg *.webp"), ("All files", "*.*")],
        )
        if path:
            setattr(self, attr, path)
            self._imgs = None
            self.edit_actions = []
            self._refresh_paths()
            if self.t_path and self.a_path:
                self.analyze()

    def _refresh_paths(self):
        self.lbl_t.config(text="template: " + (os.path.basename(self.t_path) if self.t_path else "—"))
        self.lbl_a.config(text="app: " + (os.path.basename(self.a_path) if self.a_path else "—"))

    def _entry_blocks(self, e):
        r = self.result
        if e[0] == "pair":
            i, j = r.pairs[e[1]]
            return [("template", r.t_blocks[i]), ("app", r.a_blocks[j])]
        if e[0] == "missing":
            return [("template", r.t_blocks[e[1]])]
        if e[0] == "extra":
            return [("app", r.a_blocks[e[1]])]
        return []

    def _remember(self):
        sel = self.listbox.curselection()
        if not sel or not self.result:
            return None
        e = self.entries[sel[0]]
        if e[0] == "overview":
            return ("overview",)
        _, b = self._entry_blocks(e)[0]
        return (e[0], b["cx"], b["cy"])

    def _restore(self, token, point):
        if point is not None:
            best, bd = None, 1e9
            for n, e in enumerate(self.entries):
                for _, b in self._entry_blocks(e):
                    d = math.hypot(b["cx"] - point[0], b["cy"] - point[1])
                    if d < bd:
                        best, bd = n, d
            if best is not None:
                return best
        if not token:
            return None
        if token[0] == "overview":
            return 0
        kind, cx, cy = token
        best, bd = None, 1e9
        for n, e in enumerate(self.entries):
            if e[0] != kind:
                continue
            _, b = self._entry_blocks(e)[0]
            d = math.hypot(b["cx"] - cx, b["cy"] - cy)
            if d < bd:
                best, bd = n, d
        return best if (best is not None and bd < 40) else None

    # ----- analysis -----
    def analyze(self, select_point=None):
        if not (self.t_path and self.a_path):
            messagebox.showinfo("Pick images", "Select both a template and an app image.")
            return
        token = self._remember()
        s = self.settings
        try:
            s.text_color = parse_color(self.e_color.get())
            s.x_tol = float(self.e_xtol.get())
            s.y_tol = float(self.e_ytol.get())
            s.font_tol = float(self.e_ftol.get())
            s.sensitivity = int(float(self.sens_var.get()))
            s.template_alpha_mode = self.alpha_template.get()
            s.app_alpha_mode = self.alpha_app.get()
        except ValueError as exc:
            messagebox.showerror("Bad setting", str(exc))
            return
        try:
            if self._imgs is None:
                self._imgs = (load_rgba(self.t_path), load_rgba(self.a_path))
            self.result = analyze_images(self._imgs[0], self._imgs[1], s, self.edit_actions)
        except Exception as exc:
            messagebox.showerror("Analysis failed", str(exc))
            return
        self._populate(token, select_point)

    def _populate(self, token=None, point=None):
        r = self.result
        self.entries, rows, colors = [("overview",)], ["▣  Overview (all boxes)"], [None]
        for k, (i, j) in enumerate(r.pairs):
            res = r.analyses[k]
            ok = (
                abs(res["x_off"]) <= r.settings.x_tol
                and abs(res["y_off"]) <= r.settings.y_tol
                and abs(res["font_ratio"] - 1.0) <= r.settings.font_tol
            )
            cmin = min(r.t_blocks[i]["confidence"], r.a_blocks[j]["confidence"])
            flag = (
                "L"
                if k in r.linked_pairs
                else ("M" if (r.t_blocks[i].get("manual") or r.a_blocks[j].get("manual")) else " ")
            )
            self.entries.append(("pair", k, ok))
            rows.append(
                f"{flag}{'OK ' if ok else 'OFF'} #{k + 1}  X{res['x_off']:+.0f} "
                f"Y{res['y_off']:+.0f} f{res['font_ratio'] * 100:.0f}%  c{cmin:.2f}"
            )
            colors.append("#4c9a4c" if ok else "#d9534f")
        for i in r.unmatched_t:
            self.entries.append(("missing", i))
            rows.append(f" !! missing in app (tmpl {i + 1}, " f"c{r.t_blocks[i]['confidence']:.2f})")
            colors.append("#d9534f")
        for j in r.unmatched_a:
            self.entries.append(("extra", j))
            rows.append(f" !! extra in app (app {j + 1}, " f"c{r.a_blocks[j]['confidence']:.2f})")
            colors.append("#d9534f")
        self.listbox.delete(0, "end")
        for idx, (text, col) in enumerate(zip(rows, colors)):
            self.listbox.insert("end", text)
            if col:
                self.listbox.itemconfig(idx, foreground=col)
        sel = self._restore(token, point)
        if sel is None:
            sel = next(
                (
                    n
                    for n, e in enumerate(self.entries)
                    if e[0] in ("missing", "extra") or (e[0] == "pair" and not e[2])
                ),
                0,
            )
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(sel)
        self.listbox.see(sel)
        nman = sum(1 for b in r.t_blocks + r.a_blocks if b.get("manual"))
        self.edit_lbl.config(
            text=f"{len(self.edit_actions)} edit(s) · {nman} manual box(es) · " f"{len(r.linked_pairs)} manual link(s)"
        )
        n_off = sum(1 for e in self.entries if e[0] != "overview" and (e[0] != "pair" or not e[2]))
        self.status.config(
            text=f"sensitivity {r.settings.sensitivity}/100 "
            f"(cut-off {r.settings.conf_threshold:.2f})   ·   "
            f"{len(r.t_blocks)} template / {len(r.a_blocks)} app blocks, "
            f"{len(r.pairs)} matched, {n_off} with differences"
        )
        self._fit()

    # ----- editor hooks -----
    def open_editor(self):
        if self.result is None:
            messagebox.showinfo("Analyze first", "Run Analyze before editing boxes.")
            return
        BoxEditor(self, self.edit_actions, self._after_edit)

    def _after_edit(self, actions):
        self.edit_actions = actions
        self.analyze()

    def reset_edits(self):
        if self.edit_actions and messagebox.askyesno("Reset to auto", "Discard all manual box edits and links?"):
            self.edit_actions = []
            self.analyze()

    # ----- navigation / zoom -----
    def _move(self, delta):
        if not self.listbox.size():
            return
        cur = self.listbox.curselection()
        nxt = max(0, min(self.listbox.size() - 1, (cur[0] if cur else 0) + delta))
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(nxt)
        self.listbox.see(nxt)
        self.render()

    def _toggle_mode(self):
        self.view_mode.set("overlay" if self.view_mode.get() == "side" else "side")
        self.render()

    def _zoom(self, factor):
        if self.result is None:
            return
        self.scale = (self.scale or 1.0) * factor
        self.render()

    def _fit(self):
        self.scale = None
        self.render()

    # ----- draw -----
    def render(self):
        if self.result is None or not self.listbox.curselection():
            return
        entry = self.entries[self.listbox.curselection()[0]]
        aw = max(300, self.canvas.winfo_width())
        ah = max(300, self.canvas.winfo_height())
        mode = self.view_mode.get()
        try:
            if entry[0] == "overview":
                pil = render_overview(self.result, mode, aw, ah, self.scale)
                self._details_overview()
            elif entry[0] == "pair":
                pil = render_pair(self.result, entry[1], mode, self.isolate.get(), aw, ah, self.scale)
                self._details_pair(entry[1])
            else:
                which = "template" if entry[0] == "missing" else "app"
                pil = render_single(self.result, which, entry[1], aw, ah, self.scale)
                self._details_single(which, entry[1])
        except Exception as exc:
            messagebox.showerror("Render failed", str(exc))
            return
        self._photo = ImageTk.PhotoImage(pil)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._photo)
        self.canvas.configure(scrollregion=(0, 0, pil.width, pil.height))

    def _set_details(self, text):
        self.details.delete("1.0", "end")
        self.details.insert("1.0", text)

    @staticmethod
    def _conf_line(tag, b):
        p = b["score_parts"]
        return (
            f"  {tag:<8} {'[manual] ' if b.get('manual') else ''}"
            f"confidence {b['confidence']:.2f}  (contrast {p['contrast']:.2f}, "
            f"height {p['height']:.2f}, baseline {p['baseline']:.2f}, "
            f"count {p['count']:.2f}, fill {p['fill']:.2f}, "
            f"coverage {p['coverage']:.2f}) -> weakest: {min(p, key=p.get)}"
        )

    def _details_overview(self):
        r = self.result
        self._set_details(
            f"OVERVIEW   template blocks: {len(r.t_blocks)}   app blocks: {len(r.a_blocks)}"
            f"   matched: {len(r.pairs)} ({len(r.linked_pairs)} via manual links)\n"
            f"sensitivity {r.settings.sensitivity}/100 -> confidence cut-off "
            f"{r.settings.conf_threshold:.2f};  manual edits: {len(self.edit_actions)}\n"
            "cyan=template  magenta=app  orange=manual box  green=linked pair\n\n"
            + "\n".join(
                f"#{k:<2} X {r.analyses[k]['x_off']:+6.1f} "
                f"Y {r.analyses[k]['y_off']:+6.1f} "
                f"font {r.analyses[k]['font_ratio'] * 100:6.1f}%" + ("  [linked]" if k in r.linked_pairs else "")
                for k in range(len(r.pairs))
            )
        )

    def _details_pair(self, key):
        r = self.result
        i, j = r.pairs[key]
        t, a = r.t_blocks[i], r.a_blocks[j]
        res = r.analyses[key]
        fr = res["font_ratio"]
        self._set_details(
            f"COMPONENT #{key + 1}"
            + ("   [matched via a manual link]" if key in r.linked_pairs else "")
            + "\n"
            + self._conf_line("template", t)
            + "\n"
            + self._conf_line("app", a)
            + "\n"
            f"  X offset : {res['x_off']:+.1f} px  ({res['halign']}-aligned)   "
            f"left {res['dx']['left']:+.1f} | center {res['dx']['center']:+.1f} | "
            f"right {res['dx']['right']:+.1f}\n"
            f"  Y offset : {res['y_off']:+.1f} px  ({res['valign']}-aligned)   "
            f"top {res['dy']['top']:+.1f} | center {res['dy']['center']:+.1f} | "
            f"bottom {res['dy']['bottom']:+.1f}\n"
            f"  Font     : {fr * 100:.2f}% of template ({(fr - 1) * 100:+.1f}%)   "
            f"width ratio {res['width_ratio'] * 100:.1f}%\n"
            f"  FIX      : move X {-res['x_off']:+.1f} px, move Y {-res['y_off']:+.1f} px, "
            f"scale font {((1 / fr) - 1) * 100:+.1f}%"
        )

    def _details_single(self, which, idx):
        b = (self.result.t_blocks if which == "template" else self.result.a_blocks)[idx]
        kind = "MISSING IN APP" if which == "template" else "EXTRA IN APP"
        self._set_details(
            f"{kind}, no match found in the other image\n" + self._conf_line(which, b) + "\n"
            f"  box {b['x']},{b['y']}  {b['w']}x{b['h']}  glyph_h={b['glyph_h']:.1f}\n"
            f"  Use 'Edit boxes...' to delete it, merge it by linking, or rebuild it "
            f"from the glyphs you want."
        )


def main():
    t = sys.argv[1] if len(sys.argv) > 1 else None
    a = sys.argv[2] if len(sys.argv) > 2 else None
    App(t, a).mainloop()


if __name__ == "__main__":
    main()
