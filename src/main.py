import argparse
import csv
import glob
import os
import re
from PIL import Image

from datetime import MINYEAR, datetime

from constants import (
    ACTIONS,
    ART_HEIGHT,
    ART_WIDTH,
    ART_X,
    ART_Y,
    CARD_ADDITIONAL_TITLES,
    CARD_ARTIST,
    CARD_BACKSIDES,
    CARD_CATEGORY,
    CARD_CREATION_DATE,
    CARD_DESCRIPTOR,
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
    CARD_TILE_HEIGHT,
    CARD_TILE_WIDTH,
    CARD_TITLE,
    FRAME_LAYOUT_EXTRAS_LIST,
    INPUT_ART_PATH,
    INPUT_CARDS_PATH,
    INPUT_SPREADSHEETS_PATH,
    MAX_TILING_HEIGHT,
    MAX_TILING_WIDTH,
    OUTPUT_ART_PATH,
    OUTPUT_CARDS_PATH,
    OUTPUT_TILES_PATH,
)
from log import decrease_log_indent, increase_log_indent, log, reset_log
from model.modal.ModalBackside import ModalBackside
from model.modal.ModalFrontside import ModalFrontside
from model.modal.short.ShortModalBackside import ShortModalBackside
from model.modal.short.ShortModalFrontside import ShortModalFrontside
from model.regular.RegularCard import RegularCard
from model.adventure.RegularAdventure import RegularAdventure
from model.battle.Battle import Battle
from model.battle.TransformBattle import TransformBattle
from model.mtg_class.RegularClass import RegularClass
from model.planeswalker.RegularPlaneswalker import RegularPlaneswalker
from model.regular.RegularSplitRulesText import RegularSplitRulesText
from model.room.RegularRoom import RegularRoom
from model.saga.RegularSaga import RegularSaga
from model.saga.TransformSaga import TransformSaga
from model.showcase.FullText import FullText
from model.showcase.FutureShifted import FutureShifted
from model.showcase.Japan import Japan
from model.showcase.Sketch import Sketch
from model.showcase.Zendikar import Zendikar
from model.showcase.lotr.Ring import RingLOTR
from model.showcase.lotr.Scroll import ScrollLOTR
from model.showcase.promo.ExtendedPromo import ExtendedPromo
from model.showcase.promo.OpenHousePromo import OpenHousePromo
from model.showcase.promo.RegularPromo import RegularPromo
from model.showcase.transparent.RegularTransparent import RegularTransparent
from model.split.RegularSplit import RegularSplit
from model.split.fuse.RegularFuse import RegularFuse
from model.token.RegularToken import RegularToken
from model.token.ShortToken import ShortToken
from model.token.TallToken import TallToken
from model.token.TextlessToken import TextlessToken
from model.token.transform.backside.RegularTokenTransformBackside import RegularTokenTransformBackside
from model.token.transform.backside.TextlessTokenTransformBackside import TextlessTokenTransformBackside
from model.token.transform.frontside.RegularTokenTransformFrontside import RegularTokenTransformFrontside
from model.token.transform.frontside.TextlessTokenTransformFrontside import TextlessTokenTransformFrontside
from model.transform.TransformBackside import TransformBackside
from model.transform.TransformFrontside import TransformFrontside
from utils import cardname_to_filename, get_card_key, open_image, paste_image, str_to_datetime, str_to_int


