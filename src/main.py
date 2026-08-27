import argparse
import copy
import csv
import glob
import json
import os
import re
from datetime import datetime
from typing import Callable

import openpyxl
from PIL import Image

try:
    import gspread
    from google.oauth2.service_account import Credentials as ServiceAccountCredentials

    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

from constants import (
    ACTIONS,
    ART_HEIGHT,
    ART_WIDTH,
    ART_X,
    ART_Y,
    CARD_ADDITIONAL_TITLES,
    CARD_ALL_SETS,
    CARD_ARTIST,
    CARD_BACKSIDES,
    CARD_CATEGORY,
    CARD_CREATION_DATE,
    CARD_DESCRIPTOR,
    CARD_FOOTER_LARGEST_INDEX,
    CARD_FRAME_LAYOUT,
    CARD_FRAME_LAYOUT_EXTRAS,
    CARD_FRAMES,
    CARD_FRONTSIDE,
    CARD_INDEX,
    CARD_LANGUAGE,
    CARD_ORDERER,
    CARD_ORIGINAL,
    CARD_OVERLAYS,
    CARD_RARITY,
    CARD_SET,
    CARD_SPELLBOOK,
    CARD_SPELLBOOKS,
    CARD_TILE_HEIGHT,
    CARD_TILE_WIDTH,
    CARD_TITLE,
    FRAME_LAYOUT_EXTRAS_LIST,
    GOOGLE_CREDENTIALS_PATH,
    INPUT_ART_PATH,
    INPUT_CARDS_PATH,
    INPUT_SPREADSHEETS_PATH,
    MAX_TILING_HEIGHT,
    MAX_TILING_WIDTH,
    OUTPUT_ART_PATH,
    OUTPUT_CARDS_PATH,
    OUTPUT_TILES_PATH,
    REQUIRED_COLUMNS,
    SETTINGS_PATH,
)
from log import decrease_log_indent, increase_log_indent, log, reset_log
from model.adventure.RegularAdventure import RegularAdventure
from model.battle.Battle import Battle
from model.battle.TransformBattle import TransformBattle
from model.conspiracy.Conspiracy import Conspiracy
from model.dungeon.Dungeon import Dungeon
from model.dungeon.ExpandedDungeonGlobal import ExpandedDungeonGlobal
from model.dungeon.ExpandedDungeonLocal import ExpandedDungeonLocal
from model.edifice.RegularEdifice import RegularEdifice
from model.modal.ModalBackside import ModalBackside
from model.modal.ModalFrontside import ModalFrontside
from model.modal.short.ShortModalBackside import ShortModalBackside
from model.modal.short.ShortModalFrontside import ShortModalFrontside
from model.mtg_class.RegularClass import RegularClass
from model.omen.RegularOmen import RegularOmen
from model.planeswalker.RegularPlaneswalker import RegularPlaneswalker
from model.prepare.RegularPrepare import RegularPrepare
from model.regular.RegularCard import RegularCard
from model.regular.RegularSplitRulesText import RegularSplitRulesText
from model.room.RegularRoom import RegularRoom
from model.saga.RegularSaga import RegularSaga
from model.saga.TransformSaga import TransformSaga
from model.showcase.Chat import Chat
from model.showcase.Coup import Coup
from model.showcase.full_art_basic.FullArtBasicSNC import FullArtBasicSNC
from model.showcase.full_art_basic.FullArtBasicTHB import FullArtBasicTHB
from model.showcase.FullText import FullText
from model.showcase.FutureShifted import FutureShifted
from model.showcase.Japan import Japan
from model.showcase.lotr.Ring import RingLOTR
from model.showcase.lotr.Scroll import ScrollLOTR
from model.showcase.meme.DemotivationalPoster import DemotivationalPoster
from model.showcase.Monopoly import Monopoly
from model.showcase.news.BreakingNews import BreakingNews
from model.showcase.Pixel import Pixel
from model.showcase.Playtest import Playtest
from model.showcase.Poker import Poker
from model.showcase.promo.ExtendedPromo import ExtendedPromo
from model.showcase.promo.OpenHousePromo import OpenHousePromo
from model.showcase.promo.RegularPromo import RegularPromo
from model.showcase.Sketch import Sketch
from model.showcase.transparent.RegularTransparent import RegularTransparent
from model.showcase.Zendikar import Zendikar
from model.split.fuse.RegularFuse import RegularFuse
from model.split.RegularSplit import RegularSplit
from model.token.RegularToken import RegularToken
from model.token.ShortToken import ShortToken
from model.token.TallToken import TallToken
from model.token.TextlessToken import TextlessToken
from model.token.transform.backside.RegularTokenTransformBackside import (
    RegularTokenTransformBackside,
)
from model.token.transform.backside.TextlessTokenTransformBackside import (
    TextlessTokenTransformBackside,
)
from model.token.transform.frontside.RegularTokenTransformFrontside import (
    RegularTokenTransformFrontside,
)
from model.token.transform.frontside.TextlessTokenTransformFrontside import (
    TextlessTokenTransformFrontside,
)
from model.transform.TransformBackside import TransformBackside
from model.transform.TransformFrontside import TransformFrontside
from utils import (
    cardname_to_filename,
    get_card_key,
    open_image,
    paste_image,
    str_to_datetime,
    str_to_int,
)


def read_rows_from_csv(filepath: str) -> list[dict[str, str]]:
    """
    Read all data rows from a CSV file as a list of column-to-value dicts.

    The file's header row is checked against REQUIRED_COLUMNS. If any are
    missing the file is skipped and the missing columns are logged.

    Parameters
    ----------
    filepath: str
        The path to the CSV file to read.

    Returns
    -------
    list[dict[str, str]]
        One dict per data row, mapping column headers to stripped cell values.
    """

    rows = []
    with open(filepath, "r", encoding="utf8") as f:
        reader = csv.reader(f)
        columns = next(reader)

        missing = REQUIRED_COLUMNS - {col.strip() for col in columns}
        if missing:
            log(f"Skipping '{filepath}': missing required columns: {sorted(missing)}")
            return rows

        for row in reader:
            rows.append(dict(zip(columns, [element.strip() for element in row])))
    return rows


def read_rows_from_xlsx(filepath: str, tabs_whitelist: list[str] = None) -> list[dict[str, str]]:
    """
    Read all data rows from every sheet of an XLSX workbook as column-to-value dicts.

    Each sheet is expected to have a header row followed by data rows, matching the same
    column names used by the CSV files. Sheets with no data rows are skipped. All cell values
    are converted to stripped strings; None cells become empty strings.

    Each sheet's header row is checked against REQUIRED_COLUMNS. If any are missing the
    sheet is skipped and the missing columns are logged.

    Parameters
    ----------
    filepath: str
        The path to the XLSX file to read.

    tabs_whitelist: list[str], optional
        If provided, only process sheets whose names appear in this list (case-insensitive).
        Process all sheets by default.

    Returns
    -------
    list[dict[str, str]]
        One dict per data row, mapping column headers to stripped cell values.
    """

    def _xlsx_cell_to_str(cell) -> str:
        """
        Stringify an XLSX cell value, formatting datetimes as a bare date (no time).
        """

        if cell is None:
            return ""
        if isinstance(cell, datetime):
            return cell.strftime("%m/%d/%Y")
        return str(cell).strip()

    rows = []
    tabs_whitelist_lower = [t.lower() for t in tabs_whitelist] if tabs_whitelist is not None else None
    workbook = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    for sheet in workbook.worksheets:
        if tabs_whitelist_lower is not None and sheet.title.lower() not in tabs_whitelist_lower:
            continue
        row_iter = sheet.iter_rows(values_only=True)
        header = next(row_iter, None)
        if header is None:
            continue
        columns = [str(c).strip() if c is not None else "" for c in header]

        missing = REQUIRED_COLUMNS - set(columns)
        if missing:
            log(f"Skipping tab '{sheet.title}' in '{filepath}': missing required columns: {sorted(missing)}")
            continue

        for row in row_iter:
            padded_row = list(row) + [None] * (len(columns) - len(row))
            rows.append({col: _xlsx_cell_to_str(cell) for col, cell in zip(columns, padded_row)})
    workbook.close()
    return rows


