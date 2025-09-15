import argparse
import csv
import glob
import os

from PIL import Image
from datetime import MINYEAR, datetime

from constants import (
    ACTIONS,
    ART_HEIGHT,
    ART_WIDTH,
    ART_X,
    ART_Y,
    CARD_BACKSIDES,
    CARD_CATEGORY,
    CARD_CREATION_DATE,
    CARD_FRONTSIDE,
    CARD_INDEX,
    CARD_LANGUAGE,
    CARD_ORDERER,
    CARD_RARITY,
    CARD_SET,
    CARD_TITLE,
    CHAR_TO_TITLE_CHAR,
    INPUT_CARDS_PATH,
    INPUT_SPREADSHEETS_PATH,
    OUTPUT_ART_PATH,
    OUTPUT_CARDS_PATH,
)
from log import decrease_log_indent, increase_log_indent, log, reset_log
from model.Card import Card
from utils import open_image


def process_spreadsheets() -> dict[str, dict[str, Card]]:
    """
    Convert the card info on the input spreadsheets into dictionaries.

    Returns
    -------
    dict[str, dict[str, Card]]
        A dictionary of spreadsheets in the form { output_directory: spreadsheet }.
        Each spreadsheet is in the form { card_title: card }.
    """

    card_spreadsheets: dict[str, dict[str, Card]] = {}

    for spreadsheet_path in glob.glob(f"{INPUT_SPREADSHEETS_PATH}/*.csv"):
        if spreadsheet_path.rfind("-") >= 0:
            output_path = f"{OUTPUT_CARDS_PATH}/{spreadsheet_path[spreadsheet_path.rfind("\\") + 1 : spreadsheet_path.rfind("-") - 1]}"
        else:
            output_path = f"{OUTPUT_CARDS_PATH}/{spreadsheet_path[spreadsheet_path.rfind("\\") + 1 : spreadsheet_path.rfind(".")]}"
        os.makedirs(output_path, exist_ok=True)
        card_spreadsheets[output_path] = {}
        with open(spreadsheet_path, "r", encoding="utf8") as cards_sheet:
            cards_sheet_reader = csv.reader(cards_sheet)
            columns = next(cards_sheet_reader)
            for row in cards_sheet_reader:
                values = dict(zip(columns, [element.strip() for element in row]))
                card_title = values.get(CARD_TITLE, "")
                card_spreadsheets[output_path][card_title] = Card(metadata=values)

        def str_to_int(string: str, default: int) -> int:
            try:
                return int(string)
            except Exception:
                return default

        def str_to_datetime(string: str, default: datetime) -> datetime:
            try:
                return datetime.strptime(card.metadata.get(CARD_CREATION_DATE, datetime(MINYEAR, 1, 1)), "%m/%d/%Y")(
                    string
                )
            except Exception:
                return default

        sorted_cards = sorted(
            card_spreadsheets[output_path].values(),
            key=lambda card: (
                str_to_datetime(card.metadata.get(CARD_CREATION_DATE), datetime(MINYEAR, 1, 1)),
                str_to_int(card.metadata.get(CARD_ORDERER), 0),
                card.metadata.get(CARD_TITLE, ""),
            ),
        )

        # Add indices to all the cards, for collector info
        category_indices: dict[str, int] = {}
        for card in sorted_cards:
            if len(card.metadata.get(CARD_FRONTSIDE, "")) > 0:
                card.add_metadata(CARD_INDEX, "")
                continue

            category = card.metadata.get(CARD_CATEGORY, "")
            if not category_indices.get(category, False):
                category_indices[category] = 0
            category_indices[category] += 1
            card.add_metadata(CARD_INDEX, str(category_indices[category]))

        # Add transform backsides to the transform cards
        # If the backside is missing any collector columns, copy them from the frontside
        for card in sorted_cards:
            frontside_title = card.metadata.get(CARD_FRONTSIDE, "")
            if len(frontside_title) == 0:
                continue
            frontside_card = card_spreadsheets[output_path].get(frontside_title)
            if frontside_card is not None:
                for key, value in card.metadata.items():
                    if (
                        key in (CARD_INDEX, CARD_RARITY, CARD_CREATION_DATE, CARD_SET, CARD_LANGUAGE)
                        and len(value) == 0
                    ):
                        card.add_metadata(key, frontside_card.get_metadata(key))
                frontside_card.add_metadata(CARD_BACKSIDES, card, append=True)
                del card_spreadsheets[output_path][card.get_metadata(CARD_TITLE, "")]
            else:
                log(f"Could not find '{frontside_title}' as a frontside.")

    return card_spreadsheets


def cardname_to_filename(card_name: str) -> str:
    """
    Return `card_name` with all characters not allowed in a file name replaced.

    Parameters
    ----------
    card_name: str
        The card name to convert to a legal file name.

    Returns
    -------
    str
        The card name converted to a legal file name.
    """

    file_name = card_name.replace("’", "'")
    for bad_char in CHAR_TO_TITLE_CHAR.keys():
        file_name = file_name.replace(bad_char, CHAR_TO_TITLE_CHAR[bad_char])
    return file_name


def render_cards():
    card_spreadsheets = process_spreadsheets()
    for output_path, spreadsheet in card_spreadsheets.items():
        log(f"Processing spreadsheet at '{output_path}'...")
        increase_log_indent()

        for card in spreadsheet.values():
            card_title = card.metadata.get(CARD_TITLE, "")

            log(f"Processing {card_title}...")
            increase_log_indent()

            card.create_layers()
            final_card = card.render_card()
            final_card.save(f"{output_path}/{cardname_to_filename(card_title)}.png")

            for backside in card.metadata.get(CARD_BACKSIDES, []):
                backside_title = backside.metadata.get(CARD_TITLE, "")

                log(f"Processing {backside_title}...")
                increase_log_indent()

                backside.create_layers(create_rarity_symbol_layer=False)
                final_backside = backside.render_card()
                final_backside.save(f"{output_path}/{cardname_to_filename(backside_title)}.png")

                decrease_log_indent()

            decrease_log_indent()

        decrease_log_indent()

        log()


def capture_art():
    for card_path in glob.glob(f"{INPUT_CARDS_PATH}/*.png"):
        log(f"Extracting art from '{card_path}'...")

        card_image = open_image(card_path)
        art = card_image.crop((ART_X, ART_Y, ART_X + ART_WIDTH, ART_Y + ART_HEIGHT))
        card_name = card_path[card_path.rfind("\\") + 1:]
        art.save(f"{OUTPUT_ART_PATH}/{card_name}")


def main(action: str):
    """
    Run the program.
    
    Parameters
    ----------
    action: str
        The action to perform (render cards, tile cards, etc.)
    """

    reset_log()
    if action == ACTIONS[0]:
        render_cards()
    elif action == ACTIONS[1]:
        pass # TODO
    elif action == ACTIONS[2]:
        capture_art()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate MTG cards based on the provided CSV file.")

    parser.add_argument(
        "-a"
        "--action",
        type=str,
        choices=ACTIONS,
        default=ACTIONS[0],
        dest="action",
        help=f"The action for the program to perform, one of {ACTIONS}."
    )

    args = parser.parse_args()
    main(args.action)
