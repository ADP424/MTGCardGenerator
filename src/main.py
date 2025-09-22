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
    CARD_DESCRIPTOR,
    CARD_FRAME_LAYOUT,
    CARD_FRONTSIDE,
    CARD_INDEX,
    CARD_LANGUAGE,
    CARD_ORDERER,
    CARD_RARITY,
    CARD_SET,
    CARD_TITLE,
    INPUT_CARDS_PATH,
    INPUT_SPREADSHEETS_PATH,
    OUTPUT_ART_PATH,
    OUTPUT_CARDS_PATH,
)
from log import decrease_log_indent, increase_log_indent, log, reset_log
from model.RegularCard import RegularCard
from model.battle.Battle import Battle
from model.battle.TransformBattle import TransformBattle
from model.planeswalker.RegularPlaneswalker import RegularPlaneswalker
from model.room.RegularRoom import RegularRoom
from model.saga.RegularSaga import RegularSaga
from model.token.RegularToken import RegularToken
from model.token.ShortToken import ShortToken
from model.token.TallToken import TallToken
from model.token.TextlessToken import TextlessToken
from model.transform.backside.TransformBackside import TransformBackside
from model.transform.backside.TransformBacksideNoPip import TransformBacksideNoPip
from model.transform.frontside.TransformFrontside import TransformFrontside
from utils import cardname_to_filename, open_image


