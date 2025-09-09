import re
from PIL import Image

from model.Symbol import Symbol

##########################
# CSV / SPREADSHEET INFO #
##########################

# Which columns in the spreadsheet correspond to which attribute
CARD_TITLE = "Title"
CARD_MANA_COST = "Mana Cost"
CARD_RULES_TEXT = "Rules Text"
CARD_FRAMES = "Frame(s)"
CARD_SUPERTYPES = "Supertype(s)"
CARD_TYPES = "Type(s)"
CARD_SUBTYPES = "Subtype(s)"
CARD_POWER_TOUGHNESS = "Power/Toughness"


#######################
# SIZING & DIMENSIONS #
#######################

# Card Dimensions
CARD_WIDTH = 1500
CARD_HEIGHT = 2100
BATTLE_CARD_MULT = 1.34

# Title Header Box Sizing
TITLE_BOX_WIDTH = 1280
TITLE_BOX_HEIGHT = 114
TITLE_BOX_X = 110
TITLE_BOX_Y = 105

# Mana Cost Symbol Sizing
MANA_COST_SYMBOL_SIZE = 70
MANA_COST_SYMBOL_SPACING = 6
MANA_COST_SYMBOL_SHADOW_OFFSET = (-1, 6)
HYBRID_MANA_SYMBOL_SIZE_MULT = 1.25

# Title Text Sizing
TITLE_X = 128
TITLE_Y = 105
TITLE_MAX_WIDTH = 1244
BELEREN_BOLD_SIZE = 79

# Type Text Sizing
TYPE_X = 128
TYPE_Y = 1186
TYPE_MAX_WIDTH = 1244
TYPE_BOX_HEIGHT = 114
TYPE_FONT_SIZE = 67

# Rules Text Box Sizing
RULES_BOX_WIDTH = 1278
RULES_BOX_HEIGHT = 623
RULES_BOX_X = 112
RULES_BOX_Y = 1315
RULES_BOX_MAX_FONT_SIZE = 78
RULES_BOX_MIN_FONT_SIZE = 6

# Rules Text Sizing
MANA_SYMBOL_RULES_TEXT_SCALE = 0.78
MANA_SYMBOL_RULES_TEXT_MARGIN = 5
LINE_HEIGHT_TO_GAP_RATIO = 4

# Power & Toughness Sizing
POWER_TOUGHNESS_WIDTH = 252
POWER_TOUGHNESS_HEIGHT = 124
POWER_TOUGHNESS_X = 1166
POWER_TOUGHNESS_Y = 1866
POWER_TOUGHNESS_FONT_SIZE = 80


##################
# FILE LOCATIONS #
##################

# Input & Output locations
INPUT_SPREADSHEETS_PATH = "spreadsheets"
OUTPUT_CARDS_PATH = "processed_cards"

# Image Locations
FRAMES_PATH = "images/frames"
MANA_SYMBOLS_PATH = "images/mana_symbols"

# Fonts
MPLANTIN = "fonts/mplantin.ttf"
MPLANTIN_ITALICS = "fonts/mplantinit.ttf"
BELEREN_BOLD = "fonts/beleren-bold.ttf"
BELEREN_BOLD_SMALL_CAPS = "fonts/beleren-bold-smallcaps.ttf"


##########
# IMAGES #
##########

# Standard Mana
WHITE_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/white.png").convert("RGBA")
BLUE_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/blue.png").convert("RGBA")
BLACK_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/black.png").convert("RGBA")
RED_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/red.png").convert("RGBA")
GREEN_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/green.png").convert("RGBA")
COLORLESS_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/colorless.png").convert("RGBA")

# Standard Numbered Mana
ONE_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/1.png").convert("RGBA")
TWO_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/2.png").convert("RGBA")
THREE_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/3.png").convert("RGBA")

# Standard Hybrid Mana
WHITE_BLUE_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/white_blue.png").convert("RGBA")
WHITE_BLACK_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/white_black.png").convert("RGBA")
BLUE_BLACK_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/blue_black.png").convert("RGBA")
BLUE_RED_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/blue_red.png").convert("RGBA")
BLACK_RED_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/black_red.png").convert("RGBA")
BLACK_GREEN_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/black_green.png").convert("RGBA")
RED_GREEN_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/red_green.png").convert("RGBA")
RED_WHITE_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/red_white.png").convert("RGBA")
GREEN_WHITE_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/green_white.png").convert("RGBA")
GREEN_BLUE_MANA = Image.open(f"{MANA_SYMBOLS_PATH}/green_blue.png").convert("RGBA")

# Text Formatting
FLAVOR_DIVIDING_LINE = Image.open("images/flavor_divider.png").convert("RGBA")


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
