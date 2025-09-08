import csv
from PIL import Image
from constants import CARD_CATEGORY, CARD_TITLE, CARDS_SPREADSHEET, CHAR_TO_TITLE_CHAR
from log import log
from model.Card import Card


# def get_token_full_name(token: dict[str, str]) -> str:
#     color = token[CARD_COLOR]
#     token_color = ""
#     if "Colorless" in color:
#         token_color = "Colorless "
#     else:
#         for char in color.strip():
#             try:
#                 token_color += f"{COLORS[char]} "
#             except:
#                 log(f"""Token "{token[CARD_NAME]}" has an invalid color identity.""")
#                 token_color = ""
#                 break

#     if len(token_color) == 0:
#         log(f"""Token "{token[CARD_NAME]}" has an invalid color identity.""")
#         return None

#     token_descriptor = token[DESCRIPTOR].strip()
#     if len(token_descriptor) > 0:
#         token_descriptor = f" - {token_descriptor}"

#     token_supertypes = token[CARD_SUPERTYPES]
#     token_types = token[CARD_TYPES]
#     return f"{token_color}{token_supertypes} {token[CARD_NAME]} {token_types}{token_descriptor}"


def process_spreadsheet() -> dict[str, Card]:
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
    file_name = card_name.replace("’", "'")
    for bad_char in CHAR_TO_TITLE_CHAR.keys():
        file_name = file_name.replace(bad_char, CHAR_TO_TITLE_CHAR[bad_char])
    return file_name


def open_card_file(file_name: str, card_path: str = "unprocessed_cards/") -> Image.Image | None:
    try:

        if len(file_name) > 0:
            base_card = Image.open(f"cards/{card_path}{file_name}.png")
        else:
            return None

    except FileNotFoundError:

        try:
            new_file_name = file_name.replace("'", "’")
            base_card = Image.open(f"cards/{card_path}{new_file_name}.png")
        except FileNotFoundError:
            log(f"""Couldn't find "{file_name}" in "{card_path}".""")
            return None

    return base_card
