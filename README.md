# MTG Card Generator

Turns a spreadsheet of Magic: the Gathering card data into finished, print-resolution card images, one PNG per row. Built as the rendering stage of a larger proxy-printing workflow.

---

## Contents

1. [What this does](#1-what-this-does)
2. [Setup](#2-setup)
   - [Install](#install)
   - [Where things go](#where-things-go)
3. [Your first card](#3-your-first-card)
   - [Make a spreadsheet](#make-a-spreadsheet)
   - [Render it](#render-it)
4. [Filling in the spreadsheet](#4-filling-in-the-spreadsheet)
   - [Frame(s)](#frames)
   - [Frame Layout](#frame-layout)
   - [Rules Text](#rules-text)
   - [Multi-line cells](#multi-line-cells)
5. [Adding art](#5-adding-art)
6. [Everyday commands](#6-everyday-commands)
7. [Troubleshooting](#7-troubleshooting)

[Credits](#credits)

**More documentation**, in [`Documentation/`](Documentation/):
- **[Reference](Documentation/REFERENCE.md)**, the full spreadsheet columns, frame layout tables, text markup, command-line flags, and other actions (`tile`, `art-extract`, `art-audit`).
- **[Contributing Assets](Documentation/CONTRIBUTING_ASSETS.md)**, for frame, symbol, watermark, and font contributors. No Python required for most of it.
- **[Contributing Code](Documentation/CONTRIBUTING_CODE.md)**, project layout, how a render works, adding a new frame layout, conventions, and the current implementation status (what's done, what isn't, and known bugs).

---

## 1. What this does

You keep your cards in a spreadsheet ([§3](#3-your-first-card)), one row per card. For every row, the generator composites a card image, frames you name ([Reference §3](Documentation/REFERENCE.md#3-the-frames-column-in-depth)), your art ([§5](#5-adding-art)), mana symbols and formatted rules text ([Reference §5](Documentation/REFERENCE.md#5-text-markup)), a set symbol and collector footer ([Reference §1](Documentation/REFERENCE.md#1-spreadsheet-columns)), and saves it as a PNG in `processed_cards/<Set Name>/` ([§2](#where-things-go)).

## 2. Setup

### Install

You need **Python 3.12 or newer**.

```bash
git clone <this repo>
cd MTGCardGenerator

python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

If you want to read card data straight from Google Sheets, also run `pip install gspread google-auth` (see [Reference §8](Documentation/REFERENCE.md#8-google-sheets-setup)).

### Where things go

**Always run the program from the repository root**, not from inside `src/`. Every asset path is resolved relative to where you run it.

| Folder | What goes there |
|---|---|
| `spreadsheets/` | Your card data (`.csv` or `.xlsx`). |
| `images/art/<Set Name>/` | Your card art, one PNG per card. |
| `processed_cards/<Set Name>/` | Where finished cards appear. |
| `settings.json` | Optional saved defaults (see [Reference §7](Documentation/REFERENCE.md#7-settingsjson)). |
| `log.txt` | Written every run. Check it when something looks wrong. |

Everything else (`images/frames/`, `fonts/`, `images/mana_symbols/`, …) ships with the repo and you can ignore it unless you're contributing assets.

## 3. Your first card

### Make a spreadsheet

Open Excel, LibreOffice, Numbers, or Google Sheets and create a sheet whose **first row is exactly this header** (one item per cell):

```
Title | Mana Cost | Rules Text | Supertype(s) | Type(s) | Subtype(s) | Power/Toughness | Frame(s) | Frame Layout | Rarity | Watermark | Watermark Color(s) | Category | Creation Date | Set | Language | Artist | Add Total to Footer? | Additional Title(s) | Descriptor | Orderer | Transform Hint | Transform Frontside | Original | Spellbook(s) | Overlay(s)
```

Every one of those columns must be present or the file is skipped (the log will tell you which are missing). Order doesn't matter and extra columns are ignored.

Add a row:

| Title | Mana Cost | Rules Text | Type(s) | Frame(s) | Frame Layout | Rarity | Category | Creation Date | Set |
|---|---|---|---|---|---|---|---|---|---|
| Lightning Bolt | `{R}` | Lightning Bolt deals 3 damage to any target. | Instant | `regular/red` | Regular | common | regular | 01/01/2025 | Test Set |

Leave the other cells blank. Save it as `spreadsheets/test.xlsx`. Plain `.csv` also works, but a real spreadsheet app is far easier once cells start containing newlines. To keep your data in Google Sheets instead, see [Reference §8](Documentation/REFERENCE.md#8-google-sheets-setup).

### Render it

```bash
python src/main.py
```

That's the whole command. Your card is now at `processed_cards/Test Set/Lightning Bolt.png`.

`log.txt` will mention that no art and no set symbol were found. Both are optional, the card renders without them.

## 4. Filling in the spreadsheet

Three cells do most of the work.

### Frame(s)

A list of image paths under `images/frames/`, one per line, without `.png`, drawn bottom-to-top. A legendary red creature is:

```
regular/red
regular/power_toughness/red
regular/legendary_crown/red
```

Browse `images/frames/` to see what exists. Two-color and other composite frames use *masks*; see [Reference §3](Documentation/REFERENCE.md#3-the-frames-column-in-depth).

### Frame Layout

Picks the card's overall shape, where the title, text box, and other elements sit, and how many of each there are. `Regular` covers most cards; the full table of options is in [Reference §4](Documentation/REFERENCE.md#4-frame-layouts).

### Rules Text

Supports mana symbols like `{T}` or `{2}{U}`, and light markup like `{i}…{/i}` for italics and `{flavor}` for flavor text. The full list is in [Reference §5](Documentation/REFERENCE.md#5-text-markup).

### Multi-line cells

Some layouts have more than one of something, two names, two costs, a text box divided into sections. For those, a cell's lines are read in order (line one for the first, line two for the second), and `{end}` inside Rules Text separates sections. In Excel, Alt+Enter inserts a newline in a cell. The layout table in [Reference §4](Documentation/REFERENCE.md#4-frame-layouts) says exactly which cells each layout reads this way.

Everything else, collector info, alternates, double-faced cards, spellbooks, the command-line, and `settings.json`, is covered in the [Reference](Documentation/REFERENCE.md).

## 5. Adding art

Save a PNG at `images/art/<Set Name>/<Card Title>.png`. The art is placed at the **top-left corner of the card, at its own size**, underneath the frame, so the file should be a full-card-sized canvas with the artwork already positioned where the frame's art window is, not a tight crop. If you only have a crop, `tools/resize_art.py` can help position it.

Art is optional; a missing file just logs a warning.

## 6. Everyday commands

```bash
# Render everything
python src/main.py

# Render only cards whose name contains "Bolt" (partial match)
python src/main.py -c Bolt

# Render only one set
python src/main.py -s "Test Set"

# Use several CPU cores
python src/main.py -w 8

# Pack rendered cards into print sheets instead of rendering
python src/main.py -a tile
```

If you find yourself typing the same flags every time, put them in `settings.json` ([Reference §7](Documentation/REFERENCE.md#7-settingsjson)). The complete flag list is in [Reference §6](Documentation/REFERENCE.md#6-command-line-options).

## 7. Troubleshooting

Always check `log.txt` first, every non-fatal problem is written there, and a broken card won't stop the rest of the batch.

| Symptom | Likely cause |
|---|---|
| `Skipping 'x.xlsx': missing required columns` | Header row is incomplete. Copy the one in [§3](#3-your-first-card). |
| Nothing rendered | A filter excluded everything; or Category is `{skip}`; or you used a date filter and the card has a blank Creation Date (blank-dated cards are dropped when date filtering is on). |
| `Invalid frame path 'x'` | No such file under `images/frames/`. Paths are lowercased and omit `.png`. |
| Red `[foo]` in the rules text | `{foo}` isn't a known symbol. |
| `Text is too long to fit in box even at minimum font size` | It really doesn't fit. Shorten it or use a layout with a bigger box. |
| `Could not find 'X' as an original card of an alternate` | You rendered an alternate with `-c` but filtered out its original. Include both. |
| Title overlaps mana cost | A layout bug, the class's coordinates disagree with the frame. Please report it. |
| Garbled Arabic / Devanagari / Tamil | Pillow needs the Raqm layout engine for complex scripts. |
| Slow | Use `-w` with roughly your core count. |

---

## Credits

Most frames & mana symbols sourced from CardConjurer
- https://github.com/Investigamer/cardconjurer

Standard Magic: the Gathering fonts from M15-Magic-Pack
- https://github.com/MagicSetEditorPacks/M15-Magic-Pack/

Magic: the Gathering is © Wizards of the Coast. This is an unofficial fan tool for personal proxies, not affiliated with or endorsed by Wizards of the Coast. Don't sell what you make with it.
