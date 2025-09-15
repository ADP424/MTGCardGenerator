from collections import defaultdict
import re

from model.Symbol import Symbol
from utils import open_image

##########################
# Command Line Arguments #
##########################

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

CARD_REVERSE_POWER_TOUGHNESS = "Transform P/T"
CARD_FRONTSIDE = "Transform Frontside"
CARD_ORDERER = "Orderer"
CARD_ORIGINAL = "Original Card"
CARD_DESCRIPTOR = "Descriptor"

# Not in Spreadsheet (Added at Runtime)
CARD_INDEX = "Index"
CARD_BACKSIDES = "Transform Backsides"


###########################
# FORMATTING & DIMENSIONS #
###########################

# Card Types with Different Formats
REGULAR = "regular"
TRANSFORM_FRONTSIDE = "transform frontside"
TRANSFORM_BACKSIDE_PIP = "transform backside pip"
TRANSFORM_BACKSIDE_NO_PIP = "transform backside no pip"
BATTLE = "battle"

# Card Dimensions
CARD_WIDTH = defaultdict(lambda: 1500, {REGULAR: 1500, BATTLE: 2814})
CARD_HEIGHT = defaultdict(lambda: 2100, {REGULAR: 2100, BATTLE: 2010})

# Card Art
ART_WIDTH = defaultdict(
    lambda: 1270,
    {
        REGULAR: 1270,
        BATTLE: 2511,
    },
)
ART_HEIGHT = defaultdict(
    lambda: 929,
    {
        REGULAR: 929,
        BATTLE: 1840,
    },
)
ART_X = defaultdict(
    lambda: 115,
    {
        REGULAR: 116,
        BATTLE: 224,
    },
)
ART_Y = defaultdict(
    lambda: 237,
    {
        REGULAR: 238,
        BATTLE: 81,
    },
)

# Title Header Box
TITLE_BOX_WIDTH = defaultdict(
    lambda: 1280,
    {
        REGULAR: 1280,
        BATTLE: 2326,
        TRANSFORM_FRONTSIDE: 1170,
        TRANSFORM_BACKSIDE_PIP: 1170,
        TRANSFORM_BACKSIDE_NO_PIP: 1170,
    },
)
TITLE_BOX_HEIGHT = defaultdict(lambda: 114, {REGULAR: 114, BATTLE: 153})
TITLE_BOX_X = defaultdict(lambda: 90, {REGULAR: 90, BATTLE: 312, TRANSFORM_FRONTSIDE: 220})
TITLE_BOX_Y = defaultdict(lambda: 105, {REGULAR: 105, BATTLE: 101})

# Mana Cost Symbol
MANA_COST_SYMBOL_SIZE = defaultdict(lambda: 70, {REGULAR: 70, BATTLE: 94})
MANA_COST_SYMBOL_SPACING = defaultdict(lambda: 6, {REGULAR: 6, BATTLE: 8})
MANA_COST_SYMBOL_SHADOW_OFFSET = defaultdict(
    lambda: (-1, 6),
    {
        REGULAR: (-1, 6),
    },
)
HYBRID_MANA_SYMBOL_SIZE_MULT = 1.25

# Title Text
TITLE_X = defaultdict(
    lambda: 128,
    {REGULAR: 128, BATTLE: 172, TRANSFORM_FRONTSIDE: 240},
)
TITLE_Y = defaultdict(
    lambda: 105,
    {
        REGULAR: 105,
        BATTLE: 101,
    },
)
TITLE_MAX_WIDTH = defaultdict(
    lambda: 1244,
    {
        REGULAR: 1244,
        BATTLE: 2280,
        TRANSFORM_FRONTSIDE: 1158,
        TRANSFORM_BACKSIDE_PIP: 1158,
        TRANSFORM_BACKSIDE_NO_PIP: 1158,
    },
)
TITLE_FONT_SIZE = defaultdict(
    lambda: 79,
    {
        REGULAR: 79,
        BATTLE: 106,
    },
)
TITLE_FONT_COLOR = defaultdict(
    lambda: (0, 0, 0),
    {
        REGULAR: (0, 0, 0),
        TRANSFORM_BACKSIDE_PIP: (255, 255, 255),
        TRANSFORM_BACKSIDE_NO_PIP: (255, 255, 255),
    },
)

