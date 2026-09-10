# Contributing Code

Project layout, how a render works, adding a new frame layout, coding conventions, and the current implementation status. For frame/asset contribution (which mostly doesn't need this), see [Contributing Assets](CONTRIBUTING_ASSETS.md). For everything else, see the [main README](../README.md) and the [Reference](REFERENCE.md).

---

## Contents

1. [Project layout](#1-project-layout)
2. [How a render works](#2-how-a-render-works)
   - [The data pipeline](#the-data-pipeline)
   - [Rendering a card](#rendering-a-card)
   - [Mixed-resolution frames](#mixed-resolution-frames)
   - [The rules text engine](#the-rules-text-engine)
3. [Adding a frame layout](#3-adding-a-frame-layout)
   - [Steps](#steps)
   - [Multi-section layouts](#multi-section-layouts)
   - [Proportional sections](#proportional-sections)
   - [Non-standard stacking](#non-standard-stacking)
4. [Conventions and workflow](#4-conventions-and-workflow)
   - [Code style](#code-style)
   - [Linting and formatting](#linting-and-formatting)
   - [Checking your output](#checking-your-output)
5. [Tools](#5-tools)

[Implementation status](#implementation-status)
- [Implemented](#implemented)
- [Not implemented / known gaps](#not-implemented--known-gaps)
  - [Functionality](#functionality)
  - [Assets](#assets)
  - [Code quality](#code-quality)

---

## 1. Project layout

```
src/
├── main.py          # CLI, spreadsheet ingestion, card pipeline, the four actions
├── constants.py     # Column names, paths, fonts, frame base sizes, symbol tables, regexes
├── utils.py         # Image/text/geometry helpers with no card knowledge
├── log.py           # Indented logger writing to log.txt
└── model/
    ├── Layer.py     # image + position + optional base_size
    ├── Symbol.py    # symbol image + size ratio / recolorable / resample
    ├── regular/RegularCard.py      # the renderer almost everything inherits from
    └── <family>/<Layout>.py        # one class per frame layout
tools/               # standalone helper scripts (§5)
```

## 2. How a render works

### The data pipeline

`process_spreadsheets` in `main.py`, in order:

1. Gather rows from every CSV, XLSX tab, and Google Sheet; skip sources missing any `REQUIRED_COLUMNS`.
2. Key rows by `get_card_key()`.
3. Fill blank cells on alternates from their originals.
4. Expand multi-set rows into one clone per set.
5. Assign per-(set, category) collector indices and footer totals.
6. Apply whitelists and the date range.
7. Parse Frame Layout: pull modifier tokens into `CARD_FRAME_LAYOUT_EXTRAS`, lowercase and strip the remainder, **write that normalised string back into the card's Frame Layout metadata**, and map it through `layout_to_subclass` to instantiate.
8. Re-instantiate alternates now that they've inherited a layout.
9. Move Transform-Frontside rows into their front's `CARD_BACKSIDES`.
10. Let `ExpandedDungeon*` cards `link_siblings()`.
11. Clone spellbook copies.
12. Sort and hand off to the chosen action.

### Rendering a card

`create_layers()` fills five ordered buckets; `render_card()` alpha-composites them:

```
art_layer → frame_layers → collector_layers → text_layers → overlay_layers
```

`RegularCard.create_layers()` calls one `_create_*_layer` method per element (art, frames, watermark, rarity symbol, footer, mana cost, title, type, rules text, P/T, overlays), each gated by a boolean parameter so subclasses can switch it off. Layouts with extra elements override `create_layers`, call `super()`, then add their own.

Each `_create_*_layer` is responsible for its own control-tag handling (`{skip}`, `{last}`, `{center}`, see [Reference §5](REFERENCE.md#directives-and-control-tags)); only colon directives are extracted centrally.

`render_card_to_image` in `main.py` rotates landscape results 90° so every saved PNG is portrait.

### Mixed-resolution frames

`Layer.base_size` records the resolution a frame was authored at (via `get_frame_base_size()`); `_paste_layer` scales the image and its position by `card_size / base_size` right before compositing. Non-frame layers never carry a `base_size`.

### The rules text engine

`_get_rules_text_layout()` is the most involved code in the project:

1. Split on `{flavor}` / `{divider}` into blocks.
2. For each font size from max down to min: parse lines into typed fragments, word-wrap them while tracking font/bold/alignment/indent/baseline state, reject if too tall, then check collisions with the P/T box, holo stamp, and reverse P/T box (rejecting for left-aligned lines, re-wrapping narrower for centered lines, shifting right-aligned lines).
3. Raise `ValueError` if no size fits.

`_create_rules_text_layer()` draws exactly what the layout pass returned. That separation is what lets Saga, Class, Planeswalker, and Dungeon measure their sections before drawing.

## 3. Adding a frame layout

### Steps

1. Create `src/model/<family>/<Name>.py`, subclassing `RegularCard` or a closer relative.
2. In `__init__`, call `super().__init__(...)` with the same six arguments, then override the `UPPER_CASE` geometry constants you need (all in card pixel space). Set a coordinate to `float("inf")` to disable collision checks against it.
3. Override only the `_create_*_layer` methods whose *structure* differs.
4. Register it in `layout_to_subclass` in `main.py`.
5. Copy the class docstring block from an existing layout, they're deliberately identical.
6. Add a row to the layout table in [Reference §4](REFERENCE.md#4-frame-layouts), including which cells it reads as multi-line.

### Multi-section layouts

These use a save–mutate–restore idiom: temporarily overwrite constants and metadata, call `super()`, then put everything back. `Split._create_title_layer` is a compact example. **Always restore.**

### Proportional sections

Saga, Class, and Planeswalker measure each section with `_get_rules_text_layout` at construction time, then blend each section's proportional share of the box with an even share. Copy that approach for any new sectioned layout.

### Non-standard stacking

For art above part of the frame, rotated frames, or similar, override `render_card`. `Poker` and `Playtest` are the references.

## 4. Conventions and workflow

### Code style

- Numpy-style docstrings with Parameters/Returns on every method; geometry constants grouped under `#` headers.
- Report problems with `log()` and keep going. A single broken card must never abort the batch.
- Card-agnostic helpers go in `utils.py`; anything that knows about cards goes on a model class.
- `constants.py` loads every symbol image at import, once per worker process. Keep it cheap.
- Worker results cross the `ProcessPoolExecutor` boundary as `NamedTuple`s and are logged on the main process so output stays ordered.
- Python 3.12+ is assumed.

### Linting and formatting

```bash
pip install -r requirements-dev.txt
```

The code is formatted black-style at 120 columns with double quotes and sorted imports. Run the formatter and linter from `requirements-dev.txt` over `src/` and `tools/` before committing, and don't submit changes that introduce new warnings. There is no test suite yet; a clean `log.txt` from a representative render is the current bar.

### Checking your output

1. Render a handful of cards that exercise your change (`-c`), including an edge case or two, long titles, long rules text, a two-color frame.
2. Read `log.txt`. It should contain nothing you didn't expect.
3. Open `tools/slide_compare_app.py` with your render on one side and a reference on the other, a scan of a real card in the same frame, or the same card built in CardConjurer or another card-creation tool, and drag the slider across.
4. Fix what the slider shows. Text baselines, symbol sizes, and box alignments that look "about right" alone are obvious when they're a few pixels off against a reference, which makes this the fastest way to tune a new layout's coordinates. A slider comparison is the expected evidence in a pull request that adds or changes a layout.

## 5. Tools

Standalone scripts in `tools/`, independent of the main pipeline:

| Script | Purpose |
|---|---|
| `resize_art.py` | Bulk-resize and position art onto full-card canvases. |
| `resize_frames.py` | Bulk-convert a frame directory between base resolutions (avoid if you can, see [Contributing Assets §2](CONTRIBUTING_ASSETS.md#resolution)). |
| `generate_wall_effect.py` | Generate the dungeon wall shape/effect piece set. |
| `slide_compare_app.py` | Side-by-side slider for comparing a render against a reference image (see [Checking your output](#checking-your-output)). |

---

## Implementation Status

### Implemented

| Area | What works |
|---|---|
| **Input sources** | CSV, XLSX (all tabs or a whitelist), and Google Sheets, merged into one pool. Header validation with per-source skipping. Excel lock-file skipping. XLSX date normalisation. Google Sheets URL→ID extraction; graceful degradation when the Google packages or credentials are absent. |
| **Filtering & sorting** | By name (substring), set, category, spellbook, and creation-date range. Sort by date→orderer→title or orderer→date→title. `settings.json` defaults under CLI flags. |
| **Alternates** | Descriptor / Original rows with per-field inheritance from the original. |
| **Backsides** | Transform-Frontside rows attached to their front, with collector-field inheritance. |
| **Multi-set** | One clone per listed set, with cross-set art and set-symbol fallback. |
| **Spellbooks** | Per-spellbook clones with independent numbering and `SB:` footer. |
| **Collector numbering** | Per-(set, category) indices, footer totals, `{skip}` categories. |
| **Compositing** | Five-bucket layered composite; `{end}` promotion of frames above text; mask stacking that preserves RGB; per-layer rescaling of mixed-resolution frame families; `{offset}` and `{symbol}` directives; `{last}` overlay promotion. |
| **Title & type line** | Auto-shrink to fit (title bounded by the mana cost, type by its box and the set symbol); `{color}` segments; outlines and drop shadows. |
| **Rules text** | Word wrap, italics, faux bold, per-fragment color, four alignments, bullets with hanging indent, no-break runs, invisible spacers, flavor blocks with dividers, striped dice tables, inline symbols centered on cap height, shadows and outlines; collision avoidance against P/T, reverse P/T, and holo stamps. |
| **Fonts** | Fifteen script-fallback fonts with automatic cap-height scaling and baseline alignment, italic variants where available. |
| **Collector info** | Watermarks (one or two colors, opacity), set symbols with `custom`→`official`→other-set fallback, rotatable footer with number/total/spellbook/set/language/rarity/artist/date. |
| **Mana cost** | Symbol rendering with shadows, outlines, left/center/right alignment, `{text}` literal spans. |
| **Misc text** | Smart quotes, `*`→★, `{cardname}`, overlays. |
| **Layouts** | Everything listed in [Reference §4](REFERENCE.md#4-frame-layouts), including the full dungeon engine and both expanded-dungeon variants. |
| **tile** | Per-category sheets, `{category}-{n}` / `{category}-*` filters, backsides included. |
| **art-extract** | Layout/frame support check with a spreadsheet-less fallback. |
| **art-audit** | Bidirectional art↔card reconciliation. |
| **Parallelism** | `render` and `tile` via `--workers`, with per-card error capture and tracebacks in the log. |

### Not implemented / known gaps

#### Functionality

- **No tests** of any kind, no unit tests, no golden-image comparisons, no CI.
- **`art-extract` only actually supports a fraction of what it intends to.** Its `frame_layout_map` looks up the card's Frame Layout *after* the pipeline has already lowercased it and stripped modifier tokens (pipeline step 7), so the real lookup keys are strings like `"saga"`, `"class"`, `"adventure"`, `"split"`, and `"fuse"`. The map, however, was written against older, un-normalised names, `"regular saga"`, `"regular class"`, `"regular adventure"`, `"regular split"`, `"regular fuse"`, `"regular vehicle"`, which no card can ever have by that point. Consequences:
  - Saga, Class, Adventure, Split, and Fuse cards are logged as *unsupported* even though the map has entries for them. Only `regular`, `regular split rules text`, `transform frontside`/`backside`, `modal frontside`/`backside`, `transform saga`, and `sketch` actually work.
  - Even if the split keys were fixed, the `ART_*` tables have no `"split"` entry, so extraction would raise `KeyError` (flagged `# TODO`).
  - The modifier-stripping loop inside `capture_art` runs `str.replace` with the *regex source strings* from `FRAME_LAYOUT_EXTRAS_LIST` as literal substrings, which can't match anything. It's harmless (the metadata was already stripped) but dead.
- **No packaging**: no `pyproject.toml`, entry point, or `__init__.py`; must be run from the repo root.
- **No GUI**, no PDF/print-sheet export (bleed, crop marks, DPI, imposition are downstream), no card-back generation (a `cardback` frame directory exists but nothing drives it), no Scryfall or other external import, no caching or incremental rendering, no write-back to Google Sheets.
- `log.txt` is overwritten each run; there are no log levels.

#### Assets

- **Mismatched frame sizes** in several directories, each flagged with a `# TODO` in `FRAME_DIRECTORY_BASE_SIZES` in `src/constants.py`.
- **Frame families with no layout class**: any directory under `images/frames/` whose family isn't in [Reference §4](REFERENCE.md#4-frame-layouts) (most of `custom/`, roughly forty `showcase/` families, and older shapes like `attraction`, `vanguard`, `planechase`, `flip`, `mutate`, `aftermath`, `prototype`, `station`, `spree`) is only usable as a `Regular` backdrop and will often misalign.
- **Incomplete showcase symbol sets**: Future Shifted, Playtest, Pixel, and Japanese Mystical Archive each lack part of the standard set and fall back to default art.
- **Unwired symbol directories**: several `images/mana_symbols/showcase/*` folders and `mana_symbols/purple` have art but no dict in `constants.py`.
- **Unreferenced images** in `images/collector_info/`, `images/other/`, `images/mana_symbols/`, and `images/frames/old/icons/`.
- **Working files in the asset tree**: `.kra` files and `.png~` backups in several folders.

#### Code quality

- `model/showcase/mystical_archive/MysticalArchive.py` exists but is empty and unreferenced.
- `RegularCard` handles art, frames, watermarks, symbols, footers, and all text rendering in one class; splitting it is a long-standing wish.
- Control tags (`{skip}`, `{last}`, `{center}`) are re-implemented in every `_create_*_layer` rather than parsed once, so support is uneven across elements.
- The save–mutate–restore idiom is not exception-safe (latent: objects are discarded after one render).
- `Split._create_type_layer` tests `len(supertypes) > 0` for the second half's type and subtype instead of their own lists.
- `Dungeon.__init__` performs the entire layout at construction time, so building a dungeon card is expensive even if it's never rendered.
- `Symbol.size_ratio` accepts a tuple but is annotated as `float`; `Token.__init__` has an unused `footer_largest_index` parameter.
- Paths are string-concatenated throughout, with Windows-specific `rfind("\\")` in `capture_art`/`audit_art` that misbehaves on POSIX.
- No type checking, formatter, or pre-commit hooks are enforced.
