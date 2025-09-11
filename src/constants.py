import re

from model.Symbol import Symbol
from utils import open_image

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
CARD_WATERMARK = "Watermark"
CARD_WATERMARK_COLOR = "Watermark Color(s)"


###########################
# FORMATTING & DIMENSIONS #
###########################

# Card Dimensions
CARD_WIDTH = 1500
CARD_HEIGHT = 2100
BATTLE_CARD_MULT = 1.34

# Title Header Box
TITLE_BOX_WIDTH = 1280
TITLE_BOX_HEIGHT = 114
TITLE_BOX_X = 110
TITLE_BOX_Y = 105

# Mana Cost Symbol
MANA_COST_SYMBOL_SIZE = 70
MANA_COST_SYMBOL_SPACING = 6
MANA_COST_SYMBOL_SHADOW_OFFSET = (-1, 6)
HYBRID_MANA_SYMBOL_SIZE_MULT = 1.25

# Title Text
TITLE_X = 128
TITLE_Y = 105
TITLE_MAX_WIDTH = 1244
BELEREN_BOLD_SIZE = 79

# Type Text
TYPE_X = 128
TYPE_Y = 1186
TYPE_MAX_WIDTH = 1244
TYPE_BOX_HEIGHT = 114
TYPE_FONT_SIZE = 67

# Rules Text Box
RULES_BOX_WIDTH = 1278
RULES_BOX_HEIGHT = 623
RULES_BOX_X = 112
RULES_BOX_Y = 1315
RULES_BOX_MAX_FONT_SIZE = 78
RULES_BOX_MIN_FONT_SIZE = 6

# Rules Text
MANA_SYMBOL_RULES_TEXT_SCALE = 0.78
MANA_SYMBOL_RULES_TEXT_MARGIN = 5
LINE_HEIGHT_TO_GAP_RATIO = 4

# Power & Toughness
POWER_TOUGHNESS_WIDTH = 252
POWER_TOUGHNESS_HEIGHT = 124
POWER_TOUGHNESS_X = 1166
POWER_TOUGHNESS_Y = 1866
POWER_TOUGHNESS_FONT_SIZE = 80

# Watermark
WATERMARK_WIDTH = 325
WATERMARK_OPACITY = 0.4
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


##################
# FILE LOCATIONS #
##################

# Input & Output locations
INPUT_SPREADSHEETS_PATH = "spreadsheets"
OUTPUT_CARDS_PATH = "processed_cards"

# Image Locations
FRAMES_PATH = "images/frames"
MANA_SYMBOLS_PATH = "images/mana_symbols"
WATERMARKS_PATH = "images/collector_info/watermarks"

# Fonts
MPLANTIN = "fonts/mplantin.ttf"
MPLANTIN_ITALICS = "fonts/mplantinit.ttf"
BELEREN_BOLD = "fonts/beleren-bold.ttf"
BELEREN_BOLD_SMALL_CAPS = "fonts/beleren-bold-smallcaps.ttf"


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

# Text Formatting
FLAVOR_DIVIDING_LINE = open_image("images/flavor_divider.png")


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
    # Text Formatting
    "flavor": Symbol(FLAVOR_DIVIDING_LINE),
}


#####################
# FORMATTING GUIDES #
#####################

# Collector Info Number Widths
NUMBER_WIDTHS = {
    "0": 26,
    "1": 14,
    "2": 23,
    "3": 22,
    "4": 25,
    "5": 22,
    "6": 23,
    "7": 21,
    "8": 23,
    "9": 25,
}

# Illegal Filename Character Conversion
CHAR_TO_TITLE_CHAR = {
    "<": "{BC}",
    ">": "{FC}",
    ":": "{C}",
    '"': "{QT}",
    "/": "{FS}",
    "\\": "{BS}",
    "|": "{B}",
    "?": "{QS}",
    "*": "{A}",
}

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
