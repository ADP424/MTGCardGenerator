import re
from PIL import Image

# card dimensons
CARD_WIDTH = 1500
CARD_HEIGHT = 2100
BATTLE_CARD_MULT = 1.34

RULES_BOX_WIDTH = 1278
RULES_BOX_HEIGHT = 623
RULES_BOX_X = 112
RULES_BOX_Y = 1315
RULES_BOX_MAX_FONT_SIZE = 78
RULES_BOX_MIN_FONT_SIZE = 6

LINE_HEIGHT_TO_GAP_RATIO = 4

MANA_SYMBOL_RULES_TEXT_SCALE = 0.8

# the name of the .csv file that hold all the card information
CARDS_SPREADSHEET = "spreadsheets/the_one_set - Cards.csv"

# which columns in the spreadsheet correspond to which attribute
CARD_CATEGORY = "Category"
CARD_TITLE = "Title"
CARD_MANA_COST = "Mana Cost"
CARD_RULES_TEXT = "Rules Text"
CARD_FRAME = "Frame(s)"
CARD_TYPE = "Type(s)"
CARD_SUBTYPE = "Subtype(s)"

# image locations
REGULAR_MANA_SYMBOLS_PATH = "images/mana_symbols/regular"
DROP_SHADOW_MANA_SYMBOLS_PATH = "images/mana_symbols/regular"

# fonts
RULES_TEXT_FONT = "fonts/mplantin.ttf"
FLAVOR_TEXT_FONT = "fonts/mplantinit.ttf"
MANA_SYMBOL_FONT = "fonts/mana/mana.ttf"

# conversions for characters in card names that can't appear in filenames
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

# mana symbol & text code placeholders
PLACEHOLDER_REGEX = re.compile(r"\{([^}]+)\}")
PLACEHOLDER_KEY = {
    # colored mana
    "W": Image.open("images/mana_symbols/regular/white.png").convert("RGBA"),
    "U": Image.open("images/mana_symbols/regular/blue.png").convert("RGBA"),
    "B": Image.open("images/mana_symbols/regular/black.png").convert("RGBA"),
    "R": Image.open("images/mana_symbols/regular/red.png").convert("RGBA"),
    "G": Image.open("images/mana_symbols/regular/green.png").convert("RGBA"),
    "C": Image.open("images/mana_symbols/regular/colorless.png").convert("RGBA"),

    # numbered mana
    "1": Image.open("images/mana_symbols/regular/1.png").convert("RGBA"),
    "2": Image.open("images/mana_symbols/regular/2.png").convert("RGBA"),
    "3": Image.open("images/mana_symbols/regular/3.png").convert("RGBA"),

    # text formatting
    "flavor": Image.open("images/flavor_divider.png").convert("RGBA"),
}

# the widths of numbers in the collector info
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

# color to poker borders conversion
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
