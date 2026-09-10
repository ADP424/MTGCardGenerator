# Reference

The full spreadsheet format, frame layout tables, text markup, command-line flags, and the non-`render` actions. For the quick-start walkthrough, see the [main README](../README.md).

---

## Contents

1. [Spreadsheet columns](#1-spreadsheet-columns)
   - [Column table](#column-table)
   - [Card keys and filenames](#card-keys-and-filenames)
2. [Card relationships and numbering](#2-card-relationships-and-numbering)
   - [Categories and collector numbers](#categories-and-collector-numbers)
   - [Alternates](#alternates)
   - [Backsides](#backsides)
   - [Spellbooks](#spellbooks)
   - [Multi-set cards](#multi-set-cards)
3. [The Frame(s) column in depth](#3-the-frames-column-in-depth)
   - [Masks](#masks)
   - [`{end}`](#end)
   - [Offsets](#offsets)
   - [Mixed resolutions](#mixed-resolutions)
4. [Frame layouts](#4-frame-layouts)
   - [Standard shapes](#standard-shapes)
   - [Showcase layouts](#showcase-layouts)
   - [Dungeon layouts](#dungeon-layouts)
   - [Modifier tokens](#modifier-tokens)
5. [Text markup](#5-text-markup)
   - [Symbols](#symbols)
   - [Formatting tags](#formatting-tags)
   - [Font fallback tags](#font-fallback-tags)
   - [Directives and control tags](#directives-and-control-tags)
6. [Command-line options](#6-command-line-options)
7. [settings.json](#7-settingsjson)
8. [Google Sheets setup](#8-google-sheets-setup)
9. [Other actions](#9-other-actions)
   - [tile](#tile)
   - [art-extract](#art-extract)
   - [art-audit](#art-audit)

---

## 1. Spreadsheet columns

### Column table

| Column | Meaning |
|---|---|
| **Title** | Card name. Also the basis for the output filename and the art filename. |
| **Mana Cost** | Symbol tokens, e.g. `{2}{W}{U}`. Multi-line for layouts with more than one cost ([§4](#4-frame-layouts)). |
| **Rules Text** | Body text with markup ([§5](#5-text-markup)). `{end}` separates sections on sectioned layouts. |
| **Supertype(s)** | e.g. `Legendary`, `Snow`. |
| **Type(s)** | e.g. `Creature`, `Instant`. |
| **Subtype(s)** | e.g. `Human Wizard`. Joined to the types with an em dash. |
| **Power/Toughness** | `3/4`, or a planeswalker's starting loyalty. `*` renders as ★. |
| **Frame(s)** | Newline-separated frame paths ([§3](#3-the-frames-column-in-depth)). |
| **Frame Layout** | Layout name plus optional modifier tokens ([§4](#4-frame-layouts)). |
| **Rarity** | `common`, `uncommon`, `rare`, `mythic`, `land`, `lato`, `token`. Picks the set symbol and the footer initial (see `RARITY_TO_INITIAL` in `src/constants.py`). |
| **Watermark** | Filename (no extension) under `images/collector_info/watermarks/`. |
| **Watermark Color(s)** | One or two lines naming colors, e.g. `red`, `gold`, `artifact`. Two colors split left/right. The full list is `WATERMARK_COLORS` in `src/constants.py`. |
| **Category** | Grouping for collector numbering and tile sheets ([§2](#categories-and-collector-numbers)). `{skip}` means "parse but never render". |
| **Creation Date** | `MM/DD/YYYY`. Used for sorting and date filtering. |
| **Set** | Output folder and art folder. Multi-line = one copy per set ([§2](#multi-set-cards)). |
| **Language** | Free text, shown in the footer. |
| **Artist** | Free text, shown in the footer with a brush icon. |
| **Add Total to Footer?** | `1` to show `007/250` instead of `007`. |
| **Additional Title(s)** | Extra names, used by layouts with more than one name ([§4](#4-frame-layouts)). |
| **Descriptor** | Marks this row as an alternate of another card ([§2](#alternates)). |
| **Orderer** | Integer used by `--sort-by-orderer`. |
| **Transform Hint** | The small grey reverse P/T on transform fronts, or the mana hint on modal fronts. |
| **Transform Frontside** | If set, this row is the *back* of the named card ([§2](#backsides)). |
| **Original** | Explicit card key of the card an alternate is based on ([§2](#alternates)). |
| **Spellbook(s)** | Newline-separated spellbook names ([§2](#spellbooks)). |
| **Overlay(s)** | Newline-separated images under `images/art/overlay/` drawn above everything (e.g. `foil`). |

Several of these are read line-by-line or split on `{end}` depending on the layout, see [Multi-line cells](../README.md#multi-line-cells) in the main README and the table in [§4](#4-frame-layouts).

### Card keys and filenames

Internally a card is identified by `Title - Additional Title - … - Descriptor - Spellbook` with all `{...}` markup stripped. That's what art files, **Original**, and **Transform Frontside** match on. For filenames, characters illegal on Windows are escaped (`:` → `{C}`, `/` → `{FS}`, and so on; see `cardname_to_filename` in `src/utils.py`).

## 2. Card relationships and numbering

### Categories and collector numbers

**Category** is a free-text grouping (e.g. `regular`, `token`, `basic land`). Collector numbers in the footer are assigned per (set, category), counting up in sort order, so `--sort-by-date` / `--sort-by-orderer` change the numbering, and re-sorting your sheet re-numbers your cards. Categories are also how the `tile` action groups cards onto sheets ([§9](#tile)). A category of `{skip}` parses the card but never renders it.

### Alternates

A row with a **Descriptor** (or an **Original**) is an alternate version of another card. Blank cells are filled from the original's row, except Set, Artist, Overlay(s), Transform Frontside, Category, and Spellbook(s). Its key and filename become `Title - Descriptor`. When rendering with `-c`, **include the original too**, or the fill-in fails.

### Backsides

A row with **Transform Frontside** set is attached to that card and rendered with it, never on its own. It shares its front's collector number and, wherever its own cells are blank, inherits the front's Category, Rarity, Creation Date, Language, and Spellbook(s).

### Spellbooks

Each name in **Spellbook(s)** produces a clone with its own `SB:<name>` footer line and its own numbering within that spellbook. `--no-spellbooks` suppresses them; `--spellbooks X` keeps *only* the copies for X.

### Multi-set cards

A multi-line **Set** produces one clone per set, each numbered within its own set. Art and set symbols fall back to the card's other sets when missing.

## 3. The Frame(s) column in depth

One path per line, relative to `images/frames/`, no `.png`, drawn bottom-to-top.

### Masks

Any path containing `mask/` isn't drawn. It's held and multiplied into the alpha of the *next* non-mask frame. Several masks in a row stack. This is how two-color frames work:

```
regular/mask/left
regular/red
regular/mask/right
regular/blue
regular/power_toughness/multicolor
```

### `{end}`

A line that is exactly `{end}` makes every following frame render *above* the text instead of below it.

### Offsets

Append `{offset:(x, y)}` to a line (before or after the path) to shift that frame. Ignored on mask lines.

### Mixed resolutions

Frames were authored at different sizes over the years. The generator knows each directory's native size and rescales per layer, so mixing e.g. a 2010×2814 crown over a 1500×2100 token frame just works.

## 4. Frame layouts

The Frame Layout cell is case-insensitive. Anything unrecognised falls back to **Regular**. The authoritative mapping is `layout_to_subclass` in `src/main.py`.

In the **Multi-line cells** column, `⏎` means the cell is read line by line and `{end}` means Rules Text is split into sections ([Multi-line cells](../README.md#multi-line-cells) in the main README). Cells not listed take a single value.

### Standard shapes

| Frame Layout | Multi-line cells | Notes |
|---|---|---|
| `Regular` | — | The standard M15-style card. `Draconic` is an alias. |
| `Regular Split Rules Text` | Rules Text: left `{end}` right | Regular, with two side-by-side text columns. |
| `Transform Frontside` / `Transform Backside` | — | Backside row sets **Transform Frontside** to the front's title. Front's **Transform Hint** is the grey reverse P/T. |
| `Meld Backside Top` / `Middle` / `Bottom` | — | Three landscape cards forming one meld back. |
| `Modal Frontside` / `Modal Backside`, `Short Modal …` | — | **Additional Title(s)** = bottom-left type hint, **Transform Hint** = mana hint. |
| `Split` / `Fuse` | Mana Cost ⏎ · Supertype/Type/Subtype ⏎ · Additional Title(s): second name · Rules Text: left `{end}` right (`{end}` reminder for Fuse) · Watermark Color(s): left `{end}` right | Landscape, two half-cards. |
| `Token`, `Short Token`, `Tall Token`, `Textless Token` | — | Regular with a centered small-caps title; variants differ in text box height. |
| `Token Transform Frontside` / `Backside`, `Textless Token Transform …` | — | Token styling on the transform layouts. |
| `Planeswalker` | Mana Cost: cost ⏎ ability cost ⏎ … (`+1`, `-3`, `0`) · Rules Text: one section per ability | Ability boxes sized to their text. |
| `Saga` / `Transform Saga` | Rules Text: static text `{end}` chapter I `{end}` chapter II … | Identical consecutive chapters share a box. |
| `Class` | Mana Cost: cost ⏎ level cost ⏎ … · Additional Title(s): level name ⏎ … · Rules Text: one section per level | Level headers drawn between sections. |
| `Adventure` / `Omen` / `Prepare` | Mana Cost ⏎ · Supertype/Type/Subtype ⏎ · Additional Title(s): side name · Rules Text: main `{end}` side | Second spell in a side box. |
| `Battle` / `Transform Battle` | — | Landscape; otherwise standard elements. |
| `Room` | Mana Cost ⏎ · Additional Title(s): second door · Rules Text: shared `{end}` left `{end}` right · Watermark Color(s): left `{end}` right | Landscape, two doors plus shared text. |
| `Conspiracy` | — | Regular with a repositioned set symbol. |
| `Edifice` | — | Regular with a white P/T plate (custom type). |
| `Leveler` | Mana Cost: cost ⏎ level range ⏎ level range · Power/Toughness ⏎ ⏎ · Rules Text: three sections | Three tiers, each with its own P/T. |
| `Dungeon`, `Expanded Dungeon Global` / `Local` | Rules Text: one section per room | See [Dungeon layouts](#dungeon-layouts). |

### Showcase layouts

| Frame Layout | Multi-line cells | Notes |
|---|---|---|
| `Transparent` | — | Regular geometry; light/dark text via `white`/`light` tokens. |
| `Full Text` | — | No art; text box fills the card. |
| `Clear Textbox` | — | Regular with white type and rules text. |
| `Japan` | — | Outlined white text, lower type line. |
| `Japanese Mystical Archive` | Watermark Color(s) ⏎ (title bar colors) | Vertical title bar grows to fit. |
| `Japanese Mystical Archive Horizontal` | — | Same fonts and symbols, normal title bar. |
| `Future Shifted` | — | Pips down the left edge (max six); type icon top-left. |
| `Zendikar` | — | Regular with white, drop-shadowed text. |
| `Sketch` | — | Regular with a smaller title and nudged P/T / set symbol. |
| `Playtest` | Rules Text: main `{end}` reminder | Default reminder is "TEST CARD". Honors `rotate<deg>`. |
| `Pixel` | — | Pixel font and symbols, all-caps title and type. |
| `Monopoly`, `Coup`, `Demotivational Poster` | — | Mana cost relocated off the title line; themed fonts. |
| `Chat` | Supertype/Type/Subtype ⏎ per window · Additional Title(s): username per extra window · Rules Text: one section per window · Frame(s): one window frame per section, each with `{offset:(x, y)}` | Title becomes the first window's inline username. |
| `Poker` | — | Art drawn above the border, below the base overlay. |
| `Breaking News` | Rules Text: main `{end}` red box | Landscape. Title and type share one bar. |
| `Promo` | — | White, drop-shadowed text; lower type line. |
| `Extended Promo` / `Open House Promo` | — | Promo geometry with dark title, rules text, and P/T; type line stays white. |
| `Full Art Basic THB` / `SNC` | — | Type line at the bottom; SNC draws the subtype separately on the right. |
| `LOTR Ring` | — | Regular geometry with white title, type, and P/T text. |
| `LOTR Scroll` | — | Regular geometry with a narrower set symbol. |
| `Storybook Adventure` | As `Adventure` | Adventure geometry for the storybook frame. |

### Dungeon layouts

Each `{end}` section of Rules Text is a room: its first line is the room name, the rest is its body. Rooms fill rows left to right; start a new row with `{row}`. Rooms directly above/below each other are connected by doorways automatically. Other per-room directives, written anywhere in the section: `{span=1.5}` relative width, `{rowspan=2}`, `{height=1.2}` row height multiplier, `{id=name}` extra target names, `{to=Room Name, 3}` explicit doorways (replaces the automatic ones; `{to=none}` for none), `{nameless}`, `{noarrow}`.

`Expanded Dungeon Local` spreads a dungeon over several cards, each laid out on its own; the card's grid position goes in Frame Layout (e.g. `Expanded Dungeon Top Title Left`) and cross-card doorways are written `{to=Other Card: room: right}`. `Expanded Dungeon Global` lays the whole dungeon out on one primary card (e.g. `Expanded Dungeon Global 2x3`) and crops it per card; part cards carry `{dungeon=Primary Card}` and `{cell=row,column}` in their Rules Text.

The full grammar is `_get_dungeon_placeholder_regex` in `src/model/dungeon/Dungeon.py`, with the expanded additions in `ExpandedDungeon.py` / `ExpandedDungeonGlobal.py`.

### Modifier tokens

Words that may follow the layout name (e.g. `Regular Pip Vehicle`). They're stripped off and used to tweak colors or positions. The most common:

| Token | Effect |
|---|---|
| `pip` | Shifts the type line right to clear a color-identity pip. |
| `white`, `light` | Dark text on frames with light title/type bars. |
| `black`, `dark` | Light text (Monopoly). |
| `vehicle` | White P/T text. |
| `rotate<deg>` | Rotates the frame/text layers (Playtest). |

The Expanded Dungeon position and grid tokens are also modifiers. The complete list is `FRAME_LAYOUT_EXTRAS_LIST` in `src/constants.py`.

## 5. Text markup

All of this works in Rules Text. Title, type line, P/T, and the modal hints support the `{color}` tag, the font-fallback tags, and the control tags.

### Symbols

Write mana as `{W}`, `{2}`, `{X}`, tap as `{T}`, hybrids as `{W/U}` or `{2/G}`, phyrexian as `{WP}`, energy as `{E}`. Hybrids accept any order. Unknown tokens render as a red `[token]` so you can spot them.

The complete token list, including snow, trybrids, hybrid phyrexian, and custom symbols, is `SYMBOL_PLACEHOLDER_KEY` in `src/constants.py`. Showcase layouts with their own symbol art have sibling dicts right below it.

### Formatting tags

| Tag | Effect |
|---|---|
| `{i}`…`{/i}` | Italics. |
| `{bold}`…`{/bold}` | Bold. |
| `{center}`, `{right}`, `{hardright}`, `{left}` | Line alignment. Put `{center}` at the **start** of a block. `{right}` dodges the P/T box; `{hardright}` doesn't. |
| `{nobreak}`…`{/nobreak}` | Break mid-word instead of wrapping whole words. |
| `{flavor}` | Everything after is an italic flavor block below a divider. |
| `{divider}` | Ends a flavor block / inserts a divider. |
| `{lns}` | Hard line break inside a block. |
| `{ln}` | Literal newline (for one-line cells). |
| `{bullet}` | `• ` with a hanging indent. |
| `{space}`…`{/space}` | Advance horizontally without drawing. |
| `{color(r,g,b)}`…`{/color}` | Colored text. |
| `{cardname}` | The card's Title. |
| `{-}` | Em dash. |
| `{dice-<color>}`…`{/dice}` | Striped dice-table rows; bare `1-5` / `6` tokens inside become the roll column. |
| `{text}`…`{/text}` | Mana Cost only: literal text instead of symbols. |

These are parsed by `parse_fragments` inside `RegularCard._get_rules_text_layout`.

### Font fallback tags

For characters the Magic fonts lack, wrap them: `{jp}…{/jp}` for Japanese, `{emoji}…{/emoji}`, `{ucs}…{/ucs}` for general Unicode, and so on. `{\jp}` also closes; an unclosed tag runs to the end. The fallback font is scaled and baseline-aligned to match its surroundings. The full set of tags is `DIRECTIVE_FONTS` in `src/constants.py`.

### Directives and control tags

Two kinds of tag look alike but are handled differently.

**Directives** have a colon: `{offset:(x, y)}` shifts an element (works on Title, Type, Mana Cost, Rules Text, P/T, Frame(s), Overlay(s)); `{symbol:path}` on Rarity overrides the set symbol image (relative to `images/collector_info/set_symbols/`, no extension). These are stripped centrally by `RegularCard._extract_directives` using `DIRECTIVE_PATTERN` in `src/constants.py`, before the cell text is used for anything else.

**Control tags** have no colon and are *not* centrally parsed, each `_create_*_layer` method checks for them itself:

| Tag | Effect | Honored by |
|---|---|---|
| `{skip}` | Don't draw this element. In Category, don't render the card (handled in `main.py`). | Title, Type, Mana Cost, Rules Text, P/T, Watermark, Rarity, Transform Hint |
| `{last}` | Draw this element above everything else. | Title, Type, Mana Cost, Rules Text, P/T, Watermark, Rarity |
| `{center}` | Center this element. | Title, Type, Mana Cost, modal type hint (in Rules Text it's an alignment tag, above) |
| `{end}` | Split the cell. | Frame(s) (below/above text) and whichever cells the layout class sections ([§4](#4-frame-layouts)) |

For developers: adding a new control tag means adding a check to every method that should honor it; adding a new directive means extending `DIRECTIVE_PATTERN` and reading it from the returned dict.

## 6. Command-line options

```
python src/main.py [options]
```

| Flag | Description |
|---|---|
| `-a, --action {render,tile,art-extract,art-audit}` | Default `render`. |
| `-c, --cards NAME [...]` | Only cards whose name contains one of these (case-sensitive substring). |
| `-s, --sets SET [...]` | Only these sets (case-insensitive). |
| `-cat, --categories CAT [...]` | Only these categories. |
| `-nsb, --no-spellbooks` | Don't generate spellbook copies. |
| `-sb, --spellbooks NAME [...]` | Only these spellbooks' copies; base versions dropped. |
| `-od, --oldest-date MM/DD/YYYY` | Earliest creation date. |
| `-ld, --latest-date MM/DD/YYYY` | Latest creation date. |
| `-sbd, --sort-by-date` | Sort by date → orderer → title (the default). |
| `-sbo, --sort-by-orderer` | Sort by orderer → date → title. |
| `-tn, --tile-nums CAT-N [...]` | `tile` only: e.g. `regular-12`, or `regular-*` for all. |
| `-sh, --sheets NAME [...]` | Only these spreadsheet files (filename without extension). |
| `-t, --tabs NAME [...]` | Only these XLSX / Google Sheets tabs. |
| `-gs, --google-sheets ID_OR_URL [...]` | Also fetch these Google Sheets. |
| `-gc, --google-credentials PATH` | Service-account JSON. Default `credentials/google_service_account.json`. |
| `-w, --workers N` | Parallel processes for `render` and `tile`. Default 1. |

`python src/main.py --help` prints the same list.

## 7. settings.json

Any flag can be given a default in `settings.json` at the repo root; command-line flags override it. **Copy `settings.example.json` to `settings.json` and edit it**, it lists every available key with a sample value. Dates are written as `MM/DD/YYYY` strings.

## 8. Google Sheets setup

1. `pip install gspread google-auth`
2. In Google Cloud, create a project, enable the Sheets and Drive APIs, create a **service account**, and download its JSON key to `credentials/google_service_account.json`.
3. **Share each spreadsheet with the service account's email address** (Viewer is enough).
4. Run with `-gs <url or id>`, or add the IDs to `settings.json`.

Each tab is treated like a separate sheet and must have the full header row.

## 9. Other actions

### tile

`-a tile` packs rendered cards into large sheets for bulk printing: each card is resized to 1500×2100 and laid into a grid capped at 10000×10000 (24 cards per sheet). Output: `processed_tiles/<Set>/<category>/<n>.png`, one sequence per Category ([§2](#categories-and-collector-numbers)). Backsides follow their fronts. `-tn` re-renders specific sheets.

### art-extract

`-a art-extract` crops the art window back out of finished card images in `existing_cards/` and writes full-canvas art files to `extracted_art/`. It uses the spreadsheet to know each card's layout and only proceeds for layouts and frames it recognises. With no matching spreadsheet data it blindly crops the regular art box from every PNG. See the [known gaps](CONTRIBUTING_CODE.md#functionality) before relying on it.

### art-audit

`-a art-audit` compares `images/art/<Set>/` with the spreadsheet and logs cards with no art and art with no card.
