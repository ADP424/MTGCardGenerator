import argparse
import csv
from constants import CARD_CATEGORY, CARD_TITLE, CARDS_SPREADSHEET, CHAR_TO_TITLE_CHAR
from log import log, reset_log
from model.Card import Card


def process_spreadsheet() -> dict[str, Card]:
    """
    Convert the card info on the input spreadsheet into a dictionary.

    Returns
    -------
    dict[str, Card]
        The dictionary of card info, in the form `{card_name: Card}`
    """

    cards: dict[str, Card] = {}
    transform_backsides: dict[str, Card] = {}
    with open(CARDS_SPREADSHEET, "r", encoding="utf8") as cards_sheet:
        cards_sheet_reader = csv.reader(cards_sheet)
        columns = next(cards_sheet_reader)
        for row in cards_sheet_reader:

            values = dict(zip(columns, row))
            card_title = values.get(CARD_TITLE, "")
            card_category = values.get(CARD_CATEGORY, "")

            if card_category == "Regular":
                cards[card_title] = Card(metadata=values)
            elif card_category == "Transform Backside":
                transform_backsides[card_title] = Card(metadata=values)

    for backside in transform_backsides.values():
        pass  # TODO: add TF backsides to metadata of card they're the back of

    return cards


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
    cards = process_spreadsheet()
    for card in cards.values():
        log(f"Processing {card.metadata[CARD_TITLE]}...")
        card.create_frame_layers()
        card.create_text_layers()
        final_card = card.render_card()
        final_card.save(f"processed_cards/{cardname_to_filename(card.metadata[CARD_TITLE])}.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate MTG cards based on the provided CSV file.")
    main()