def extract_google_spreadsheet_id(id_or_url: str) -> str:
    """
    Extract a Google Sheets spreadsheet ID from a full URL, or return the string as-is if
    it is already a bare ID.

    Parameters
    ----------
    id_or_url: str
        A Google Sheets URL (e.g. ``https://docs.google.com/spreadsheets/d/abc123/edit``)
        or a raw spreadsheet ID (e.g. ``abc123``).

    Returns
    -------
    str
        The spreadsheet ID.
    """

    match = re.match(r"https?://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)", id_or_url)
    if match:
        return match.group(1)
    return id_or_url.strip()


def read_rows_from_google_sheet(
    client,
    spreadsheet_id: str,
    tabs_whitelist: list[str] = None,
) -> list[dict[str, str]]:
    """
    Read all data rows from a Google Sheets spreadsheet as column-to-value dicts.

    Each worksheet's header row is checked against REQUIRED_COLUMNS. Worksheets with
    missing required columns are skipped with a log message.

    Parameters
    ----------
    client: gspread.Client
        An authorised gspread client.

    spreadsheet_id: str
        The Google Sheets spreadsheet ID.

    tabs_whitelist: list[str], optional
        If provided, only process worksheets whose names appear in this list
        (case-insensitive). Process all worksheets by default.

    Returns
    -------
    list[dict[str, str]]
        One dict per data row, mapping column headers to stripped cell values.
    """

    rows: list[dict[str, str]] = []
    tabs_whitelist_lower = [t.lower() for t in tabs_whitelist] if tabs_whitelist is not None else None

    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
    except Exception as e:
        log(f"Could not open Google Sheet '{spreadsheet_id}': {type(e).__name__}: {e}")
        return rows

    for worksheet in spreadsheet.worksheets():
        if tabs_whitelist_lower is not None and worksheet.title.lower() not in tabs_whitelist_lower:
            continue

        try:
            all_values = worksheet.get_all_values()
        except Exception as e:
            log(f"Error reading tab '{worksheet.title}' in Google Sheet '{spreadsheet_id}': {type(e).__name__}: {e}")
            continue

        if len(all_values) < 2:
            continue

        columns = [str(c).strip() for c in all_values[0]]

        missing = REQUIRED_COLUMNS - set(columns)
        if missing:
            log(
                f"Skipping tab '{worksheet.title}' in Google Sheet '{spreadsheet_id}': "
                f"missing required columns {sorted(missing)}"
            )
            continue

        num_columns = len(columns)
        for row in all_values[1:]:
            padded_row = row + [""] * (num_columns - len(row))
            rows.append({col: str(cell).strip() for col, cell in zip(columns, padded_row)})

    return rows


def read_all_spreadsheets(
    input_path: str,
    sheets_whitelist: list[str] = None,
    tabs_whitelist: list[str] = None,
    google_sheets_ids: list[str] = None,
    google_credentials_path: str = None,
) -> list[dict[str, str]]:
    """
    Read and combine all rows from every CSV, XLSX, and Google Sheets source.

    Parameters
    ----------
    input_path: str
        The local directory to read CSV / XLSX files from.

    sheets_whitelist: list[str], optional
        If provided, only process local files whose stem (filename without extension)
        appears in this list (case-insensitive).

    tabs_whitelist: list[str], optional
        If provided, only process tabs / worksheets whose names appear in this list
        (case-insensitive). Applies to both XLSX files and Google Sheets.

    google_sheets_ids: list[str], optional
        Google Sheets spreadsheet IDs or full URLs to fetch.

    google_credentials_path: str, optional
        Path to a Google service-account JSON key file. Falls back to
        GOOGLE_CREDENTIALS_PATH if not provided.

    Returns
    -------
    list[dict[str, str]]
        One dict per data row across all accepted sources, mapping column headers to
        stripped cell values.
    """

    rows = []
    sheets_whitelist_lower = [s.lower() for s in sheets_whitelist] if sheets_whitelist is not None else None

    def file_on_whitelist(filepath: str) -> bool:
        if sheets_whitelist_lower is None:
            return True
        stem = os.path.splitext(os.path.basename(filepath))[0]
        return stem.lower() in sheets_whitelist_lower

    for filepath in glob.glob(f"{input_path}/*.csv"):
        if not file_on_whitelist(filepath):
            continue
        rows.extend(read_rows_from_csv(filepath))

    for filepath in glob.glob(f"{input_path}/*.xlsx"):
        # Skip Excel lock files that appear while a workbook is open
        if os.path.basename(filepath).startswith("~$"):
            continue
        if not file_on_whitelist(filepath):
            continue
        rows.extend(read_rows_from_xlsx(filepath, tabs_whitelist))

    if google_sheets_ids:
        if not GOOGLE_SHEETS_AVAILABLE:
            log(
                "Google Sheets support requires the 'gspread' and 'google-auth' packages. "
                "Install them with:  pip install gspread google-auth"
            )
        else:
            credentials_path = google_credentials_path or GOOGLE_CREDENTIALS_PATH
            if not os.path.isfile(credentials_path):
                log(
                    f"Google credentials file not found at '{credentials_path}'. "
                    "Provide a service-account JSON key via --google-credentials."
                )
            else:
                scopes = [
                    "https://www.googleapis.com/auth/spreadsheets.readonly",
                    "https://www.googleapis.com/auth/drive.readonly",
                ]
                credentials = ServiceAccountCredentials.from_service_account_file(credentials_path, scopes=scopes)
                client = gspread.authorize(credentials)
                for id_or_url in google_sheets_ids:
                    spreadsheet_id = extract_google_spreadsheet_id(id_or_url)
                    log(f"Fetching Google Sheet '{spreadsheet_id}'...")
                    rows.extend(read_rows_from_google_sheet(client, spreadsheet_id, tabs_whitelist))

    return rows


