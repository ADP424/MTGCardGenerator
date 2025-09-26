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

CARD_ADDITIONAL_TITLES = "Additional Title(s)"
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
MPLANTIN_BOLD = "fonts/mplantin-bold.ttf"
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

# Mono-Colored Mana
WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/white.png")
BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/blue.png")
BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/black.png")
RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/red.png")
GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/green.png")
COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/colorless.png")
PURPLE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/purple.png")

# Numbered Mana
ZERO_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/0.png")
ONE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/1.png")
TWO_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/2.png")
THREE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/3.png")
FOUR_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/4.png")
FIVE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/5.png")
SIX_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/6.png")
SEVEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/7.png")
EIGHT_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/8.png")
NINE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/9.png")
TEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/10.png")
ELEVEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/11.png")
TWELVE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/12.png")
THIRTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/13.png")
FOURTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/14.png")
FIFTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/15.png")
SIXTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/16.png")
SEVENTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/17.png")
EIGHTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/18.png")
NINETEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/19.png")
TWENTY_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/20.png")
HALF_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/half.png")
INFINITY_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/infinity.png")

# Tapping
TAP = open_image(f"{MANA_SYMBOLS_PATH}/tap/tap.png")
UNTAP = open_image(f"{MANA_SYMBOLS_PATH}/tap/untap.png")
OLD_TAP = open_image(f"{MANA_SYMBOLS_PATH}/tap/old_tap.png")
ORIGINAL_TAP = open_image(f"{MANA_SYMBOLS_PATH}/tap/original_tap.png")

# Standard Hybrid Mana
WHITE_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/white_blue.png")
WHITE_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/white_black.png")
BLUE_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/blue_black.png")
BLUE_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/blue_red.png")
BLACK_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/black_red.png")
BLACK_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/black_green.png")
RED_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/red_green.png")
RED_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/red_white.png")
GREEN_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/green_white.png")
GREEN_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/green_blue.png")
COLORLESS_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/colorless_white.png")
COLORLESS_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/colorless_white.png")
COLORLESS_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/colorless_white.png")
COLORLESS_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/colorless_white.png")
COLORLESS_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/colorless_white.png")
PURPLE_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/purple_white.png")
PURPLE_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/purple_blue.png")
PURPLE_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/purple_black.png")
PURPLE_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/purple_red.png")
PURPLE_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/purple_green.png")

# Phyrexian Mana
WHITE_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/phyrexian/white.png")
BLUE_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/phyrexian/blue.png")
BLACK_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/phyrexian/black.png")
RED_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/phyrexian/red.png")
GREEN_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/phyrexian/green.png")
COLORLESS_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/phyrexian/colorless.png")
PURPLE_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/phyrexian/purple.png")

# Hybrid Generic Mana
TWO_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/white.png")
TWO_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/blue.png")
TWO_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/black.png")
TWO_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/red.png")
TWO_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/green.png")
TWO_PURPLE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/purple.png")

# Hybrid Phyrexian Mana
WHITE_BLUE_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/phyrexian/white_blue.png")
WHITE_BLACK_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/phyrexian/white_black.png")
BLUE_BLACK_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/phyrexian/blue_black.png")
BLUE_RED_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/phyrexian/blue_red.png")
BLACK_RED_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/phyrexian/black_red.png")
BLACK_GREEN_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/phyrexian/black_green.png")
RED_GREEN_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/phyrexian/red_green.png")
RED_WHITE_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/phyrexian/red_white.png")
GREEN_WHITE_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/phyrexian/green_white.png")
GREEN_BLUE_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/phyrexian/green_blue.png")

# Variable Mana
X_MANA = open_image(f"{MANA_SYMBOLS_PATH}/variable/x.png")
Y_MANA = open_image(f"{MANA_SYMBOLS_PATH}/variable/y.png")
Z_MANA = open_image(f"{MANA_SYMBOLS_PATH}/variable/z.png")

# Other
SNOW_MANA = open_image(f"{MANA_SYMBOLS_PATH}/snow.png")
ENERGY = open_image(f"{MANA_SYMBOLS_PATH}/energy.png")
TICKET = open_image(f"{MANA_SYMBOLS_PATH}/ticket.png")


###########
# SYMBOLS #
###########

PLACEHOLDER_REGEX = re.compile(r"\{([^}]+)\}")