# Type Text
TYPE_X = defaultdict(
    lambda: 128,
    {REGULAR: 128, BATTLE: 172, TRANSFORM_BACKSIDE_PIP: 199},
)
TYPE_Y = defaultdict(
    lambda: 1190,
    {
        REGULAR: 1190,
        BATTLE: 1166,
    },
)
TYPE_MAX_WIDTH = defaultdict(
    lambda: 1244,
    {REGULAR: 1244, BATTLE: 2280, TRANSFORM_BACKSIDE_PIP: 1115},
)
TYPE_BOX_HEIGHT = defaultdict(
    lambda: 114,
    {
        REGULAR: 114,
        BATTLE: 153,
    },
)
TYPE_FONT_SIZE = defaultdict(
    lambda: 67,
    {
        REGULAR: 67,
        BATTLE: 90,
    },
)
TYPE_FONT_COLOR = defaultdict(
    lambda: (0, 0, 0),
    {
        REGULAR: (0, 0, 0),
        TRANSFORM_BACKSIDE_PIP: (255, 255, 255),
        TRANSFORM_BACKSIDE_NO_PIP: (255, 255, 255),
    },
)

# Rules Text Box
RULES_BOX_WIDTH = defaultdict(
    lambda: 1278,
    {
        REGULAR: 1278,
        BATTLE: 2276,
    },
)
RULES_BOX_HEIGHT = defaultdict(
    lambda: 623,
    {
        REGULAR: 623,
        BATTLE: 579,
    },
)
RULES_BOX_X = defaultdict(
    lambda: 112,
    {
        REGULAR: 112,
        BATTLE: 339,
    },
)
RULES_BOX_Y = defaultdict(
    lambda: 1315,
    {
        REGULAR: 1315,
        BATTLE: 1339,
    },
)
RULES_BOX_MAX_FONT_SIZE = defaultdict(
    lambda: 78,
    {
        REGULAR: 78,
        BATTLE: 104,
    },
)
RULES_BOX_MIN_FONT_SIZE = defaultdict(
    lambda: 6,
    {
        REGULAR: 6,
        BATTLE: 8,
    },
)

# Rules Text
MANA_SYMBOL_RULES_TEXT_SCALE = defaultdict(
    lambda: 0.78,
    {
        REGULAR: 0.78,
    },
)
MANA_SYMBOL_RULES_TEXT_MARGIN = defaultdict(
    lambda: 5,
    {
        REGULAR: 5,
        BATTLE: 7,
    },
)
RULES_TEXT_LINE_HEIGHT_TO_GAP_RATIO = defaultdict(
    lambda: 4,
    {
        REGULAR: 4,
    },
)

# Power & Toughness
POWER_TOUGHNESS_WIDTH = defaultdict(
    lambda: 252,
    {
        REGULAR: 252,
        BATTLE: 118,
    },
)
POWER_TOUGHNESS_HEIGHT = defaultdict(
    lambda: 124,
    {
        REGULAR: 124,
        BATTLE: 137,
    },
)
POWER_TOUGHNESS_X = defaultdict(
    lambda: 1166,
    {
        REGULAR: 1166,
        BATTLE: 2570,
    },
)
POWER_TOUGHNESS_Y = defaultdict(
    lambda: 1866,
    {
        REGULAR: 1866,
        BATTLE: 1784,
    },
)
POWER_TOUGHNESS_FONT_SIZE = defaultdict(
    lambda: 80,
    {
        REGULAR: 80,
        BATTLE: 107,
    },
)
POWER_TOUGHNESS_FONT_COLOR = defaultdict(
    lambda: (0, 0, 0),
    {
        REGULAR: (0, 0, 0),
        TRANSFORM_BACKSIDE_PIP: (255, 255, 255),
        TRANSFORM_BACKSIDE_NO_PIP: (255, 255, 255),
    },
)

# Reverse Power & Toughness
REVERSE_POWER_TOUGHNESS_WIDTH = defaultdict(
    lambda: 90,
    {
        REGULAR: 90,
    },
)
REVERSE_POWER_TOUGHNESS_HEIGHT = defaultdict(
    lambda: 65,
    {
        REGULAR: 65,
    },
)
REVERSE_POWER_TOUGHNESS_X = defaultdict(
    lambda: 1301,
    {
        REGULAR: 1301,
    },
)
REVERSE_POWER_TOUGHNESS_Y = defaultdict(
    lambda: 1762,
    {
        REGULAR: 1762,
    },
)
REVERSE_POWER_TOUGHNESS_FONT_SIZE = defaultdict(
    lambda: 60,
    {
        REGULAR: 60,
    },
)
REVERSE_POWER_TOUGHNESS_FONT_COLOR = defaultdict(
    lambda: (102, 102, 102),
    {
        REGULAR: (102, 102, 102),
    },
)

