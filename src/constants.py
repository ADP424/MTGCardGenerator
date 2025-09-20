import re

from model.Symbol import Symbol
from utils import open_image

################
# Command Line #
################

ACTIONS = ["render", "tile", "art"]


##########################
# CSV / SPREADSHEET INFO #
##########################

# Which columns in the spreadsheet correspond to which attribute
CARD_TITLE = "Title"
CARD_MANA_COST = "Mana Cost"
CARD_RULES_TEXT = "Rules Text"
CARD_SUPERTYPES = "Supertype(s)"
CARD_TYPES = "Type(s)"
CARD_SUBTYPES = "Subtype(s)"
CARD_POWER_TOUGHNESS = "Power/Toughness"

CARD_FRAMES = "Frame(s)"
CARD_FRAME_LAYOUT = "Frame Layout"
CARD_RARITY = "Rarity"
CARD_WATERMARK = "Watermark"
CARD_WATERMARK_COLOR = "Watermark Color(s)"
CARD_CATEGORY = "Category"
CARD_CREATION_DATE = "Creation Date"
CARD_SET = "Set"
CARD_LANGUAGE = "Language"
CARD_ARTIST = "Artist"
ADD_TOTAL_TO_FOOTER = "Add Total to Footer?"

CARD_DESCRIPTOR = "Descriptor"
CARD_ORDERER = "Orderer"
CARD_REVERSE_POWER_TOUGHNESS = "Transform P/T"
CARD_FRONTSIDE = "Transform Frontside"

CARD_OVERLAYS = "Overlay(s)"

# Not in Spreadsheet (Added at Runtime)
CARD_INDEX = "Index"
CARD_BACKSIDES = "Transform Backsides"


##################
# FILE LOCATIONS #
##################

# Input & Output locations
INPUT_SPREADSHEETS_PATH = "spreadsheets"
OUTPUT_CARDS_PATH = "processed_cards"

INPUT_CARDS_PATH = "existing_cards"
OUTPUT_ART_PATH = "extracted_art"

INPUT_ART_PATH = "images/art"

# Image Locations
FRAMES_PATH = "images/frames"
MANA_SYMBOLS_PATH = "images/mana_symbols"
WATERMARKS_PATH = "images/collector_info/watermarks"
SET_SYMBOLS_PATH = "images/collector_info/set_symbols"
OVERLAYS_PATH = "images/art/overlay"

# Fonts
MPLANTIN = "fonts/mplantin.ttf"
MPLANTIN_ITALICS = "fonts/mplantin-italics.ttf"
BELEREN_BOLD = "fonts/beleren-bold.ttf"
BELEREN_BOLD_SMALL_CAPS = "fonts/beleren-bold-smallcaps.ttf"
GOTHAM_BOLD = "fonts/gotham-bold.ttf"


###########################
# FORMATTING & DIMENSIONS #
###########################

# Card Art
ART_WIDTH = 1270
ART_HEIGHT = 929
ART_X = 115
ART_Y = 237

# Mana Symbols
HYBRID_MANA_SYMBOL_SIZE_MULT = 1.25

# Watermark
WATERMARK_COLORS = {
    "white": (183, 157, 88),
    "blue": (140, 172, 197),
    "black": (94, 94, 94),
    "red": (198, 109, 57),
    "green": (89, 140, 82),
    "multicolor": (202, 179, 77),
    "artifact": (100, 125, 134),
    "colorless": (100, 125, 134),
    "land": (94, 84, 72),
}

# Rarity to Initial (For Footer)
RARITY_TO_INITIAL = {"common": "C", "uncommon": "U", "rare": "R", "mythic": "M", "land": "L", "lato": "O", "token": "T"}


##########
# IMAGES #
##########

# Standard Mana
WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/white.png")
BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/blue.png")
BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/black.png")
RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/red.png")
GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/green.png")
COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/colorless.png")

# Standard Numbered Mana
ONE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/1.png")
TWO_MANA = open_image(f"{MANA_SYMBOLS_PATH}/2.png")
THREE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/3.png")

# Tapping
TAP = open_image(f"{MANA_SYMBOLS_PATH}/tap.png")
UNTAP = open_image(f"{MANA_SYMBOLS_PATH}/untap.png")
OLD_TAP = open_image(f"{MANA_SYMBOLS_PATH}/old_tap.png")
ORIGINAL_TAP = open_image(f"{MANA_SYMBOLS_PATH}/original_tap.png")

# Standard Hybrid Mana
WHITE_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/white_blue.png")
WHITE_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/white_black.png")
BLUE_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/blue_black.png")
BLUE_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/blue_red.png")
BLACK_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/black_red.png")
BLACK_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/black_green.png")
RED_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/red_green.png")
RED_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/red_white.png")
GREEN_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/green_white.png")
GREEN_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/green_blue.png")

# Other Mana
SNOW_MANA = open_image(f"{MANA_SYMBOLS_PATH}/snow.png")

# Planeswalker
PLANESWALKER_ABILITY_BODY_EVEN = open_image(f"{FRAMES_PATH}/planeswalker/ability/body/even.png")
PLANESWALKER_ABILITY_BODY_ODD = open_image(f"{FRAMES_PATH}/planeswalker/ability/body/odd.png")
PLANESWALKER_ABILITY_TOP_EVEN = open_image(f"{FRAMES_PATH}/planeswalker/ability/top/even.png")
PLANESWALKER_ABILITY_TOP_ODD = open_image(f"{FRAMES_PATH}/planeswalker/ability/top/odd.png")

# Other
FLAVOR_DIVIDING_LINE = open_image("images/flavor_divider.png")
ARTIST_BRUSH = open_image("images/collector_info/artist_brush.png")


################
# PLACEHOLDERS #
################

PLACEHOLDER_REGEX = re.compile(r"\{([^}]+)\}")

SYMBOL_PLACEHOLDER_KEY = {
    # Standard Mana
    "w": Symbol(WHITE_MANA),
    "u": Symbol(BLUE_MANA),
    "b": Symbol(BLACK_MANA),
    "r": Symbol(RED_MANA),
    "g": Symbol(GREEN_MANA),
    "c": Symbol(COLORLESS_MANA),
    # Standard Numbered Mana
    "1": Symbol(ONE_MANA),
    "2": Symbol(TWO_MANA),
    "3": Symbol(THREE_MANA),
    # Tapping
    "t": Symbol(TAP),
    "untap": Symbol(UNTAP),
    "old_tap": Symbol(OLD_TAP),
    "original_tap": Symbol(ORIGINAL_TAP),
    # Standard Hybrid Mana
    "w/u": Symbol(WHITE_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/w": Symbol(WHITE_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/b": Symbol(WHITE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/w": Symbol(WHITE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/b": Symbol(BLUE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/u": Symbol(BLUE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/r": Symbol(BLUE_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/u": Symbol(BLUE_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/r": Symbol(BLACK_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/b": Symbol(BLACK_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/g": Symbol(BLACK_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/b": Symbol(BLACK_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/g": Symbol(RED_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/r": Symbol(RED_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/w": Symbol(RED_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/r": Symbol(RED_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/w": Symbol(GREEN_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/g": Symbol(GREEN_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/u": Symbol(GREEN_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/g": Symbol(GREEN_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    # other mana
    "s": Symbol(SNOW_MANA),
    # Other
    "flavor": Symbol(FLAVOR_DIVIDING_LINE),
    "artist_brush": Symbol(ARTIST_BRUSH, 1.25),
}