def process_spreadsheets(
    do_cards: bool = True,
    do_tokens: bool = True,
    do_basic_lands: bool = True,
    do_alts: bool = True,
    card_names_whitelist: list[str] = None,
) -> dict[str, dict[str, RegularCard]]:
    """
    Convert the card info on the input spreadsheets into dictionaries.

    Parameters
    ----------

    do_cards: bool, default : True
        Whether to process regular cards or skip them instead.

    do_tokens: bool, default : True
        Whether to process tokens or skip them instead.

    do_basic_lands: bool, default : True
        Whether to process basic land cards or skip them instead.

    do_alts: bool, default : True
        Whether to process alternate versions of cards or skip them instead.

    card_names_whitelist: list[str], optional
        The names of the cards to process. Process all of them by default.

    Returns
    -------
    dict[str, dict[str, RegularCard]]
        A dictionary of spreadsheets in the form { output_directory: spreadsheet }.
        Each spreadsheet is in the form { card_title: card }.
    """

    # Frame Layout to Subclass
    layout_to_subclass = {
        "regular": RegularCard,
        # Transform
        "transform frontside": TransformFrontside,
        "transform backside": TransformBackside,
        "transform backside no pip": TransformBacksideNoPip,
        # Token
        "regular token": RegularToken,
        "textless token": TextlessToken,
        "short token": ShortToken,
        "tall token": TallToken,
        # Planeswalker
        "regular planeswalker": RegularPlaneswalker,
        # Saga
        "regular saga": RegularSaga,
        # Battle
        "battle": Battle,
        "transform battle": TransformBattle,
        # Room
        "regular room": RegularRoom,
    }

    card_spreadsheets: dict[str, dict[str, RegularCard]] = {}

    for spreadsheet_path in glob.glob(f"{INPUT_SPREADSHEETS_PATH}/*.csv"):
        if spreadsheet_path.rfind("-") >= 0:
            output_path = (
                f"{OUTPUT_CARDS_PATH}/"
                f"{spreadsheet_path[spreadsheet_path.rfind("\\") + 1 : spreadsheet_path.rfind("-") - 1]}"
            )
        else:
            output_path = (
                f"{OUTPUT_CARDS_PATH}/"
                f"{spreadsheet_path[spreadsheet_path.rfind("\\") + 1 : spreadsheet_path.rfind(".")]}"
            )
        os.makedirs(output_path, exist_ok=True)
        card_spreadsheets[output_path] = {}
        with open(spreadsheet_path, "r", encoding="utf8") as cards_sheet:
            cards_sheet_reader = csv.reader(cards_sheet)
            columns = next(cards_sheet_reader)
            for row in cards_sheet_reader:
                values = dict(zip(columns, [element.strip() for element in row]))
                card_title = values.get(CARD_TITLE, "").replace("\n", "{N}")
                values[CARD_TITLE] = card_title
                card_descriptor = values.get(CARD_DESCRIPTOR, "")
                card_key = f"{card_title}{f" - {card_descriptor}" if len(card_descriptor) > 0 else ""}"
                if len(card_title) == 0:
                    continue
                frame_layout = values.get(CARD_FRAME_LAYOUT, "").lower()
                subclass = layout_to_subclass.get(frame_layout, RegularCard)
                card_spreadsheets[output_path][card_key] = subclass(metadata=values)

        def str_to_int(string: str, default: int) -> int:
            try:
                return int(string)
            except ValueError:
                return default

        def str_to_datetime(string: str, default: datetime) -> datetime:
            try:
                return datetime.strptime(string, "%m/%d/%Y")
            except ValueError:
                return default

        def get_sorted_cards():
            return sorted(
                card_spreadsheets[output_path].values(),
                key=lambda card: (
                    str_to_datetime(card.get_metadata(CARD_CREATION_DATE), datetime(MINYEAR, 1, 1)),
                    str_to_int(card.get_metadata(CARD_ORDERER), 0),
                    card.get_metadata(CARD_TITLE),
                ),
            )

        sorted_cards = get_sorted_cards()

        # Add indices to all the cards, for collector info
        category_indices: dict[str, int] = {}
        for card in sorted_cards:
            if len(card.get_metadata(CARD_FRONTSIDE)) > 0:
                card.set_metadata(CARD_INDEX, "")
                continue

            category = card.get_metadata(CARD_CATEGORY)
            if not category_indices.get(category, False):
                category_indices[category] = 0
            category_indices[category] += 1
            card.set_metadata(CARD_INDEX, str(category_indices[category]))

        # Set largest index to all the cards for the footers
        for card in sorted_cards:
            card.footer_largest_index = category_indices[card.get_metadata(CARD_CATEGORY)]

        # Give each alternate card a subclass based on their frame layout (now that they have one)
        # Also replace empty columns in alternates with their original card's values
        for card in sorted_cards:
            card_title = card.get_metadata(CARD_TITLE)
            descriptor = card.get_metadata(CARD_DESCRIPTOR)
            card_key = f"{card_title}{f" - {descriptor}" if len(descriptor) > 0 else ""}"

            # skip if this isn't an alternate
            if len(descriptor) == 0:
                continue

            original_card = card_spreadsheets[output_path].get(card_title)
            if original_card is not None:
                for key, value in card.metadata.items():
                    if len(value) == 0:
                        card.set_metadata(key, original_card.get_metadata(key))
                frame_layout = card.get_metadata(CARD_FRAME_LAYOUT).lower()
                subclass = layout_to_subclass.get(frame_layout, RegularCard)
                if subclass is not RegularCard:
                    card_spreadsheets[output_path][card_key] = subclass(metadata=card.metadata)
            else:
                log(f"Could not find '{card_title}' as an original card of an alternate.")

        sorted_cards = get_sorted_cards()

        # Add transform backsides to the transform cards and delete them from the dictionary
        # If the backside is missing any collector columns, copy them from the frontside
        for card in sorted_cards:
            frontside_title = card.get_metadata(CARD_FRONTSIDE)

            # Skip if this isn't a transform card
            if len(frontside_title) == 0:
                continue

            frontside_card = card_spreadsheets[output_path].get(frontside_title)
            if frontside_card is not None:
                for key, value in card.metadata.items():
                    if (
                        key in (CARD_INDEX, CARD_RARITY, CARD_CREATION_DATE, CARD_SET, CARD_LANGUAGE)
                        and len(value) == 0
                    ):
                        card.set_metadata(key, frontside_card.get_metadata(key))
                frontside_card.set_metadata(CARD_BACKSIDES, card, append=True)
            else:
                log(f"Could not find '{frontside_title}' as a frontside.")

            card_title = card.get_metadata(CARD_TITLE)
            card_descriptor = card.get_metadata(CARD_DESCRIPTOR)
            card_key = f"{card_title}{f" - {card_descriptor}" if len(card_descriptor) > 0 else ""}"
            del card_spreadsheets[output_path][card_key]

        # Remove any cards that aren't on the whitelist
        # We have to do this last so alternates can still read their info off the original
        for card_key, card in list(card_spreadsheets[output_path].items()):
            card_category = card.get_metadata(CARD_CATEGORY)
            if (
                (not do_cards and card_category.lower() == "regular")
                or (not do_tokens and card_category.lower() == "token")
                or (not do_basic_lands and card_category.lower() == "basic land")
                or (not do_alts and card_category.lower() == "alternate")
                or (card_names_whitelist is not None and card_key not in card_names_whitelist)
            ):
                del card_spreadsheets[output_path][card_key]

            backsides = card.get_metadata(CARD_BACKSIDES, [])
            idx = 0
            while idx < len(backsides):
                backside_title = backsides[idx].get_metadata(CARD_TITLE)
                backside_descriptor = backsides[idx].get_metadata(CARD_DESCRIPTOR)
                backside_key = f"{backside_title}{f" - {backside_descriptor}" if len(backside_descriptor) > 0 else ""}"
                if card_names_whitelist is not None and backside_key not in card_names_whitelist:
                    backsides.pop(idx)
                    idx -= 1
                idx += 1

    return card_spreadsheets