# Watermark
WATERMARK_WIDTH = defaultdict(
    lambda: 325,
    {
        REGULAR: 325,
        BATTLE: 435,
    },
)
WATERMARK_OPACITY = defaultdict(
    lambda: 0.4,
    {
        REGULAR: 0.4,
    },
)
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

# Rarity / Set Symbol
SET_SYMBOL_X = defaultdict(
    lambda: 1296,
    {
        REGULAR: 1296,
        BATTLE: 2484,
    },
)
SET_SYMBOL_Y = defaultdict(
    lambda: 1198,
    {
        REGULAR: 1198,
        BATTLE: 1176,
    },
)
SET_SYMBOL_WIDTH = defaultdict(
    lambda: 90,
    {
        REGULAR: 90,
        BATTLE: 121,
    },
)

# Footer
FOOTER_WIDTH = defaultdict(
    lambda: 1304,
    {
        REGULAR: 1304,
        BATTLE: 204,
    },
)
FOOTER_HEIGHT = defaultdict(
    lambda: 152,
    {
        REGULAR: 152,
        BATTLE: 1747,
    },
)
FOOTER_X = defaultdict(
    lambda: 96,
    {
        REGULAR: 96,
        BATTLE: 0,
    },
)
FOOTER_Y = defaultdict(
    lambda: 1968,
    {
        REGULAR: 1968,
        BATTLE: 120,
    },
)
FOOTER_FONT_SIZE = defaultdict(
    lambda: 35,
    {
        REGULAR: 35,
        BATTLE: 47,
    },
)
FOOTER_FONT_OUTLINE_SIZE = defaultdict(
    lambda: 3,
    {
        REGULAR: 3,
        BATTLE: 4,
    },
)
FOOTER_LINE_HEIGHT_TO_GAP_RATIO = defaultdict(
    lambda: 2,
    {
        REGULAR: 2,
    },
)
FOOTER_TAB_LENGTH = defaultdict(
    lambda: 25,
    {
        REGULAR: 25,
        BATTLE: 33,
    },
)
ARTIST_GAP_LENGTH = defaultdict(
    lambda: 5,
    {
        REGULAR: 5,
        BATTLE: 7,
    },
)


##################
# FILE LOCATIONS #
##################

# Input & Output locations
INPUT_SPREADSHEETS_PATH = "spreadsheets"
OUTPUT_CARDS_PATH = "processed_cards"

INPUT_CARDS_PATH = "existing_cards"
ART_PATH = "images/art"

# Image Locations
FRAMES_PATH = "images/frames"
MANA_SYMBOLS_PATH = "images/mana_symbols"
WATERMARKS_PATH = "images/collector_info/watermarks"
SET_SYMBOLS_PATH = "images/collector_info/set_symbols"

# Fonts
MPLANTIN = "fonts/mplantin.ttf"
MPLANTIN_ITALICS = "fonts/mplantinit.ttf"
BELEREN_BOLD = "fonts/beleren-bold.ttf"
BELEREN_BOLD_SMALL_CAPS = "fonts/beleren-bold-smallcaps.ttf"
MATRIX_BOLD = "fonts/MatrixBold.ttf"
HELVETICA = "fonts/GothamBold.ttf"


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
    # Other
    "flavor": Symbol(FLAVOR_DIVIDING_LINE),
    "artist_brush": Symbol(ARTIST_BRUSH, 1.25),
}


#####################
# FORMATTING GUIDES #
#####################

# Rarity to Collector Initial Conversion
RARITY_TO_INITIAL = {"common": "C", "uncommon": "U", "rare": "R", "mythic": "M", "land": "L", "lato": "O"}

# Color to Poker Border Conversion
POKER_BORDERS = {
    "W": "fold",
    "U": "echo",
    "B": "necro",
    "R": "joker",
    "G": "wild",
    "WU": "fold_echo",
    "WB": "fold_necro",
    "WR": "joker_fold",
    "WG": "wild_fold",
    "UB": "echo_necro",
    "UR": "echo_joker",
    "UG": "wild_echo",
    "BR": "necro_joker",
    "BG": "necro_wild",
    "RG": "joker_wild",
    "Colorless": "glass",
}
