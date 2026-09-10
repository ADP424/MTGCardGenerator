# Contributing Assets

For people contributing frames, mana symbols, watermarks, set symbols, or fonts. You don't need to run any Python for most of this, but you do need to understand how the generator finds what you add. For code contributors, see [Contributing Code](CONTRIBUTING_CODE.md). For everything else, see the [main README](../README.md) and the [Reference](REFERENCE.md).

---

## Contents

1. [Do I need to touch Python?](#1-do-i-need-to-touch-python)
   - [Where assets live](#where-assets-live)
2. [Contributing frames](#2-contributing-frames)
   - [Does it need a new layout class?](#does-it-need-a-new-layout-class)
   - [Format](#format)
   - [Resolution](#resolution)
   - [Naming](#naming)
3. [Contributing mana symbols](#3-contributing-mana-symbols)
4. [Contributing set symbols, watermarks, and fonts](#4-contributing-set-symbols-watermarks-and-fonts)
   - [Set symbols](#set-symbols)
   - [Watermarks](#watermarks)
   - [Fonts](#fonts)
5. [Asset wish-list](#5-asset-wish-list)

---

## 1. Do I need to touch Python?

| Contribution | Python needed? |
|---|---|
| A new color or variant **inside an existing frame family** (e.g. another `regular/…` file), an overlay, a watermark, a set symbol | **No.** Drop the file in the right folder; it's found by path. |
| A new mana symbol or a font | **Two or three lines** of copy-paste in `src/constants.py` to register it ([§3](#3-contributing-mana-symbols), [§4](#fonts)). |
| A **new frame family** whose title bar, text box, or P/T plate is somewhere the existing layouts don't expect | **Yes, a new layout class** ([§2](#does-it-need-a-new-layout-class), [Contributing Code](CONTRIBUTING_CODE.md)). Without one, the frame is only usable as a `Regular` backdrop and text will land in the wrong places. |

### Where assets live

| Path | Contents |
|---|---|
| `images/frames/<family>/…/<color>.png` | Frame layers, referenced by path from the spreadsheet. |
| `images/frames/…/mask/*.png` | Masks. Only the alpha channel is used. |
| `images/mana_symbols/` | Mana, tap, energy, and other inline symbols. |
| `images/collector_info/set_symbols/{custom,official}/<set>/<rarity>.png` | Set symbols. `custom` is searched first. |
| `images/collector_info/watermarks/<name>.png` | Watermarks. |
| `images/art/overlay/<name>.png` | Full-card overlays (foil, etc.). |
| `images/other/` | Dividers, dice-table backgrounds. |
| `fonts/<family>/*.ttf` | Fonts. |

## 2. Contributing frames

### Does it need a new layout class?

**This is the single most important question.** A frame is just a picture; a layout class (`src/model/…`) is what knows where on that picture the title, type line, rules text, P/T, set symbol, and footer go. The generator ships one class per shape listed in [Reference §4](REFERENCE.md#4-frame-layouts), each with hard-coded pixel coordinates.

- If your frame keeps every element where an existing layout puts it, a recolor, a new texture, an alternate border for `regular/`, no class is needed. Drop the file in.
- If anything moves, a taller text box, a title bar in a new spot, an extra name plate, the frame **needs its own layout class**, or the text will render in the wrong place.

If you can write the class yourself, see [Adding a frame layout](CONTRIBUTING_CODE.md#3-adding-a-frame-layout). If not, submit the frame anyway, with pixel measurements of its title bar, type line, text box, P/T plate, and set symbol position; a code contributor can build the class from those. Either way, include a rendered test card so the fit can be checked.

### Format

RGBA PNG, transparent wherever nothing should draw. Don't bake in anything the code draws: text, set symbols, watermarks, collector info.

### Resolution

New frames should be **2010×2814** (portrait) or **2814×2010** (landscape). Every existing directory has a known native size recorded in `FRAME_DIRECTORY_BASE_SIZES` in `src/constants.py`, and the generator rescales per layer at render time. So:

- Adding files to an **existing** directory: match that directory's size.
- Adding a **new** directory at a non-standard size: add one entry to `FRAME_DIRECTORY_BASE_SIZES`. Don't resize the artwork, rescaling costs quality and is handled for you.
- Only if you absolutely must change the size of an existing directory's files (e.g. fixing a set of mismatched strays), `tools/resize_frames.py` does the bulk conversion.

### Naming

Follow the existing conventions so spreadsheets stay predictable:

- Color files: `white`, `blue`, `black`, `red`, `green`, `colorless`, `artifact`, `multicolor`, `land`, `vehicle`, `snow`.
- Sub-elements in sibling folders: `power_toughness/`, `legendary_crown/`, `holo/`, `margin/`, `enchantment/`, `land/`, `transform/{front,back}/`, `nickname/`, `extended/`, `textless/`.
- Masks in `mask/`: `top`, `bottom`, `left`, `right` for color splits, plus element masks like `frame`, `pinline`, `title`, `type`, `rules`, `border`.

Look at `images/frames/regular/` as the canonical example.

## 3. Contributing mana symbols

1. Add the PNG under `images/mana_symbols/` following the existing folder structure.
2. In `src/constants.py`, add a module-level `open_image(...)` constant next to the similar ones, then register it in `SYMBOL_PLACEHOLDER_KEY` under **every** spelling you want to accept (e.g. both `"w/n"` and `"n/w"`). The existing entries show the pattern, including when to use `HYBRID_MANA_SYMBOL_SIZE_MULT`, `recolorable=True` (flat glyphs that take the text color), and `resample=PIXEL_SYMBOL_RESAMPLE` (pixel art).

Showcase styles with their own symbol art get their own dict (`PIXEL_SYMBOL_PLACEHOLDER_KEY` etc.) assigned to the layout's `MANA_SYMBOL_KEY`. Those dicts don't need to be complete, missing symbols fall back to the standard set.

## 4. Contributing set symbols, watermarks, and fonts

### Set symbols

`images/collector_info/set_symbols/custom/<set name, lowercased, spaces→underscores>/<rarity>.png`. Rarity files are `common`, `uncommon`, `rare`, `mythic`, `lato`; `token` and `land` rarities use `common`.

### Watermarks

A solid silhouette at `images/collector_info/watermarks/<name>.png`. Color and transparency are applied at render time.

### Fonts

Add the TTF under `fonts/<family>/`, then add a path constant in `src/constants.py` beside the others. Display fonts are referenced by a layout's `TITLE_FONT` / `RULES_TEXT_FONT` etc.; script-fallback fonts go in `DIRECTIVE_FONTS`, which makes a new `{tag}` available everywhere.

## 5. Asset wish-list

Good, self-contained contributions:

- **Fix the mismatched stray files** flagged with `# TODO` comments in `FRAME_DIRECTORY_BASE_SIZES`.
- **Fill out the showcase symbol sets**, Future Shifted, Playtest, Pixel, and Japanese Mystical Archive are all missing pieces.
- **Set symbols** for more rarities and sets.
- Clean `.kra` working files and `.png~` backups out of the asset tree, or move them to a `source/` folder.