def process_spreadsheets(
    card_names_whitelist: list[str] = None,
    card_sets_whitelist: list[str] = None,
    card_categories_whitelist: list[str] = None,
    sort: bool = True,
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

    sort: bool, default: True
        Whether to sort the sheet by date, then by name, or not.

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
        # Battle
        "battle": Battle,
        "transform battle": TransformBattle,
        # Room
        "regular room": RegularRoom,
        # Showcase
        "regular transparent": RegularTransparent,
        "full text": FullText,
        "japan": Japan,
        "future shifted": FutureShifted,
        "zendikar": Zendikar,
        "sketch": Sketch,
        # Showcase Promo
        "regular promo": RegularPromo,
        "extended promo": ExtendedPromo,
        "open house promo": OpenHousePromo,
        # Showcase LOTR
        "lotr ring": RingLOTR,
        "lotr scroll": ScrollLOTR,
    }

    card_sets: dict[str, dict[str, RegularCard]] = {}

    raw_cards: dict[str, dict[str, str]] = {}
    for spreadsheet_path in glob.glob(f"{INPUT_SPREADSHEETS_PATH}/*.csv"):
        with open(spreadsheet_path, "r", encoding="utf8") as cards_sheet:
            cards_sheet_reader = csv.reader(cards_sheet)
            columns = next(cards_sheet_reader)
            for row in cards_sheet_reader:
                values = dict(zip(columns, [element.strip() for element in row]))
                card_title = values.get(CARD_TITLE, "")
                card_additional_titles = values.get(CARD_ADDITIONAL_TITLES, "")
                card_descriptor = values.get(CARD_DESCRIPTOR, "")
                card_key = get_card_key(card_title, card_additional_titles, card_descriptor)

                if len(card_title) == 0:
                    continue

                values[CARD_FRAME_LAYOUT_EXTRAS] = []
                card_frame_layout = values.get(CARD_FRAME_LAYOUT, "").lower()
                for extra in FRAME_LAYOUT_EXTRAS_LIST:
                    extra_idx = card_frame_layout.find(extra)
                    if card_frame_layout.find(extra) >= 0:
                        card_frame_layout = card_frame_layout[:extra_idx] + card_frame_layout[extra_idx + len(extra) :]
                        values[CARD_FRAME_LAYOUT_EXTRAS].append(extra.strip())
                values[CARD_FRAME_LAYOUT] = card_frame_layout

                raw_cards[card_key] = values

    def get_sorted_keys():
        return sorted(
            raw_cards.keys(),
            key=lambda key: (
                str_to_datetime(raw_cards[key].get(CARD_CREATION_DATE, ""), datetime(MINYEAR, 1, 1)),
                str_to_int(raw_cards[key].get(CARD_ORDERER, ""), 0),
                raw_cards[key].get(CARD_TITLE, ""),
            ),
        )

    sorted_keys = get_sorted_keys()

    # Add indices to all the cards, for collector info
    category_indices: dict[str : dict[str, int]] = {}
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
            card["footer_largest_index"] = category_indices[card_set][category]

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

    filtered_cards: dict[str, dict[str, str]] = {}
    for key, metadata in raw_cards.items():
        card_title = metadata.get(CARD_TITLE, "")
        card_additional_titles = metadata.get(CARD_ADDITIONAL_TITLES, "")
        card_descriptor = metadata.get(CARD_DESCRIPTOR, "")
        card_set = metadata.get(CARD_SET, "").lower()
        card_category = metadata.get(CARD_CATEGORY, "").lower()
        if (
            not card_on_card_name_whitelist(card_title, card_additional_titles, card_descriptor)
            or not card_on_set_whitelist(card_set)
            or not card_on_category_whitelist(card_category)
        ):
            continue
        filtered_cards[key] = metadata

    # Give each card a class depending on its frame layout
    for key, metadata in filtered_cards.items():
        frame_layout = metadata.get(CARD_FRAME_LAYOUT, "").lower()
        subclass = layout_to_subclass.get(frame_layout, RegularCard)

        card_set = metadata.get(CARD_SET, "")
        if card_set not in card_sets:
            os.makedirs(f"{OUTPUT_CARDS_PATH}/{card_set}", exist_ok=True)
            card_sets[card_set] = {}

        card_sets[card_set][key] = subclass(metadata=metadata)

    def get_sorted_cards(card_set: str):
        return sorted(
            card_sets[card_set].values(),
            key=lambda card: (
                str_to_datetime(card.get_metadata(CARD_CREATION_DATE), datetime(MINYEAR, 1, 1)),
                str_to_int(card.get_metadata(CARD_ORDERER), 0),
                card.get_metadata(CARD_TITLE),
            ),
        )

    for card_set in card_sets:
        sorted_cards = get_sorted_cards(card_set)

        # Give each alternate card a subclass based on their frame layout (now that they have one)
        # Also replace empty columns in alternates with their original card's values
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
                for key, value in card.metadata.items():
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
                        )
                        and len(value) == 0
                    ):
                        card.set_metadata(key, original_card.get_metadata(key))
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
                        key in (CARD_INDEX, CARD_CATEGORY, CARD_RARITY, CARD_CREATION_DATE, CARD_LANGUAGE)
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

    if sort:
        sorted_card_sets = {}
        for card_set in card_sets:
            sorted_card_sets[card_set] = dict(
                sorted(
                    card_sets[card_set].items(),
                    key=lambda card: (
                        str_to_datetime(card[1].get_metadata(CARD_CREATION_DATE), datetime(MINYEAR, 1, 1)),
                        str_to_int(card[1].get_metadata(CARD_ORDERER), 0),
                        card[1].get_metadata(CARD_TITLE),
                    ),
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
            card_title = card.get_metadata(CARD_TITLE)
            card_additional_titles = card.get_metadata(CARD_ADDITIONAL_TITLES)
            card_descriptor = card.get_metadata(CARD_DESCRIPTOR)
            card_key = get_card_key(card_title, card_additional_titles, card_descriptor)

            card.create_layers()
            final_card = card.render_card()
            final_card.save(f"{output_path}/{cardname_to_filename(card_key)}.png")
            final_card.close()

        for card in spreadsheet.values():
            card_title = card.get_metadata(CARD_TITLE)
            card_additional_titles = card.get_metadata(CARD_ADDITIONAL_TITLES)
            card_descriptor = card.get_metadata(CARD_DESCRIPTOR)
            card_key = get_card_key(card_title, card_additional_titles, card_descriptor)

            log(f"Processing '{card_key}'...")
            increase_log_indent()

            render_card(card)

            for backside in card.get_metadata(CARD_BACKSIDES, []):
                backside_title = backside.get_metadata(CARD_TITLE)
                backside_additional_titles = backside.get_metadata(CARD_ADDITIONAL_TITLES)
                backside_descriptor = backside.get_metadata(CARD_DESCRIPTOR)
                backside_key = get_card_key(backside_title, backside_additional_titles, backside_descriptor)

                log(f"Processing '{backside_key}'...")
                increase_log_indent()

                render_card(backside)

                decrease_log_indent()

            decrease_log_indent()

        decrease_log_indent()

        log()


def render_tiled_cards(card_sets: dict[str, dict[str, RegularCard]]):
    tile_image_width = (MAX_TILING_WIDTH // CARD_TILE_WIDTH) * CARD_TILE_WIDTH
    tile_image_height = (MAX_TILING_HEIGHT // CARD_TILE_HEIGHT) * CARD_TILE_HEIGHT

    for card_set, spreadsheet in card_sets.items():
        output_path = f"{OUTPUT_TILES_PATH}/{card_set}"
        log(f"Processing set at '{output_path}'...")
        increase_log_indent()

        tile_image: dict[str, int] = {}
        tile_num: dict[str, int] = {}
        curr_width: dict[str, int] = {}
        curr_height: dict[str, int] = {}

        def tile_card(card: RegularCard):
            card.create_layers()
            final_card = card.render_card()
            if card.FOOTER_ROTATION == 90:
                final_card = final_card.transpose(Image.Transpose.ROTATE_270)
            elif card.FOOTER_ROTATION == 270:
                final_card = final_card.transpose(Image.Transpose.ROTATE_90)
            final_card = final_card.resize((CARD_TILE_WIDTH, CARD_TILE_HEIGHT))

            card_category = card.get_metadata(CARD_CATEGORY).lower()
            if not tile_image.get(card_category, False):
                tile_image[card_category] = Image.new("RGBA", (tile_image_width, tile_image_height), (0, 0, 0, 0))
                tile_num[card_category] = 1
                curr_width[card_category] = 0
                curr_height[card_category] = 0

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

            tile_image[card_category] = paste_image(
                final_card, tile_image[card_category], (curr_width[card_category], curr_height[card_category])
            )
            final_card.close()
            curr_width[card_category] += CARD_TILE_WIDTH

        for card in spreadsheet.values():
            card_title = card.get_metadata(CARD_TITLE)
            card_additional_titles = card.get_metadata(CARD_ADDITIONAL_TITLES)
            card_descriptor = card.get_metadata(CARD_DESCRIPTOR)
            card_key = get_card_key(card_title, card_additional_titles, card_descriptor)

            log(f"Tiling '{card_key}'...")
            increase_log_indent()

            tile_card(card)

            for backside in card.get_metadata(CARD_BACKSIDES, []):
                backside_title = backside.get_metadata(CARD_TITLE)
                backside_additional_titles = backside.get_metadata(CARD_ADDITIONAL_TITLES)
                backside_descriptor = backside.get_metadata(CARD_DESCRIPTOR)
                backside_key = get_card_key(backside_title, backside_additional_titles, backside_descriptor)

                log(f"Tiling '{backside_key}'...")
                increase_log_indent()

                tile_card(backside)

                decrease_log_indent()

            decrease_log_indent()

        for category in tile_image.keys():
            if curr_width[category] > 0 or curr_height[category] > 0:
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
        }

        blacklisted_frames = (
            "regular/eldrazi",
            "adventure/storybook/",
            "battle/",
            "planeswalker/",
            "room/",
            "showcase/draconic/",
            "showcase/full_text/",
            "showcase/japan/",
            "showcase/transparent/",
            "token/",
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
            if "full text" in card_frame_layout:
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
    sort: bool = True,
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

    sort: bool, default: False
        Whether to automatically sort the cards by date, then by name, or not.
    """

    reset_log()
    card_sets = process_spreadsheets(card_names_whitelist, card_sets_whitelist, card_categories_whitelist, sort)
    if action == ACTIONS[0]:
        log("Rendering cards...")
        render_cards(card_sets)
    elif action == ACTIONS[1]:
        log("Tiling cards...")
        render_tiled_cards(card_sets)
    elif action == ACTIONS[2]:
        log("Capturing art from existing cards...")
        capture_art(card_sets)
    elif action == ACTIONS[3]:
        log("Auditing art...")
        audit_art(card_sets)


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
        "-c",
        "--cards",
        nargs="+",
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
        help=("Only process the cards in these sets. "),
        dest="card_sets_whitelist",
    )
    parser.add_argument(
        "-cat",
        "--categories",
        nargs="+",
        help=(
            "Only process the cards in these categories. "
            "NOTE: If you're rendering alternates, you MUST render the original versions as well, or they will break."
        ),
        dest="card_categories_whitelist",
    )
    parser.add_argument(
        "-st",
        "--sort",
        action="store_false",
        help=(
            "Whether to sort the provided cards by date (ascending) then card name (ascending)."
            "If false, it will take the order given in the spreadsheets, one spreadsheet after another. "
            "This matters for what order cards are indexed on in their footer (and for the order when tiling)."
        ),
        dest="sort",
    )

    args = parser.parse_args()
    main(
        args.action,
        args.card_names_whitelist,
        args.card_sets_whitelist,
        args.card_categories_whitelist,
        args.sort,
    )