def process_spreadsheets(
    card_names_whitelist: list[str] = None,
    card_sets_whitelist: list[str] = None,
    card_categories_whitelist: list[str] = None,
    oldest_date: datetime = None,
    latest_date: datetime = None,
    sort_by: tuple[tuple[str, Callable], tuple[str, Callable], tuple[str, Callable]] = None,
    sheets_whitelist: list[str] = None,
    tabs_whitelist: list[str] = None,
    google_sheets_ids: list[str] = None,
    google_credentials_path: str = None,
    no_spellbooks: bool = False,
    spellbooks_whitelist: list[str] = None,
) -> dict[str, dict[str, RegularCard]]:
    """
    Convert the card info on the input spreadsheets into dictionaries.

    Parameters
    ----------
    card_names_whitelist: list[str], optional
        The names of the cards to process. Process all of them by default.

    card_sets_whitelist: list[str], optional
        The names of the card sets to process. Process all of them by default.

    card_categories_whitelist: list[str], optional
        The names of the card categories to process. Process all of them by default.

    oldest_date: datetime, optional
        The earliest date to process cards from.

    latest_date: datetime, optional
        The latest date to process cards from.

    sort_by: tuple[tuple[str, Callable], tuple[str, Callable], tuple[str, Callable]], optional
        Which card sheet columns to sort the cards by, plus their default values.

    sheets_whitelist: list[str], optional
        The filenames (without extension) of the spreadsheet files to process.
        Process all of them by default.

    tabs_whitelist: list[str], optional
        The names of the XLSX tabs/sheets to process. Process all of them by default.
        Has no effect on CSV files.

    google_sheets_ids: list[str], optional
        Google Sheets spreadsheet IDs or URLs to fetch and include.

    google_credentials_path: str, optional
        Path to a Google service-account JSON key file.

    no_spellbooks: bool, default: False
        If True, don't generate any spellbook copies of cards; only their base versions are kept.

    spellbooks_whitelist: list[str], optional
        If given, only generate spellbook copies for these spellbooks, and only keep those copies
        (base versions and copies of other spellbooks are dropped). Has no effect if no_spellbooks
        is True.

    Returns
    -------
    dict[str, dict[str, RegularCard]]
        A dictionary of spreadsheets in the form { output_directory: spreadsheet }.
        Each spreadsheet is in the form { card_title: card }.
    """

    # Frame Layout to Subclass
    layout_to_subclass = {
        # Regular
        "regular": RegularCard,
        "regular split rules text": RegularSplitRulesText,
        # Transform
        "transform frontside": TransformFrontside,
        "transform backside": TransformBackside,
        # Modal
        "modal frontside": ModalFrontside,
        "modal backside": ModalBackside,
        "short modal frontside": ShortModalFrontside,
        "short modal backside": ShortModalBackside,
        # Split
        "regular split": RegularSplit,
        "regular fuse": RegularFuse,
        # Token
        "regular token": RegularToken,
        "textless token": TextlessToken,
        "short token": ShortToken,
        "tall token": TallToken,
        # Transform Token
        "regular token transform frontside": RegularTokenTransformFrontside,
        "regular token transform backside": RegularTokenTransformBackside,
        "textless token transform frontside": TextlessTokenTransformFrontside,
        "textless token transform backside": TextlessTokenTransformBackside,
        # Planeswalker
        "regular planeswalker": RegularPlaneswalker,
        # Saga
        "regular saga": RegularSaga,
        "transform saga": TransformSaga,
        # Class
        "regular class": RegularClass,
        # Adventure
        "regular adventure": RegularAdventure,
        # Omen
        "regular omen": RegularOmen,
        # Prepare
        "regular prepare": RegularPrepare,
        # Battle
        "battle": Battle,
        "transform battle": TransformBattle,
        # Room
        "regular room": RegularRoom,
        # Conspiracy
        "conspiracy": Conspiracy,
        # Dungeon
        "dungeon": Dungeon,
        "expanded dungeon": ExpandedDungeonGlobal,
        "expanded dungeon global": ExpandedDungeonGlobal,
        "expanded dungeon local": ExpandedDungeonLocal,
        # Edifice
        "regular edifice": RegularEdifice,
        # Showcase
        "regular transparent": RegularTransparent,
        "full text": FullText,
        "japan": Japan,
        "future shifted": FutureShifted,
        "zendikar": Zendikar,
        "sketch": Sketch,
        "playtest": Playtest,
        "pixel": Pixel,
        "monopoly": Monopoly,
        "coup": Coup,
        "chat": Chat,
        "poker": Poker,
        "breaking news": BreakingNews,
        # Showcase Meme
        "demotivational poster": DemotivationalPoster,
        # Showcase Promo
        "regular promo": RegularPromo,
        "extended promo": ExtendedPromo,
        "open house promo": OpenHousePromo,
        # Showcase Full Art Basic Lands
        "full art basic thb": FullArtBasicTHB,
        "full art basic snc": FullArtBasicSNC,
        # Showcase LOTR
        "lotr ring": RingLOTR,
        "lotr scroll": ScrollLOTR,
    }

    if oldest_date is None:
        oldest_date = datetime.min
    if latest_date is None:
        latest_date = datetime.max

    card_sets: dict[str, dict[str, RegularCard]] = {}

    raw_cards: dict[str, dict[str, str]] = {}
    for values in read_all_spreadsheets(
        INPUT_SPREADSHEETS_PATH,
        sheets_whitelist,
        tabs_whitelist,
        google_sheets_ids,
        google_credentials_path,
    ):
        card_title = values.get(CARD_TITLE, "")
        card_additional_titles = values.get(CARD_ADDITIONAL_TITLES, "")
        card_descriptor = values.get(CARD_DESCRIPTOR, "")
        card_key = get_card_key(card_title, card_additional_titles, card_descriptor)

        if len(card_title) == 0:
            continue

        raw_cards[card_key] = values

    def get_sorted_keys():
        if sort_by is not None:
            return sorted(
                raw_cards.keys(),
                key=lambda card_key: tuple(sort[1](raw_cards[card_key].get(sort[0], "")) for sort in sort_by),
            )
        return raw_cards.keys()

    sorted_keys = get_sorted_keys()

    # Replace missing columns in alternate cards with copies from their originals
    for card_key in sorted_keys:
        card = raw_cards[card_key]
        card_title = card.get(CARD_TITLE, None)
        card_additional_titles = card.get(CARD_ADDITIONAL_TITLES, None)
        card_descriptor = card.get(CARD_DESCRIPTOR, None)
        card_original_title = card.get(CARD_ORIGINAL, None)

        # skip if this isn't an alternate
        if len(card_descriptor) == 0 and len(card_original_title) == 0:
            continue

        original_card = None
        if len(card_original_title) > 0:
            original_card = raw_cards.get(card_original_title, None)
            if original_card is None:
                log(f"Could not find '{card_original_title}' as an original card of an alternate.")

        if original_card is None and len(card_descriptor) > 0:
            original_card = raw_cards.get(get_card_key(card_title, card_additional_titles), None)

        if original_card is not None:
            for key, value in card.items():
                if (
                    not isinstance(value, int)
                    and key
                    not in (
                        CARD_SET,
                        CARD_ARTIST,
                        CARD_OVERLAYS,
                        CARD_FRONTSIDE,
                        CARD_CATEGORY,
                        CARD_FRAME_LAYOUT_EXTRAS,
                        CARD_SPELLBOOKS,
                    )
                    and len(value) == 0
                ):
                    card[key] = original_card[key]
        else:
            log(f"Could not find '{card_title}' as an original card of an alternate.")

    expanded_cards: dict[str, dict[str, str]] = {}
    for key in sorted_keys:
        card = raw_cards[key]
        card_sets_raw = card.get(CARD_SET, "")

        set_names = [line.strip() for line in card_sets_raw.splitlines()]
        set_names = [set_name for set_name in set_names if len(set_name) > 0]
        if len(set_names) <= 1:
            card[CARD_ALL_SETS] = set_names
            expanded_cards[key] = card
            continue

        card_title = card.get(CARD_TITLE, "")
        card_additional_titles = card.get(CARD_ADDITIONAL_TITLES, "")
        card_descriptor = card.get(CARD_DESCRIPTOR, "")
        for set_name in set_names:
            clone = copy.deepcopy(card)
            clone[CARD_SET] = set_name
            clone[CARD_ALL_SETS] = set_names
            clone_key = get_card_key(card_title, card_additional_titles, card_descriptor, set_name)
            expanded_cards[clone_key] = clone
    raw_cards = expanded_cards

    # Resort now that alternates have all the correct columns
    sorted_keys = get_sorted_keys()

    # Add indices to all the cards, for collector info
    category_indices: dict[str, dict[str, int]] = {}
    for key in sorted_keys:
        card = raw_cards[key]
        if len(card.get(CARD_FRONTSIDE, "")) > 0:
            card[CARD_INDEX] = ""
            continue

        card_set = card.get(CARD_SET, "")
        if len(card_set) == 0:
            continue

        category = card.get(CARD_CATEGORY, "")
        if not category_indices.get(card_set, False):
            category_indices[card_set] = {}
        if not category_indices[card_set].get(category, False):
            category_indices[card_set][category] = 0
        category_indices[card_set][category] += 1
        card[CARD_INDEX] = str(category_indices[card_set][category])

    # Set largest index of all the cards for the footers
    for key in sorted_keys:
        card = raw_cards[key]
        category = card.get(CARD_CATEGORY, "")
        card_set = card.get(CARD_SET, "")
        if len(card_set) > 0 and len(category) > 0:
            card[CARD_FOOTER_LARGEST_INDEX] = category_indices[card_set][category]

    # Cull any cards not on the whitelist
    def card_on_card_name_whitelist(card_title: str, card_additional_titles: str, card_descriptor: str):
        if card_names_whitelist is None:
            return True
        raw_card_titles = [title.strip() for title in card_additional_titles.split("\n")] + [card_title]
        card_titles = []
        for raw_title in raw_card_titles:
            title = re.sub(r"{.*?}", "", raw_title)
            card_titles.append(title)

        for title in card_titles:
            for card_name in card_names_whitelist:
                if len(card_descriptor) > 0:
                    if (
                        card_name in f"{title} - {card_descriptor}"
                        or card_name in f"{card_title} - {title} - {card_descriptor}"
                    ):
                        return True
                elif card_name in title or card_name in f"{card_title} - {title}":
                    return True
        return False

    def card_on_set_whitelist(card_set: str):
        if card_sets_whitelist is None:
            return True
        return card_set.lower() in [set.lower() for set in card_sets_whitelist]

    def card_on_category_whitelist(card_category: str):
        if card_categories_whitelist is None:
            return True
        return card_category.lower() in [category.lower() for category in card_categories_whitelist]

    def card_within_date_range(card_creation_date: str):
        converted_creation_date = str_to_datetime(card_creation_date, None)
        return converted_creation_date is None or (oldest_date <= converted_creation_date <= latest_date)

    filtered_cards: dict[str, dict[str, str]] = {}
    for key, metadata in raw_cards.items():
        card_title = metadata.get(CARD_TITLE, "")
        card_additional_titles = metadata.get(CARD_ADDITIONAL_TITLES, "")
        card_descriptor = metadata.get(CARD_DESCRIPTOR, "")
        card_set = metadata.get(CARD_SET, "").lower()
        card_category = metadata.get(CARD_CATEGORY, "").lower()
        card_creation_date = metadata.get(CARD_CREATION_DATE)
        if (
            not card_on_card_name_whitelist(card_title, card_additional_titles, card_descriptor)
            or not card_on_set_whitelist(card_set)
            or not card_on_category_whitelist(card_category)
            or not card_within_date_range(card_creation_date)
        ):
            continue
        filtered_cards[key] = metadata

    # Give each card a class depending on its frame layout (and sort out its frame layout)
    for metadata in filtered_cards.values():
        frame_layout = metadata.get(CARD_FRAME_LAYOUT, "").lower()

        metadata[CARD_FRAME_LAYOUT_EXTRAS] = []
        card_frame_layout = metadata.get(CARD_FRAME_LAYOUT, "").lower()
        for extra_pattern in FRAME_LAYOUT_EXTRAS_LIST:
            extras = re.findall(extra_pattern, card_frame_layout)
            if len(extras) >= 1:
                metadata[CARD_FRAME_LAYOUT_EXTRAS].append(extras[-1].strip())
            for extra in extras:
                card_frame_layout = card_frame_layout.replace(extra, "")
        metadata[CARD_FRAME_LAYOUT] = card_frame_layout.strip()

        subclass = layout_to_subclass.get(metadata[CARD_FRAME_LAYOUT], RegularCard)

        card_set = metadata.get(CARD_SET, "")
        if card_set not in card_sets:
            os.makedirs(f"{OUTPUT_CARDS_PATH}/{card_set}", exist_ok=True)
            card_sets[card_set] = {}

        key = get_card_key(
            metadata.get(CARD_TITLE, ""),
            metadata.get(CARD_ADDITIONAL_TITLES, ""),
            metadata.get(CARD_DESCRIPTOR, ""),
        )
        card_sets[card_set][key] = subclass(metadata=metadata)

    def get_sorted_cards(card_set: str):
        return sorted(
            card_sets[card_set].values(),
            key=lambda card: tuple(sort[1](card.get_metadata(sort[0])) for sort in sort_by),
        )

    # Give each alternate card a subclass based on their frame layout (now that they have one)
    for card_set in card_sets:
        sorted_cards = get_sorted_cards(card_set)

        for card in sorted_cards:
            card_title = card.get_metadata(CARD_TITLE)
            card_additional_titles = card.get_metadata(CARD_ADDITIONAL_TITLES)
            card_descriptor = card.get_metadata(CARD_DESCRIPTOR)
            card_key = get_card_key(card_title, card_additional_titles, card_descriptor)
            card_original_title = card.get_metadata(CARD_ORIGINAL)

            # skip if this isn't an alternate
            if len(card_descriptor) == 0 and len(card_original_title) == 0:
                continue

            original_card = None
            if len(card_original_title) > 0:
                original_card = card_sets[card_set].get(card_original_title)
                if original_card is None:
                    log(f"Could not find '{card_original_title}' as an original card of an alternate.")

            if original_card is None and len(card_descriptor) > 0:
                original_card = card_sets[card_set].get(get_card_key(card_title, card_additional_titles))

            if original_card is not None:
                frame_layout = card.get_metadata(CARD_FRAME_LAYOUT).lower()
                subclass = layout_to_subclass.get(frame_layout, RegularCard)
                if subclass is not RegularCard:
                    card_sets[card_set][card_key] = subclass(metadata=card.metadata)
            else:
                log(f"Could not find '{card_title}' as an original card of an alternate.")

    for card_set in card_sets:
        sorted_cards = get_sorted_cards(card_set)

        # Add transform backsides to the transform cards and delete them from the dictionary
        # If the backside is missing any collector columns, copy them from the frontside
        for card in sorted_cards:
            frontside_title = card.get_metadata(CARD_FRONTSIDE)

            # Skip if this isn't a transform card
            if len(frontside_title) == 0:
                continue

            # Skip if it's not on the set whitelist
            if not card_on_set_whitelist(card_set):
                continue

            frontside_card = card_sets[card_set].get(frontside_title)
            if frontside_card is not None:
                for key, value in card.metadata.items():
                    if (
                        key
                        in (
                            CARD_INDEX,
                            CARD_CATEGORY,
                            CARD_RARITY,
                            CARD_CREATION_DATE,
                            CARD_LANGUAGE,
                            CARD_SPELLBOOKS,
                        )
                        and len(value) == 0
                    ):
                        card.set_metadata(key, frontside_card.get_metadata(key))
                frontside_card.set_metadata(CARD_BACKSIDES, card, append=True)
            else:
                log(f"Could not find '{frontside_title}' as a frontside.")

            card_title = card.get_metadata(CARD_TITLE)
            card_additional_titles = card.get_metadata(CARD_ADDITIONAL_TITLES)
            card_descriptor = card.get_metadata(CARD_DESCRIPTOR)
            card_key = get_card_key(card_title, card_additional_titles, card_descriptor)
            del card_sets[card_set][card_key]

    # Resolve expanded/global dungeons' cross-card {to=...}/{continues=...} targets (and, for
    # global dungeons, primary/part linkage) to the actual sibling card/room objects they name, now
    # that every card in each set has been constructed
    for card_set in card_sets:
        for card in card_sets[card_set].values():
            if isinstance(card, (ExpandedDungeonLocal, ExpandedDungeonGlobal)):
                card.link_siblings(card_sets[card_set])

    # Remove cards with blank creation dates, if date filtering is on
    if oldest_date > datetime.min or latest_date < datetime.max:
        for card_set in card_sets:
            for card_name, card in list(card_sets[card_set].items()):
                card_creation_date = card.get_metadata(CARD_CREATION_DATE)
                if len(card_creation_date) == 0:
                    del card_sets[card_set][card_name]

    if not no_spellbooks:
        for card_set in card_sets:
            sorted_cards = get_sorted_cards(card_set)
            new_cards: dict[str, RegularCard] = {}
            spellbook_indices: dict[str, int] = {}

            for card in sorted_cards:
                spellbooks_raw = card.get_metadata(CARD_SPELLBOOKS, "")
                if len(spellbooks_raw) == 0:
                    continue

                for line in spellbooks_raw.splitlines():
                    spellbook_name = line.strip()
                    if len(spellbook_name) == 0:
                        continue
                    if spellbooks_whitelist is not None and spellbook_name.lower() not in [
                        spellbook.lower() for spellbook in spellbooks_whitelist
                    ]:
                        continue

                    if spellbook_indices.get(spellbook_name, False):
                        spellbook_indices[spellbook_name] += 1
                    else:
                        spellbook_indices[spellbook_name] = 1

                    clone_metadata = copy.deepcopy(card.metadata)
                    clone_backsides = []
                    for backside in clone_metadata.get(CARD_BACKSIDES, []):
                        clone_backside_metadata = copy.deepcopy(backside.metadata)
                        clone_backside_metadata[CARD_CATEGORY] = spellbook_name
                        clone_backside_metadata[CARD_SPELLBOOK] = spellbook_name
                        clone_backside_metadata[CARD_INDEX] = str(spellbook_indices[spellbook_name])
                        clone_backsides.append(backside.__class__(metadata=clone_backside_metadata))
                    clone_metadata[CARD_BACKSIDES] = clone_backsides

                    clone_metadata[CARD_CATEGORY] = spellbook_name
                    clone_metadata[CARD_SPELLBOOK] = spellbook_name
                    clone_metadata[CARD_INDEX] = str(spellbook_indices[spellbook_name])

                    card_title = card.get_metadata(CARD_TITLE)
                    card_additional_titles = card.get_metadata(CARD_ADDITIONAL_TITLES)
                    card_descriptor = card.get_metadata(CARD_DESCRIPTOR)
                    spellbook_key = get_card_key(card_title, card_additional_titles, card_descriptor, spellbook_name)
                    new_cards[spellbook_key] = card.__class__(metadata=clone_metadata)

            for card in new_cards.values():
                card_spellbook = card.get_metadata(CARD_SPELLBOOK)
                card.set_metadata(CARD_FOOTER_LARGEST_INDEX, str(spellbook_indices[card_spellbook]))
                for backside in card.get_metadata(CARD_BACKSIDES):
                    backside.set_metadata(CARD_FOOTER_LARGEST_INDEX, str(spellbook_indices[card_spellbook]))

            if spellbooks_whitelist is not None:
                card_sets[card_set] = new_cards
            else:
                card_sets[card_set].update(new_cards)

    # If sorting is on, sort by the given columns
    if sort_by is not None:
        sorted_card_sets = {}
        for card_set in card_sets:
            sorted_card_sets[card_set] = dict(
                sorted(
                    card_sets[card_set].items(),
                    key=lambda card: tuple(sort[1](card[1].get_metadata(sort[0])) for sort in sort_by),
                )
            )
        return sorted_card_sets

    return card_sets