SYMBOL_PLACEHOLDER_KEY = {
    # Mono-Colored Mana
    "w": Symbol(WHITE_MANA),
    "u": Symbol(BLUE_MANA),
    "b": Symbol(BLACK_MANA),
    "r": Symbol(RED_MANA),
    "g": Symbol(GREEN_MANA),
    "c": Symbol(COLORLESS_MANA),
    "p": Symbol(PURPLE_MANA),
    # Numbered Mana
    "0": Symbol(ZERO_MANA),
    "1": Symbol(ONE_MANA),
    "2": Symbol(TWO_MANA),
    "3": Symbol(THREE_MANA),
    "4": Symbol(FOUR_MANA),
    "5": Symbol(FIVE_MANA),
    "6": Symbol(SIX_MANA),
    "7": Symbol(SEVEN_MANA),
    "8": Symbol(EIGHT_MANA),
    "9": Symbol(NINE_MANA),
    "10": Symbol(TEN_MANA),
    "11": Symbol(ELEVEN_MANA),
    "12": Symbol(TWELVE_MANA),
    "13": Symbol(THIRTEEN_MANA),
    "14": Symbol(FOURTEEN_MANA),
    "15": Symbol(FIFTEEN_MANA),
    "16": Symbol(SIXTEEN_MANA),
    "17": Symbol(SEVENTEEN_MANA),
    "18": Symbol(EIGHTEEN_MANA),
    "19": Symbol(NINETEEN_MANA),
    "20": Symbol(TWENTY_MANA),
    "1/2": Symbol(HALF_MANA),
    "inf": Symbol(INFINITY_MANA),
    "infinity": Symbol(INFINITY_MANA),
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
    "p/w": Symbol(PURPLE_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/p": Symbol(PURPLE_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "p/u": Symbol(PURPLE_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/p": Symbol(PURPLE_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "p/b": Symbol(PURPLE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/p": Symbol(PURPLE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "p/r": Symbol(PURPLE_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/p": Symbol(PURPLE_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "p/g": Symbol(PURPLE_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/p": Symbol(PURPLE_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/w": Symbol(COLORLESS_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/c": Symbol(COLORLESS_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/u": Symbol(COLORLESS_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/c": Symbol(COLORLESS_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/b": Symbol(COLORLESS_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/c": Symbol(COLORLESS_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/r": Symbol(COLORLESS_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/c": Symbol(COLORLESS_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/g": Symbol(COLORLESS_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/c": Symbol(COLORLESS_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    # Phyrexian Mana
    "wp": Symbol(WHITE_PHYREXIAN_MANA),
    "up": Symbol(BLUE_PHYREXIAN_MANA),
    "bp": Symbol(BLACK_PHYREXIAN_MANA),
    "rp": Symbol(RED_PHYREXIAN_MANA),
    "gp": Symbol(GREEN_PHYREXIAN_MANA),
    "cp": Symbol(COLORLESS_PHYREXIAN_MANA),
    "pp": Symbol(PURPLE_PHYREXIAN_MANA),
    # Hybrid Generic Mana
    "2/w": Symbol(TWO_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/2": Symbol(TWO_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/u": Symbol(TWO_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/2": Symbol(TWO_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/b": Symbol(TWO_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/2": Symbol(TWO_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/r": Symbol(TWO_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/2": Symbol(TWO_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/g": Symbol(TWO_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/2": Symbol(TWO_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    # Hybrid Phyrexian Mana
    "wp/up": Symbol(WHITE_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "up/wp": Symbol(WHITE_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "wp/bp": Symbol(WHITE_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "bp/wp": Symbol(WHITE_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "up/bp": Symbol(BLUE_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "bp/up": Symbol(BLUE_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "up/rp": Symbol(BLUE_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "rp/up": Symbol(BLUE_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "bp/rp": Symbol(BLACK_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "rp/bp": Symbol(BLACK_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "bp/gp": Symbol(BLACK_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "gp/bp": Symbol(BLACK_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "rp/gp": Symbol(RED_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "gp/rp": Symbol(RED_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "rp/wp": Symbol(RED_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "wp/rp": Symbol(RED_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "gp/wp": Symbol(GREEN_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "wp/gp": Symbol(GREEN_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "gp/up": Symbol(GREEN_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "up/gp": Symbol(GREEN_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    # Variable Mana
    "x": Symbol(X_MANA),
    "y": Symbol(Y_MANA),
    "z": Symbol(Z_MANA),
    # Other
    "s": Symbol(SNOW_MANA),
    "e": Symbol(ENERGY),
    "ticket": Symbol(TICKET),
}

# Planeswalker Abilities
PLANESWALKER_ABILITY_BODY_EVEN = Symbol(open_image(f"{FRAMES_PATH}/planeswalker/ability/body/even.png"))
PLANESWALKER_ABILITY_BODY_ODD = Symbol(open_image(f"{FRAMES_PATH}/planeswalker/ability/body/odd.png"))
PLANESWALKER_ABILITY_TOP_EVEN = Symbol(open_image(f"{FRAMES_PATH}/planeswalker/ability/top/even.png"))
PLANESWALKER_ABILITY_TOP_ODD = Symbol(open_image(f"{FRAMES_PATH}/planeswalker/ability/top/odd.png"))

# Planeswalker Ability Cost Borders
PLANESWALKER_ABILITY_COST_BORDER_POSITIVE = Symbol(open_image(f"{FRAMES_PATH}/planeswalker/ability/cost/positive.png"))
PLANESWALKER_ABILITY_COST_BORDER_NEGATIVE = Symbol(open_image(f"{FRAMES_PATH}/planeswalker/ability/cost/negative.png"))
PLANESWALKER_ABILITY_COST_BORDER_NEUTRAL = Symbol(open_image(f"{FRAMES_PATH}/planeswalker/ability/cost/neutral.png"))

# Saga
SAGA_CHAPTER_FRAME = Symbol(open_image(f"{FRAMES_PATH}/saga/chapter.png"))
SAGA_CHAPTER_DIVIDING_LINE = Symbol(open_image(f"{FRAMES_PATH}/saga/divider.png"), (1.0, 0.67))
SAGA_BANNER_STRIPE = Symbol(open_image(f"{FRAMES_PATH}/saga/banner_stripe.png"))

# Class
CLASS_HEADER = Symbol(open_image(f"{FRAMES_PATH}/class/header.png"))

# Other
RULES_DIVIDING_LINE = Symbol(open_image("images/other/divider.png"))
ARTIST_BRUSH = Symbol(open_image("images/collector_info/artist_brush.png"), 1.25)
DICE_SECTION = Symbol(open_image("images/other/dice_section.png"))
