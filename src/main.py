import argparse
import csv
import glob
import os
from constants import CARD_TITLE, CHAR_TO_TITLE_CHAR, INPUT_SPREADSHEETS_PATH, OUTPUT_CARDS_PATH
from log import log, reset_log
from model.Card import Card


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
        output_path = f"{OUTPUT_CARDS_PATH}/{spreadsheet_path[spreadsheet_path.rfind("\\") + 1 : spreadsheet_path.rfind(".")]}"
        os.makedirs(output_path, exist_ok=True)
        card_spreadsheets[output_path] = {}
        with open(spreadsheet_path, "r", encoding="utf8") as cards_sheet:
            cards_sheet_reader = csv.reader(cards_sheet)
            columns = next(cards_sheet_reader)
            for row in cards_sheet_reader:
                values = dict(zip(columns, row))
                card_title = values.get(CARD_TITLE, "")
                card_spreadsheets[output_path][card_title] = Card(metadata=values)

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


def main():
    reset_log()
    card_spreadsheets = process_spreadsheets()
    for output_path, spreadsheet in card_spreadsheets.items():
        for card in spreadsheet.values():
            log(f"\nProcessing {card.metadata[CARD_TITLE]}...")
            card.create_frame_layers()
            card.create_text_layers()
            final_card = card.render_card()
            final_card.save(f"{output_path}/{cardname_to_filename(card.metadata[CARD_TITLE])}.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate MTG cards based on the provided CSV file.")
    main()