def render_cards(card_sets: dict[str, dict[str, RegularCard]]):
    for card_set, spreadsheet in card_sets.items():
        output_path = f"{OUTPUT_CARDS_PATH}/{card_set}"
        log(f"Processing set at '{output_path}'...")
        increase_log_indent()

        def render_card(card: RegularCard):
            card_category = card.get_metadata(CARD_CATEGORY)
            if card_category.lower() == "{skip}":
                return

            card_title = card.get_metadata(CARD_TITLE)
            card_additional_titles = card.get_metadata(CARD_ADDITIONAL_TITLES)
            card_descriptor = card.get_metadata(CARD_DESCRIPTOR)
            card_spellbook = card.get_metadata(CARD_SPELLBOOK)
            card_key = get_card_key(card_title, card_additional_titles, card_descriptor, card_spellbook)

            card.create_layers()
            final_card = card.render_card()
            final_card.save(f"{output_path}/{cardname_to_filename(card_key)}.png")
            final_card.close()

        for card in spreadsheet.values():
            card_title = card.get_metadata(CARD_TITLE)
            card_additional_titles = card.get_metadata(CARD_ADDITIONAL_TITLES)
            card_descriptor = card.get_metadata(CARD_DESCRIPTOR)
            card_spellbook = card.get_metadata(CARD_SPELLBOOK)
            card_key = get_card_key(card_title, card_additional_titles, card_descriptor, card_spellbook)

            log(f"Processing '{card_key}'...")
            increase_log_indent()

            render_card(card)

            for backside in card.get_metadata(CARD_BACKSIDES, []):
                backside_title = backside.get_metadata(CARD_TITLE)
                backside_additional_titles = backside.get_metadata(CARD_ADDITIONAL_TITLES)
                backside_descriptor = backside.get_metadata(CARD_DESCRIPTOR)
                backside_spellbook = card.get_metadata(CARD_SPELLBOOK)
                backside_key = get_card_key(
                    backside_title,
                    backside_additional_titles,
                    backside_descriptor,
                    backside_spellbook,
                )

                log(f"Processing '{backside_key}'...")
                increase_log_indent()

                render_card(backside)

                decrease_log_indent()

            decrease_log_indent()

        decrease_log_indent()

        log()