def render_cards(card_spreadsheets: dict[str, dict[str, RegularCard]]):
    for output_path, spreadsheet in card_spreadsheets.items():
        log(f"Processing spreadsheet at '{output_path}'...")
        increase_log_indent()

        for card in spreadsheet.values():
            card_title = card.get_metadata(CARD_TITLE)
            card_descriptor = card.get_metadata(CARD_DESCRIPTOR)
            card_key = f"{card_title}{f" - {card_descriptor}" if len(card_descriptor) > 0 else ""}"

            log(f"Processing '{card_key}'...")
            increase_log_indent()

            card.create_layers()
            final_card = card.render_card()
            final_card.save(f"{output_path}/{cardname_to_filename(card_key)}.png")

            for backside in card.get_metadata(CARD_BACKSIDES, []):
                backside_title = backside.metadata.get(CARD_TITLE, "")
                backside_descriptor = backside.get_metadata(CARD_DESCRIPTOR)
                backside_key = f"{backside_title}{f" - {backside_descriptor}" if len(backside_descriptor) > 0 else ""}"

                log(f"Processing '{backside_key}'...")
                increase_log_indent()

                backside.create_layers(create_rarity_symbol_layer=False)
                final_backside = backside.render_card()
                final_backside.save(f"{output_path}/{cardname_to_filename(backside_key)}.png")

                decrease_log_indent()

            decrease_log_indent()

        decrease_log_indent()

        log()


def capture_art():
    for card_path in glob.glob(f"{INPUT_CARDS_PATH}/*.png"):
        log(f"Extracting art from '{card_path}'...")

        card_image = open_image(card_path)
        art_bounding_box = (
            ART_X,
            ART_Y,
            ART_X + ART_WIDTH,
            ART_Y + ART_HEIGHT,
        )
        art = card_image.crop(art_bounding_box)
        base_image = Image.new("RGBA", (1500, 2100), (0, 0, 0, 0))
        base_image.paste(art, art_bounding_box)
        card_name = card_path[card_path.rfind("\\") + 1 :]
        base_image.save(f"{OUTPUT_ART_PATH}/{card_name}")


def main(
    action: str,
    do_cards: bool = True,
    do_tokens: bool = True,
    do_basic_lands: bool = True,
    do_alts: bool = True,
    card_names_whitelist: list[str] = None,
):
    """
    Run the program.

    Parameters
    ----------
    action: str
        The action to perform (render cards, tile cards, etc.)

    do_cards: bool, default : True
        Whether to perform the action on regular cards or skip them instead.

    do_tokens: bool, default : True
        Whether to perform the action on tokens or skip them instead.

    do_basic_lands: bool, default : True
        Whether to perform the action on basic land cards or skip them instead.

    do_alts: bool, default : True
        Whether to perform the action on alternate versions of cards or skip them instead.

    card_names_whitelist: list[str], optional
        The names of the cards to perform the action on (including descriptors when applicable).
        By default, perform the action on all cards.
    """

    reset_log()
    if action == ACTIONS[0]:
        log("Rendering cards...")
        card_spreadsheets = process_spreadsheets(do_cards, do_tokens, do_basic_lands, do_alts, card_names_whitelist)
        render_cards(card_spreadsheets)
    elif action == ACTIONS[1]:
        pass  # TODO
    elif action == ACTIONS[2]:
        log("Capturing art from existing cards...")
        capture_art()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate MTG cards based on the provided CSV file.")

    parser.add_argument(
        "-a" "--action",
        type=str,
        choices=ACTIONS,
        default=ACTIONS[0],
        dest="action",
        help=f"The action for the program to perform, one of {ACTIONS}.",
    )
    parser.add_argument(
        "-nc",
        "--no-cards",
        action="store_false",
        help="Skip processing the regular cards.",
        dest="cards",
    )
    parser.add_argument(
        "-nt",
        "--no-tokens",
        action="store_false",
        help="Skip processing the tokens.",
        dest="tokens",
    )
    parser.add_argument(
        "-nbl",
        "--no-basic-lands",
        action="store_false",
        help="Skip processing the basic lands.",
        dest="basic_lands",
    )
    parser.add_argument(
        "-naa",
        "--no-alt-arts",
        action="store_false",
        help="Skip processing the alternate arts of cards.",
        dest="alt_arts",
    )
    parser.add_argument(
        "-c",
        "--cards",
        nargs="+",
        help="Only process the cards with these names (including tokens, alt arts, etc.). Use '{N}' in place of newlines.",
        dest="card_names_whitelist",
    )

    args = parser.parse_args()
    main(
        args.action,
        args.cards,
        args.tokens,
        args.basic_lands,
        args.alt_arts,
        args.card_names_whitelist,
    )