def render_tiled_cards(card_sets: dict[str, dict[str, RegularCard]], tile_nums: list[str] = None):
    tile_image_width = (MAX_TILING_WIDTH // CARD_TILE_WIDTH) * CARD_TILE_WIDTH
    tile_image_height = (MAX_TILING_HEIGHT // CARD_TILE_HEIGHT) * CARD_TILE_HEIGHT

    if tile_nums is not None:
        tile_num_pairs = []
        max_tile_num = {}

        for num in tile_nums:
            category, tile_num = num.split("-")
            converted_tile_num = str_to_int(tile_num)
            if converted_tile_num > 0 or tile_num == "*":
                tile_num_pairs.append((category, tile_num))
                if category not in max_tile_num or converted_tile_num > max_tile_num[category]:
                    max_tile_num[category] = str_to_int(tile_num, float("inf"))
    else:
        tile_num_pairs = None
        max_tile_num = None

    for card_set, spreadsheet in card_sets.items():
        output_path = f"{OUTPUT_TILES_PATH}/{card_set}"
        log(f"Processing set at '{output_path}'...")
        increase_log_indent()

        tile_image: dict[str, Image.Image] = {}
        tile_num: dict[str, int] = {}
        curr_width: dict[str, int] = {}
        curr_height: dict[str, int] = {}

        def tile_card(card: RegularCard):
            card_category = card.get_metadata(CARD_CATEGORY).lower()
            if card_category.lower() == "{skip}":
                return

            if not tile_image.get(card_category, False):
                tile_image[card_category] = Image.new("RGBA", (tile_image_width, tile_image_height), (0, 0, 0, 0))
                tile_num[card_category] = 1
                curr_width[card_category] = 0
                curr_height[card_category] = 0

            if (
                tile_num_pairs is not None
                and (card_category, str(tile_num[card_category])) not in tile_num_pairs
                and (card_category, "*") not in tile_num_pairs
            ):
                log("Not in provided tile nums. Skipping...")

                curr_width[card_category] += CARD_TILE_WIDTH
                if curr_width[card_category] > tile_image_width - CARD_TILE_WIDTH:
                    curr_width[card_category] = 0
                    curr_height[card_category] += CARD_TILE_HEIGHT
                if curr_height[card_category] > tile_image_height - CARD_TILE_HEIGHT:
                    curr_height[card_category] = 0
                    tile_num[card_category] += 1
                    if (
                        max_tile_num is not None
                        and card_category in max_tile_num
                        and tile_num[card_category] > max_tile_num[card_category]
                    ):
                        log(f"Reached end of requested tiles for {card_category}. Skipping remaining cards...")
                        return
                return

            card.create_layers()
            final_card = card.render_card()
            if card.FOOTER_ROTATION == 90:
                final_card = final_card.transpose(Image.Transpose.ROTATE_270)
            elif card.FOOTER_ROTATION == 270:
                final_card = final_card.transpose(Image.Transpose.ROTATE_90)
            final_card = final_card.resize((CARD_TILE_WIDTH, CARD_TILE_HEIGHT))

            if curr_width[card_category] > tile_image_width - CARD_TILE_WIDTH:
                curr_width[card_category] = 0
                curr_height[card_category] += CARD_TILE_HEIGHT
            if curr_height[card_category] > tile_image_height - CARD_TILE_HEIGHT:
                output_file_path = f"{output_path}/{card_category}/{tile_num[card_category]}.png"
                log(f"Saving {card_category} tile set to '{output_file_path}'...")
                os.makedirs(f"{output_path}/{card_category}", exist_ok=True)
                tile_image[card_category].save(output_file_path)
                tile_image[card_category].close()
                tile_image[card_category] = Image.new("RGBA", (tile_image_width, tile_image_height), (0, 0, 0, 0))
                curr_height[card_category] = 0
                tile_num[card_category] += 1
                if (
                    max_tile_num is not None
                    and card_category in max_tile_num
                    and tile_num[card_category] > max_tile_num[card_category]
                ):
                    log(f"Reached end of requested tiles for {card_category}. Skipping remaining cards...")
                    return

            tile_image[card_category] = paste_image(
                final_card,
                tile_image[card_category],
                (curr_width[card_category], curr_height[card_category]),
            )
            final_card.close()
            curr_width[card_category] += CARD_TILE_WIDTH

        for card in spreadsheet.values():
            card_title = card.get_metadata(CARD_TITLE)
            card_additional_titles = card.get_metadata(CARD_ADDITIONAL_TITLES)
            card_descriptor = card.get_metadata(CARD_DESCRIPTOR)
            card_spellbook = card.get_metadata(CARD_SPELLBOOK)
            card_key = get_card_key(card_title, card_additional_titles, card_descriptor, card_spellbook)

            log(f"Tiling '{card_key}'...")
            increase_log_indent()

            tile_card(card)

            for backside in card.get_metadata(CARD_BACKSIDES, []):
                backside_title = backside.get_metadata(CARD_TITLE)
                backside_additional_titles = backside.get_metadata(CARD_ADDITIONAL_TITLES)
                backside_descriptor = backside.get_metadata(CARD_DESCRIPTOR)
                backside_spellbook = card.get_metadata(CARD_SPELLBOOK)
                backside_key = get_card_key(
                    backside_title,
                    backside_additional_titles,
                    backside_descriptor,
                    backside_spellbook,
                )

                log(f"Tiling '{backside_key}'...")
                increase_log_indent()

                tile_card(backside)

                decrease_log_indent()

            decrease_log_indent()

        for category in tile_image.keys():
            if (
                (tile_num_pairs is None)
                or ((category, str(tile_num[category])) in tile_num_pairs)
                and (curr_width[category] > 0 or curr_height[category] > 0)
            ):
                os.makedirs(f"{output_path}/{category}", exist_ok=True)
                tile_image[category].save(f"{output_path}/{category}/{tile_num[category]}.png")

        decrease_log_indent()

        log()


def capture_art(card_sets: dict[str, dict[str, RegularCard]]):
    if card_sets is not None:

        frame_layout_map = {
            # Regular
            "regular": "regular",
            "regular split rules text": "regular",
            # Transform
            "transform frontside": "regular",
            "transform backside": "regular",
            # Modal
            "modal frontside": "regular",
            "modal backside": "regular",
            # Split TODO: SPLIT ART EXTRACTION POSSIBLE BUT NOT IMPLEMENTED
            "regular split": "split",
            "regular fuse": "split",
            # Token -- Not Allowed
            # Planeswalker -- Not Allowed
            # Vehicle
            "regular vehicle": "regular",
            # Saga
            "regular saga": "saga",
            "transform saga": "saga",
            # Class
            "regular class": "class",
            # Adventure
            "regular adventure": "regular",
            # Battle -- Not Allowed
            # Room -- Not Allowed
            # Showcase
            "sketch": "regular",
        }

        blacklisted_frames = (
            "regular/eldrazi",
            "regular/transform/front/borderless",
            "regular/transform/front/extended",
            "regular/transform/back/borderless",
            "regular/transform/back/extended",
            "regular/modal/borderless",
            "regular/modal/extended",
            "regular/modal/helper",
            "regular/modal/nickname",
            "regular/modal/short",
            "adventure/storybook/",
            "battle/",
            "planeswalker/",
            "room/",
            "token/",
            "showcase/draconic/",
            "showcase/full_text/",
            "showcase/future/",
            "showcase/japan/",
            "showcase/lotr/",
            "showcase/promo/",
            "showcase/transparent/",
            "showcase/zendikar/",
        )

        def frame_supported(frame_path: str) -> bool:
            for unsupported_path in blacklisted_frames:
                if frame_path[: len(unsupported_path)].strip() == unsupported_path.strip():
                    return False
            return True

        for output_path, spreadsheet in card_sets.items():
            output_path = f"{OUTPUT_ART_PATH}/{output_path[output_path.rfind("/") + 1:]}"
            log(f"Processing set at '{output_path}'...")
            os.makedirs(output_path, exist_ok=True)
            increase_log_indent()

            def extract_card_art(card: RegularCard):
                card_title = card.get_metadata(CARD_TITLE)
                card_additional_titles = card.get_metadata(CARD_ADDITIONAL_TITLES)
                card_descriptor = card.get_metadata(CARD_DESCRIPTOR)
                card_key = get_card_key(card_title, card_additional_titles, card_descriptor)

                card_frame_layout = card.get_metadata(CARD_FRAME_LAYOUT).lower()
                for extra in FRAME_LAYOUT_EXTRAS_LIST:
                    card_frame_layout = card_frame_layout.replace(extra, "")

                art_layout = frame_layout_map.get(card_frame_layout, "")
                if len(art_layout) == 0:
                    log(
                        f"Unsupported frame layout for card extraction: '{card_frame_layout}'. Skipping '{card_key}'..."
                    )
                    return

                card_frames = card.get_metadata(CARD_FRAMES)

                if not all(frame_supported(frame) for frame in card_frames.split("\n")):
                    log(f"Card uses unsupported frame for card extraction. Skipping '{card_key}'...")
                    return

                art_bounding_box = (
                    ART_X[art_layout],
                    ART_Y[art_layout],
                    ART_X[art_layout] + ART_WIDTH[art_layout],
                    ART_Y[art_layout] + ART_HEIGHT[art_layout],
                )

                card_filename = cardname_to_filename(card_key)
                card_path = f"{INPUT_CARDS_PATH}/{card_filename}.png"
                card_image = open_image(card_path)
                if card_image is None:
                    log(f"Couldn't find '{card_filename}' in '{card_path}'. Skipping '{card_key}'...")
                    return

                art = card_image.crop(art_bounding_box)
                base_image = Image.new("RGBA", (1500, 2100), (0, 0, 0, 0))
                base_image.paste(art, art_bounding_box)
                base_image.save(f"{output_path}/{card_filename}.png")
                log(f"Successfully extracted art from '{card_key}'.")

            for card in spreadsheet.values():
                extract_card_art(card)

                increase_log_indent()
                for backside in card.get_metadata(CARD_BACKSIDES, []):
                    extract_card_art(backside)
                decrease_log_indent()

            decrease_log_indent()

            log()

    else:
        art_bounding_box = (
            ART_X["regular"],
            ART_Y["regular"],
            ART_X["regular"] + ART_WIDTH["regular"],
            ART_Y["regular"] + ART_HEIGHT["regular"],
        )

        for card_path in glob.glob(f"{INPUT_CARDS_PATH}/*.png"):
            log(f"Extracting art from '{card_path}'...")
            card_image = open_image(card_path)
            art = card_image.crop(art_bounding_box)
            base_image = Image.new("RGBA", (1500, 2100), (0, 0, 0, 0))
            base_image.paste(art, art_bounding_box)
            card_name = card_path[card_path.rfind("\\") + 1 :]
            base_image.save(f"{OUTPUT_ART_PATH}/{card_name}")


def audit_art(card_sets: dict[str, dict[str, RegularCard]]):
    """
    Check if all the art in the art directory corresponds to a specific card, for the sets provided.
    """

    for output_path, spreadsheet in card_sets.items():
        art_path = f"{INPUT_ART_PATH}/{output_path[output_path.rfind("/") + 1:]}"
        log(f"Finding cards from the set without art in '{art_path}'...")
        increase_log_indent()

        card_filenames = []

        def check_card_art(card: RegularCard):
            card_title = card.get_metadata(CARD_TITLE)
            card_additional_titles = card.get_metadata(CARD_ADDITIONAL_TITLES)
            card_descriptor = card.get_metadata(CARD_DESCRIPTOR)
            card_key = get_card_key(card_title, card_additional_titles, card_descriptor)

            card_filename = cardname_to_filename(card_key)
            card_path = f"{art_path}/{card_filename}.png"

            card_frame_layout = card.get_metadata(CARD_FRAME_LAYOUT).lower()
            if "full text" in card_frame_layout or "monopoly" in card_frame_layout:
                card_filenames.append(card_filename)
                return

            if not os.path.isfile(card_path):
                log(f"No card art with filename '{card_filename}' for '{card_key}' in '{art_path}'...")
            else:
                card_filenames.append(card_filename)

        for card in spreadsheet.values():
            check_card_art(card)

            increase_log_indent()
            for backside in card.get_metadata(CARD_BACKSIDES, []):
                check_card_art(backside)
            decrease_log_indent()

        decrease_log_indent()

        log(f"Finding art in '{art_path}' that doesn't correspond to a card in the set...")
        increase_log_indent()

        for art_path in glob.glob(f"{art_path}/*.png"):
            filename = art_path[art_path.rfind("\\") + 1 : art_path.rfind(".png")]
            if filename not in card_filenames:
                log(f"'{filename}' in '{art_path}' has no associated card in the spreadsheets provided.")

        decrease_log_indent()

        log()


def main(
    action: str,
    card_names_whitelist: list[str] = None,
    card_sets_whitelist: list[str] = None,
    card_categories_whitelist: list[str] = None,
    oldest_date: datetime = None,
    latest_date: datetime = None,
    sort_by_date: bool = True,
    sort_by_orderer: bool = True,
    tile_nums: list[str] = None,
    sheets_whitelist: list[str] = None,
    tabs_whitelist: list[str] = None,
    google_sheets_ids: list[str] = None,
    google_credentials_path: str = None,
    no_spellbooks: bool = False,
    spellbooks_whitelist: list[str] = None,
):
    """
    Run the program.

    Parameters
    ----------
    action: str
        The action to perform (render cards, tile cards, etc.)

    card_names_whitelist: list[str], optional
        The names of the cards to perform the action on (including descriptors when applicable).
        By default, perform the action on all cards.

    card_sets_whitelist: list[str], optional
        The names of the sets to include cards from in performing the action on.
        By default, perform the action on all cards.

    card_categories_whitelist: list[str], optional
        The names of the categories to include cards of in performing the action on.
        By default, perform the action on all cards.

    oldest_date: datetime, optional
        The earliest date to process cards from.

    latest_date: datetime, optional
        The latest date to process cards from.

    sort_by_date: bool, default: False
        Whether to automatically sort the cards by date, then by name, or not.

    sort_by_orderer: bool, default: False
        Whether to automatically sort the cards by the orderer column, then by date, then name, or not.

    tile_nums: list[str], optional
        The category/number pairs for which tiles to process during the tiling action.
        Written as "{category}-{num}" like "regular-12". Processes all by default.

    sheets_whitelist: list[str], optional
        The filenames (without extension) of the spreadsheet files to process.
        Process all of them by default.

    tabs_whitelist: list[str], optional
        The names of the XLSX tabs/sheets to process. Process all of them by default.

    google_sheets_ids: list[str], optional
        Google Sheets spreadsheet IDs or URLs to fetch and include.

    google_credentials_path: str, optional
        Path to a Google service-account JSON key file.

    no_spellbooks: bool, default: False
        If True, don't generate any spellbook copies of cards; only their base versions are kept.

    spellbooks_whitelist: list[str], optional
        If given, only generate spellbook copies for these spellbooks, and only keep those copies
        (base versions and copies of other spellbooks are dropped). Has no effect if no_spellbooks
        is True.
    """

    sort_by: tuple[tuple[str, Callable], tuple[str, Callable], tuple[str, Callable]] = None
    if sort_by_date:
        sort_by = (
            (CARD_CREATION_DATE, str_to_datetime),
            (CARD_ORDERER, str_to_int),
            (CARD_TITLE, str),
        )
    if sort_by_orderer:
        if sort_by is not None:
            log("ERROR: User supplied multiple conflicting sort commands.")
            return
        sort_by = (
            (CARD_ORDERER, str_to_int),
            (CARD_CREATION_DATE, str_to_datetime),
            (CARD_TITLE, str),
        )

    reset_log()
    card_sets = process_spreadsheets(
        card_names_whitelist,
        card_sets_whitelist,
        card_categories_whitelist,
        oldest_date,
        latest_date,
        sort_by,
        sheets_whitelist,
        tabs_whitelist,
        google_sheets_ids,
        google_credentials_path,
        no_spellbooks,
        spellbooks_whitelist,
    )
    if action == ACTIONS[0]:
        log("Rendering cards...")
        render_cards(card_sets)
    elif action == ACTIONS[1]:
        log("Tiling cards...")
        render_tiled_cards(card_sets, tile_nums)
    elif action == ACTIONS[2]:
        log("Capturing art from existing cards...")
        capture_art(card_sets)
    elif action == ACTIONS[3]:
        log("Auditing art...")
        audit_art(card_sets)


def load_settings() -> dict:
    # Keys should match the argparse 'dest' names (e.g. "card_sets_whitelist", "action").
    if not os.path.isfile(SETTINGS_PATH):
        return {}
    with open(SETTINGS_PATH, "r", encoding="utf-8") as settings_file:
        settings = json.load(settings_file)
    for date_key in ("oldest_date", "latest_date"):
        if settings.get(date_key):
            settings[date_key] = [datetime.strptime(settings[date_key], "%m/%d/%Y")]
    return settings


if __name__ == "__main__":
    settings = load_settings()

    parser = argparse.ArgumentParser(description="Generate MTG cards based on the provided CSV file.")

    parser.add_argument(
        "-a",
        "--action",
        type=str,
        choices=ACTIONS,
        default=settings.get("action", ACTIONS[0]),
        dest="action",
        help=f"The action for the program to perform, one of {ACTIONS}.",
    )
    parser.add_argument(
        "-c",
        "--cards",
        nargs="+",
        default=settings.get("card_names_whitelist"),
        help=(
            "Only process the cards with these names (including tokens, alt arts, etc.). "
            "Accepts partial matches (i.e. 'Lotus' matches 'Black Lotus'). "
            "NOTE: If you're rendering alternates, you MUST render the original versions as well, or they will break."
        ),
        dest="card_names_whitelist",
    )
    parser.add_argument(
        "-s",
        "--sets",
        nargs="+",
        default=settings.get("card_sets_whitelist"),
        help=("Only process the cards in these sets."),
        dest="card_sets_whitelist",
    )
    parser.add_argument(
        "-cat",
        "--categories",
        nargs="+",
        default=settings.get("card_categories_whitelist"),
        help=("Only process the cards in these categories."),
        dest="card_categories_whitelist",
    )
    parser.add_argument(
        "-nsb",
        "--no-spellbooks",
        action="store_true",
        default=settings.get("no_spellbooks", False),
        help="Don't generate any spellbook copies of cards; only their base versions are rendered.",
        dest="no_spellbooks",
    )
    parser.add_argument(
        "-sb",
        "--spellbooks",
        nargs="+",
        default=settings.get("spellbooks_whitelist"),
        help=(
            "Only process cards from these spellbooks. Only the spellbook copies are processed, not the "
            "base versions. Has no effect if --no-spellbooks is set."
        ),
        dest="spellbooks_whitelist",
    )
    parser.add_argument(
        "-od",
        "--oldest-date",
        nargs=1,
        type=lambda string: datetime.strptime(string, "%m/%d/%Y"),
        default=settings.get("oldest_date"),
        help="The oldest card creation date to process cards from, in 'MM/DD/YYYY' format.",
        dest="oldest_date",
    )
    parser.add_argument(
        "-ld",
        "--latest-date",
        nargs=1,
        type=lambda string: datetime.strptime(string, "%m/%d/%Y"),
        default=settings.get("latest_date"),
        help="The latest card creation date to process cards from, in 'MM/DD/YYYY' format.",
        dest="latest_date",
    )
    parser.add_argument(
        "-sbd",
        "--sort-by-date",
        action="store_true",
        default=settings.get("sort_by_date", False),
        help=(
            "Whether to sort the provided cards by date (ascending) then card name (ascending)."
            "Sorting matters for what order cards are indexed on in their footer (and for the order when tiling)."
        ),
        dest="sort_by_date",
    )
    parser.add_argument(
        "-sbo",
        "--sort-by-orderer",
        action="store_true",
        default=settings.get("sort_by_orderer", False),
        help=(
            "Whether to sort the provided cards by the 'orderer' column or not."
            "This column is usually for ordering transform backsides, but it can be used to sort whole "
            "sheets if every card is given an 'orderer' value. Cards with the same 'orderer' value are "
            "sorted by date, then name. Cards without an 'orderer' value are considered 'orderer' 0."
        ),
        dest="sort_by_orderer",
    )
    parser.add_argument(
        "-tn",
        "--tile-nums",
        nargs="+",
        default=settings.get("tile_nums"),
        help=(
            "Only process the tiles with these categories and numbers, written as '{category}-{num}' like "
            "'regular-12'. You can also enter '{category}-*' to process all tiles from that category. "
            "Only relevant for the 'tile' action."
        ),
        dest="tile_nums",
    )
    parser.add_argument(
        "-sh",
        "--sheets",
        nargs="+",
        default=settings.get("sheets_whitelist"),
        help=(
            "Only process spreadsheet files whose names (without extension) match these values. "
            "Matches are case-insensitive and apply to both CSV and XLSX files."
        ),
        dest="sheets_whitelist",
    )
    parser.add_argument(
        "-t",
        "--tabs",
        nargs="+",
        default=settings.get("tabs_whitelist"),
        help=(
            "Only process tabs (sheets) with these names from XLSX files. "
            "Matches are case-insensitive. Has no effect on CSV files."
        ),
        dest="tabs_whitelist",
    )
    parser.add_argument(
        "-gs",
        "--google-sheets",
        nargs="+",
        default=settings.get("google_sheets_ids"),
        help=(
            "Google Sheets spreadsheet IDs or full URLs to fetch and process. "
            "Each spreadsheet must be shared with the service account. "
            "Requires a service-account JSON key file (see --google-credentials)."
        ),
        dest="google_sheets_ids",
    )
    parser.add_argument(
        "-gc",
        "--google-credentials",
        type=str,
        default=settings.get("google_credentials_path"),
        help=("Path to a Google service-account JSON key file. " f"Defaults to '{GOOGLE_CREDENTIALS_PATH}'."),
        dest="google_credentials_path",
    )

    args = parser.parse_args()
    main(
        args.action,
        args.card_names_whitelist,
        args.card_sets_whitelist,
        args.card_categories_whitelist,
        args.oldest_date[0] if args.oldest_date is not None else None,
        args.latest_date[0] if args.latest_date is not None else None,
        args.sort_by_date or (not args.sort_by_orderer),
        args.sort_by_orderer,
        args.tile_nums,
        args.sheets_whitelist,
        args.tabs_whitelist,
        args.google_sheets_ids,
        args.google_credentials_path,
        args.no_spellbooks,
        args.spellbooks_whitelist,
    )
