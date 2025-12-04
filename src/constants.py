import re

from model.Symbol import Symbol
from utils import open_image

################
# Command Line #
################

ACTIONS = ["render", "tile", "art-extract", "art-audit"]


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
CARD_TRANSFORM_HINT = "Transform Hint"
CARD_FRONTSIDE = "Transform Frontside"
CARD_ORIGINAL = "Original"

CARD_OVERLAYS = "Overlay(s)"

# Not in Spreadsheet (Added at Runtime)
CARD_INDEX = "Index"
CARD_BACKSIDES = "Transform Backsides"
CARD_FRAME_LAYOUT_EXTRAS = "Frame Layout Extras"
CARD_FOOTER_LARGEST_INDEX = "Footer Largest_Index"

##################
# FILE LOCATIONS #
##################

# Input & Output locations
INPUT_SPREADSHEETS_PATH = "spreadsheets"
OUTPUT_CARDS_PATH = "processed_cards"
OUTPUT_TILES_PATH = "processed_tiles"

INPUT_CARDS_PATH = "existing_cards"
OUTPUT_ART_PATH = "extracted_art"

INPUT_ART_PATH = "images/art"

# Image Locations
FRAMES_PATH = "images/frames"
MANA_SYMBOLS_PATH = "images/mana_symbols"
WATERMARKS_PATH = "images/collector_info/watermarks"
SET_SYMBOLS_PATH = "images/collector_info/set_symbols"
OVERLAYS_PATH = "images/art/overlay"
DICE_SECTION_PATH = "images/other/dice_section"

# Fonts
MPLANTIN = "fonts/mplantin.ttf"
MPLANTIN_ITALICS = "fonts/mplantin-italics.ttf"
MPLANTIN_BOLD = "fonts/mplantin-bold.ttf"

BELEREN_BOLD = "fonts/beleren-bold.ttf"
BELEREN_BOLD_SMALL_CAPS = "fonts/beleren-bold-smallcaps.ttf"

GOTHAM_BOLD = "fonts/gotham-bold.ttf"

LATO = "fonts/lato.ttf"
LATO_ITALICS = "fonts/lato-italics.ttf"
LATO_BOLD = "fonts/lato-bold.ttf"
LATO_BOLD_ITALICS = "fonts/lato-bold-italics.ttf"


###########################
# FORMATTING & DIMENSIONS #
###########################

# Tiling
CARD_TILE_WIDTH = 1500
CARD_TILE_HEIGHT = 2100
MAX_TILING_WIDTH = 10000
MAX_TILING_HEIGHT = 10000

# Card Art
ART_WIDTH = {
    "regular": 1270,
    "class": 633,
    "saga": 633,
}
ART_HEIGHT = {
    "regular": 929,
    "class": 1522,
    "saga": 1522,
}
ART_X = {
    "regular": 115,
    "class": 115,
    "saga": 752,
}
ART_Y = {
    "regular": 237,
    "class": 237,
    "saga": 237,
}

# Mana Symbols
HYBRID_MANA_SYMBOL_SIZE_MULT = 1.25

# Watermark
WATERMARK_COLORS = {
    # regular
    "white": (183, 157, 88),
    "blue": (140, 172, 197),
    "black": (94, 94, 94),
    "red": (198, 109, 57),
    "green": (89, 140, 82),
    "gold": (202, 179, 77),
    "multicolor": (202, 179, 77),
    "artifact": (100, 125, 134),
    "colorless": (100, 125, 134),
    "land": (94, 84, 72),
    # pycok
    "purple": (100, 32, 156),
    "yellow": (242, 181, 40),
    "cyan": (38, 185, 179),
    "orange": (226, 110, 21),
    "pink": (228, 143, 175),
    "edifice": (61, 40, 23),
    # the one set
    "triangle": (181, 108, 236),
}

# Rarity to Initial (For Footer)
RARITY_TO_INITIAL = {"common": "C", "uncommon": "U", "rare": "R", "mythic": "M", "land": "L", "lato": "O", "token": "T"}

# Card Frame Layout Extras
FRAME_LAYOUT_EXTRAS_LIST = (
    r" pip",
    r"pip ",
    r" white",
    r"white ",
    r" light",
    r"light ",
    r" vehicle",
    r"vehicle ",
    r"rotate-?\d+ ",
    r" rotate-?\d+",
)

# Splitter for Coloring Text
COLOR_TAG_PATTERN = re.compile(r"\{color\((\d+),(\d+),(\d+)\)\}(.*?)\{\/color\}", flags=re.DOTALL)
COLOR_TAG_PATTERN_NO_BRACES = re.compile(r"color\((\d+),(\d+),(\d+)\)", flags=re.DOTALL)


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

# Mono-Colored Mana (PYCOK)
PURPLE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/pycok/purple.png")
YELLOW_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/pycok/yellow.png")
CYAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/pycok/cyan.png")
ORANGE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/pycok/orange.png")
PINK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/pycok/pink.png")

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

# Other Mono Mana
SNOW_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/snow.png")
LOVE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/the_one_set/love.png")
TRIANGLE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/the_one_set/triangle.png")

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
COLORLESS_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/colorless_blue.png")
COLORLESS_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/colorless_black.png")
COLORLESS_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/colorless_red.png")
COLORLESS_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/colorless_green.png")

# Phyrexian Mana
WHITE_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/phyrexian/white.png")
BLUE_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/phyrexian/blue.png")
BLACK_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/phyrexian/black.png")
RED_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/phyrexian/red.png")
GREEN_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/phyrexian/green.png")
COLORLESS_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/mono/phyrexian/colorless.png")

# Hybrid Generic Mana
TWO_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/white.png")
TWO_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/blue.png")
TWO_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/black.png")
TWO_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/red.png")
TWO_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/green.png")
TWO_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/colorless.png")
TWO_SNOW_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/snow.png")

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

# Hybrid Generic Phyrexian Mana
TWO_WHITE_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/phyrexian/white.png")
TWO_BLUE_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/phyrexian/blue.png")
TWO_BLACK_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/phyrexian/black.png")
TWO_RED_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/phyrexian/red.png")
TWO_GREEN_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/phyrexian/green.png")
TWO_COLORLESS_PHYREXIAN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/generic/phyrexian/colorless.png")

# Snow Hybrid Mana
SNOW_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/hybrid/snow_colorless.png")

# Love Hybrid Mana
LOVE_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/the_one_set/hybrid/love_white.png")
LOVE_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/the_one_set/hybrid/love_blue.png")
LOVE_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/the_one_set/hybrid/love_black.png")
LOVE_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/the_one_set/hybrid/love_red.png")
LOVE_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/the_one_set/hybrid/love_green.png")
LOVE_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/the_one_set/hybrid/love_colorless.png")

# Other Hybrid Mana
SNOW_LOVE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/the_one_set/hybrid/snow_love.png")

# Standard Trybrid Mana
WHITE_BLUE_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/white_blue_black.png")
BLUE_RED_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/blue_red_white.png")
GREEN_WHITE_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/green_white_blue.png")
RED_WHITE_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/red_white_black.png")
WHITE_BLACK_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/white_black_green.png")
RED_GREEN_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/red_green_white.png")
BLUE_BLACK_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/blue_black_red.png")
BLACK_GREEN_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/black_green_blue.png")
GREEN_BLUE_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/green_blue_red.png")
BLACK_RED_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/black_red_green.png")
WHITE_BLUE_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/white_blue_colorless.png")
WHITE_BLACK_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/white_black_colorless.png")
BLUE_BLACK_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/blue_black_colorless.png")
BLUE_RED_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/blue_red_colorless.png")
BLACK_RED_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/black_red_colorless.png")
BLACK_GREEN_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/black_green_colorless.png")
RED_GREEN_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/red_green_colorless.png")
RED_WHITE_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/red_white_colorless.png")
GREEN_WHITE_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/green_white_colorless.png")
GREEN_BLUE_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/trybrid/green_blue_colorless.png")

# Complex Trybrid Mana
BLACK_DOUBLE_GREEN_PHYREXIAN_SNOW_MANA = open_image(
    f"{MANA_SYMBOLS_PATH}/trybrid/complex/black_double_green_phyrexian_snow.png"
)

# Variable Mana
X_MANA = open_image(f"{MANA_SYMBOLS_PATH}/variable/x.png")
Y_MANA = open_image(f"{MANA_SYMBOLS_PATH}/variable/y.png")
Z_MANA = open_image(f"{MANA_SYMBOLS_PATH}/variable/z.png")

# Other
ENERGY = open_image(f"{MANA_SYMBOLS_PATH}/energy.png")
TICKET = open_image(f"{MANA_SYMBOLS_PATH}/ticket.png")

# Showcase Future Shifted Mana Symbols
FUTURE_SHIFTED_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/white.png")
FUTURE_SHIFTED_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/blue.png")
FUTURE_SHIFTED_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/black.png")
FUTURE_SHIFTED_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/red.png")
FUTURE_SHIFTED_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/green.png")

FUTURE_SHIFTED_ZERO_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/0.png")
FUTURE_SHIFTED_ONE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/1.png")
FUTURE_SHIFTED_TWO_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/2.png")
FUTURE_SHIFTED_THREE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/3.png")
FUTURE_SHIFTED_FOUR_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/4.png")
FUTURE_SHIFTED_FIVE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/5.png")
FUTURE_SHIFTED_SIX_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/6.png")
FUTURE_SHIFTED_SEVEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/7.png")
FUTURE_SHIFTED_EIGHT_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/8.png")
FUTURE_SHIFTED_NINE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/9.png")
FUTURE_SHIFTED_TEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/10.png")
FUTURE_SHIFTED_ELEVEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/11.png")
FUTURE_SHIFTED_TWELVE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/12.png")
FUTURE_SHIFTED_THIRTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/13.png")
FUTURE_SHIFTED_FOURTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/14.png")
FUTURE_SHIFTED_FIFTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/15.png")
FUTURE_SHIFTED_SIXTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/16.png")
FUTURE_SHIFTED_SEVENTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/17.png")
FUTURE_SHIFTED_EIGHTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/18.png")
FUTURE_SHIFTED_NINETEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/19.png")
FUTURE_SHIFTED_TWENTY_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/mono/20.png")

FUTURE_SHIFTED_WHITE_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/hybrid/white_blue.png")
FUTURE_SHIFTED_WHITE_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/hybrid/white_black.png")
FUTURE_SHIFTED_BLUE_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/hybrid/blue_black.png")
FUTURE_SHIFTED_BLUE_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/hybrid/blue_red.png")
FUTURE_SHIFTED_BLACK_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/hybrid/black_red.png")
FUTURE_SHIFTED_BLACK_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/hybrid/black_green.png")
FUTURE_SHIFTED_RED_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/hybrid/red_green.png")
FUTURE_SHIFTED_RED_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/hybrid/red_white.png")
FUTURE_SHIFTED_GREEN_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/hybrid/green_white.png")
FUTURE_SHIFTED_GREEN_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/hybrid/green_blue.png")

FUTURE_SHIFTED_X_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/future/variable/x.png")

# Showcase Future Shifted Mana Symbols
PLAYTEST_WHITE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/white.png")
PLAYTEST_BLUE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/blue.png")
PLAYTEST_BLACK_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/black.png")
PLAYTEST_RED_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/red.png")
PLAYTEST_GREEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/green.png")
PLAYTEST_COLORLESS_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/colorless.png")

PLAYTEST_ZERO_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/0.png")
PLAYTEST_ONE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/1.png")
PLAYTEST_TWO_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/2.png")
PLAYTEST_THREE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/3.png")
PLAYTEST_FOUR_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/4.png")
PLAYTEST_FIVE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/5.png")
PLAYTEST_SIX_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/6.png")
PLAYTEST_SEVEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/7.png")
PLAYTEST_EIGHT_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/8.png")
PLAYTEST_NINE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/9.png")
PLAYTEST_TEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/10.png")
PLAYTEST_ELEVEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/11.png")
PLAYTEST_TWELVE_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/12.png")
PLAYTEST_THIRTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/13.png")
PLAYTEST_FOURTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/14.png")
PLAYTEST_FIFTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/15.png")
PLAYTEST_SIXTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/16.png")
PLAYTEST_SEVENTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/17.png")
PLAYTEST_EIGHTEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/18.png")
PLAYTEST_NINETEEN_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/19.png")
PLAYTEST_TWENTY_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/mono/20.png")

PLAYTEST_X_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/variable/x.png")
PLAYTEST_Y_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/variable/y.png")
PLAYTEST_Z_MANA = open_image(f"{MANA_SYMBOLS_PATH}/showcase/playtest/variable/z.png")


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
    # Mono-Colored Mana (PYCOK)
    "pp": Symbol(PURPLE_MANA),
    "yw": Symbol(YELLOW_MANA),
    "cy": Symbol(CYAN_MANA),
    "or": Symbol(ORANGE_MANA),
    "pk": Symbol(PINK_MANA),
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
    # Other Mono Mana
    "s": Symbol(SNOW_MANA),
    "l": Symbol(LOVE_MANA),
    "triangle": Symbol(TRIANGLE_MANA),
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
    "pw": Symbol(WHITE_PHYREXIAN_MANA),
    "up": Symbol(BLUE_PHYREXIAN_MANA),
    "pu": Symbol(BLUE_PHYREXIAN_MANA),
    "bp": Symbol(BLACK_PHYREXIAN_MANA),
    "pb": Symbol(BLACK_PHYREXIAN_MANA),
    "rp": Symbol(RED_PHYREXIAN_MANA),
    "pr": Symbol(RED_PHYREXIAN_MANA),
    "gp": Symbol(GREEN_PHYREXIAN_MANA),
    "pg": Symbol(GREEN_PHYREXIAN_MANA),
    "cp": Symbol(COLORLESS_PHYREXIAN_MANA),
    "pc": Symbol(COLORLESS_PHYREXIAN_MANA),
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
    "2/c": Symbol(TWO_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/2": Symbol(TWO_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/s": Symbol(TWO_SNOW_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "s/2": Symbol(TWO_SNOW_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    # Hybrid Phyrexian Mana
    "wp/up": Symbol(WHITE_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pw/pu": Symbol(WHITE_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "up/wp": Symbol(WHITE_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pu/pw": Symbol(WHITE_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "wp/bp": Symbol(WHITE_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pw/pb": Symbol(WHITE_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "bp/wp": Symbol(WHITE_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pb/pw": Symbol(WHITE_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "up/bp": Symbol(BLUE_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pu/pb": Symbol(BLUE_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "bp/up": Symbol(BLUE_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pb/pu": Symbol(BLUE_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "up/rp": Symbol(BLUE_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pu/pr": Symbol(BLUE_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "rp/up": Symbol(BLUE_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pr/pu": Symbol(BLUE_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "bp/rp": Symbol(BLACK_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pb/pr": Symbol(BLACK_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "rp/bp": Symbol(BLACK_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pr/pb": Symbol(BLACK_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "bp/gp": Symbol(BLACK_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pb/pg": Symbol(BLACK_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "gp/bp": Symbol(BLACK_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pg/pb": Symbol(BLACK_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "rp/gp": Symbol(RED_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pr/pg": Symbol(RED_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "gp/rp": Symbol(RED_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pg/pr": Symbol(RED_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "rp/wp": Symbol(RED_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pr/pw": Symbol(RED_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "wp/rp": Symbol(RED_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pw/pr": Symbol(RED_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "gp/wp": Symbol(GREEN_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pg/pw": Symbol(GREEN_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "wp/gp": Symbol(GREEN_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pw/pg": Symbol(GREEN_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "gp/up": Symbol(GREEN_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pg/pu": Symbol(GREEN_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "up/gp": Symbol(GREEN_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pu/pg": Symbol(GREEN_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    # Hybrid Generic Phyrexian Mana
    "2/wp": Symbol(TWO_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "wp/2": Symbol(TWO_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/pw": Symbol(TWO_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pw/2": Symbol(TWO_WHITE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/up": Symbol(TWO_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "up/2": Symbol(TWO_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/pu": Symbol(TWO_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pu/2": Symbol(TWO_BLUE_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/bp": Symbol(TWO_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "bp/2": Symbol(TWO_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/pb": Symbol(TWO_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pb/2": Symbol(TWO_BLACK_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/rp": Symbol(TWO_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "rp/2": Symbol(TWO_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/pr": Symbol(TWO_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pr/2": Symbol(TWO_RED_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/gp": Symbol(TWO_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "gp/2": Symbol(TWO_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/pg": Symbol(TWO_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pg/2": Symbol(TWO_GREEN_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/cp": Symbol(TWO_COLORLESS_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "cp/2": Symbol(TWO_COLORLESS_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "2/pc": Symbol(TWO_COLORLESS_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pc/2": Symbol(TWO_COLORLESS_PHYREXIAN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    # Snow Hybrid Mana
    "s/c": Symbol(SNOW_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/s": Symbol(SNOW_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    # Love Hybrid Mana
    "l/w": Symbol(LOVE_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/l": Symbol(LOVE_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "l/u": Symbol(LOVE_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/l": Symbol(LOVE_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "l/b": Symbol(LOVE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/l": Symbol(LOVE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "l/r": Symbol(LOVE_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/l": Symbol(LOVE_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "l/g": Symbol(LOVE_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/l": Symbol(LOVE_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "l/c": Symbol(LOVE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/l": Symbol(LOVE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    # Other Hybrid Mana
    "s/l": Symbol(SNOW_LOVE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "l/s": Symbol(SNOW_LOVE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    # Standard Trybrid Mana
    "w/u/b": Symbol(WHITE_BLUE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/b/u": Symbol(WHITE_BLUE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/w/b": Symbol(WHITE_BLUE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/b/w": Symbol(WHITE_BLUE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/w/u": Symbol(WHITE_BLUE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/u/w": Symbol(WHITE_BLUE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/r/w": Symbol(BLUE_RED_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/w/r": Symbol(BLUE_RED_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/u/w": Symbol(BLUE_RED_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/w/u": Symbol(BLUE_RED_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/u/r": Symbol(BLUE_RED_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/r/u": Symbol(BLUE_RED_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/w/u": Symbol(GREEN_WHITE_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/u/w": Symbol(GREEN_WHITE_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/g/u": Symbol(GREEN_WHITE_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/u/g": Symbol(GREEN_WHITE_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/g/w": Symbol(GREEN_WHITE_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/w/g": Symbol(GREEN_WHITE_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/w/b": Symbol(RED_WHITE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/b/w": Symbol(RED_WHITE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/r/b": Symbol(RED_WHITE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/b/r": Symbol(RED_WHITE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/r/w": Symbol(RED_WHITE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/w/r": Symbol(RED_WHITE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/b/g": Symbol(WHITE_BLACK_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/g/b": Symbol(WHITE_BLACK_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/w/g": Symbol(WHITE_BLACK_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/g/w": Symbol(WHITE_BLACK_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/w/b": Symbol(WHITE_BLACK_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/b/w": Symbol(WHITE_BLACK_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/g/w": Symbol(RED_GREEN_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/w/g": Symbol(RED_GREEN_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/r/w": Symbol(RED_GREEN_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/w/r": Symbol(RED_GREEN_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/r/g": Symbol(RED_GREEN_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/g/r": Symbol(RED_GREEN_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/b/r": Symbol(BLUE_BLACK_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/r/b": Symbol(BLUE_BLACK_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/u/r": Symbol(BLUE_BLACK_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/r/u": Symbol(BLUE_BLACK_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/u/b": Symbol(BLUE_BLACK_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/b/u": Symbol(BLUE_BLACK_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/g/u": Symbol(BLACK_GREEN_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/u/g": Symbol(BLACK_GREEN_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/b/u": Symbol(BLACK_GREEN_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/u/b": Symbol(BLACK_GREEN_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/b/g": Symbol(BLACK_GREEN_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/g/b": Symbol(BLACK_GREEN_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/u/r": Symbol(GREEN_BLUE_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/r/u": Symbol(GREEN_BLUE_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/g/r": Symbol(GREEN_BLUE_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/r/g": Symbol(GREEN_BLUE_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/g/u": Symbol(GREEN_BLUE_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/u/g": Symbol(GREEN_BLUE_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/r/g": Symbol(BLACK_RED_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/g/r": Symbol(BLACK_RED_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/b/g": Symbol(BLACK_RED_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/g/b": Symbol(BLACK_RED_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/b/r": Symbol(BLACK_RED_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/r/b": Symbol(BLACK_RED_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/u/c": Symbol(WHITE_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/c/u": Symbol(WHITE_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/w/c": Symbol(WHITE_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/c/w": Symbol(WHITE_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/w/u": Symbol(WHITE_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/u/w": Symbol(WHITE_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/b/c": Symbol(WHITE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/c/b": Symbol(WHITE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/w/c": Symbol(WHITE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/c/w": Symbol(WHITE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/w/b": Symbol(WHITE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/b/w": Symbol(WHITE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/b/c": Symbol(BLUE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/c/b": Symbol(BLUE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/u/c": Symbol(BLUE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/c/u": Symbol(BLUE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/u/b": Symbol(BLUE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/b/u": Symbol(BLUE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/r/c": Symbol(BLUE_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/c/r": Symbol(BLUE_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/u/c": Symbol(BLUE_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/c/u": Symbol(BLUE_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/u/r": Symbol(BLUE_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/r/u": Symbol(BLUE_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/r/c": Symbol(BLACK_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/c/r": Symbol(BLACK_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/b/c": Symbol(BLACK_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/c/b": Symbol(BLACK_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/b/r": Symbol(BLACK_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/r/b": Symbol(BLACK_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/g/c": Symbol(BLACK_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/c/g": Symbol(BLACK_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/b/c": Symbol(BLACK_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/c/b": Symbol(BLACK_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/b/g": Symbol(BLACK_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/g/b": Symbol(BLACK_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/g/c": Symbol(RED_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/c/g": Symbol(RED_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/r/c": Symbol(RED_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/c/r": Symbol(RED_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/r/g": Symbol(RED_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/g/r": Symbol(RED_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/w/c": Symbol(RED_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/c/w": Symbol(RED_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/r/c": Symbol(RED_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/c/r": Symbol(RED_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/r/w": Symbol(RED_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/w/r": Symbol(RED_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/w/c": Symbol(GREEN_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/c/w": Symbol(GREEN_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/g/c": Symbol(GREEN_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/c/g": Symbol(GREEN_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/g/w": Symbol(GREEN_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/w/g": Symbol(GREEN_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/u/c": Symbol(GREEN_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/c/u": Symbol(GREEN_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/g/c": Symbol(GREEN_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/c/g": Symbol(GREEN_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/g/u": Symbol(GREEN_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "c/u/g": Symbol(GREEN_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    # Complex Trybrid Mana
    "b/pgpg/s": Symbol(BLACK_DOUBLE_GREEN_PHYREXIAN_SNOW_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/s/pgpg": Symbol(BLACK_DOUBLE_GREEN_PHYREXIAN_SNOW_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pgpg/b/s": Symbol(BLACK_DOUBLE_GREEN_PHYREXIAN_SNOW_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "pgpg/s/b": Symbol(BLACK_DOUBLE_GREEN_PHYREXIAN_SNOW_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "s/b/pgpg": Symbol(BLACK_DOUBLE_GREEN_PHYREXIAN_SNOW_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "s/pgpg/b": Symbol(BLACK_DOUBLE_GREEN_PHYREXIAN_SNOW_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    # Variable Mana
    "x": Symbol(X_MANA),
    "y": Symbol(Y_MANA),
    "z": Symbol(Z_MANA),
    # Other
    "e": Symbol(ENERGY),
    "tk": Symbol(TICKET),
}

FUTURE_SHIFTED_SYMBOL_PLACEHOLDER_KEY = {
    # Mono-Colored Mana
    "w": Symbol(FUTURE_SHIFTED_WHITE_MANA),
    "u": Symbol(FUTURE_SHIFTED_BLUE_MANA),
    "b": Symbol(FUTURE_SHIFTED_BLACK_MANA),
    "r": Symbol(FUTURE_SHIFTED_RED_MANA),
    "g": Symbol(FUTURE_SHIFTED_GREEN_MANA),
    # Numbered Mana
    "0": Symbol(FUTURE_SHIFTED_ZERO_MANA),
    "1": Symbol(FUTURE_SHIFTED_ONE_MANA),
    "2": Symbol(FUTURE_SHIFTED_TWO_MANA),
    "3": Symbol(FUTURE_SHIFTED_THREE_MANA),
    "4": Symbol(FUTURE_SHIFTED_FOUR_MANA),
    "5": Symbol(FUTURE_SHIFTED_FIVE_MANA),
    "6": Symbol(FUTURE_SHIFTED_SIX_MANA),
    "7": Symbol(FUTURE_SHIFTED_SEVEN_MANA),
    "8": Symbol(FUTURE_SHIFTED_EIGHT_MANA),
    "9": Symbol(FUTURE_SHIFTED_NINE_MANA),
    "10": Symbol(FUTURE_SHIFTED_TEN_MANA),
    "11": Symbol(FUTURE_SHIFTED_ELEVEN_MANA),
    "12": Symbol(FUTURE_SHIFTED_TWELVE_MANA),
    "13": Symbol(FUTURE_SHIFTED_THIRTEEN_MANA),
    "14": Symbol(FUTURE_SHIFTED_FOURTEEN_MANA),
    "15": Symbol(FUTURE_SHIFTED_FIFTEEN_MANA),
    "16": Symbol(FUTURE_SHIFTED_SIXTEEN_MANA),
    "17": Symbol(FUTURE_SHIFTED_SEVENTEEN_MANA),
    "18": Symbol(FUTURE_SHIFTED_EIGHTEEN_MANA),
    "19": Symbol(FUTURE_SHIFTED_NINETEEN_MANA),
    "20": Symbol(FUTURE_SHIFTED_TWENTY_MANA),
    # Standard Hybrid Mana
    "w/u": Symbol(FUTURE_SHIFTED_WHITE_BLUE_MANA),
    "u/w": Symbol(FUTURE_SHIFTED_WHITE_BLUE_MANA),
    "w/b": Symbol(FUTURE_SHIFTED_WHITE_BLACK_MANA),
    "b/w": Symbol(FUTURE_SHIFTED_WHITE_BLACK_MANA),
    "u/b": Symbol(FUTURE_SHIFTED_BLUE_BLACK_MANA),
    "b/u": Symbol(FUTURE_SHIFTED_BLUE_BLACK_MANA),
    "u/r": Symbol(FUTURE_SHIFTED_BLUE_RED_MANA),
    "r/u": Symbol(FUTURE_SHIFTED_BLUE_RED_MANA),
    "b/r": Symbol(FUTURE_SHIFTED_BLACK_RED_MANA),
    "r/b": Symbol(FUTURE_SHIFTED_BLACK_RED_MANA),
    "b/g": Symbol(FUTURE_SHIFTED_BLACK_GREEN_MANA),
    "g/b": Symbol(FUTURE_SHIFTED_BLACK_GREEN_MANA),
    "r/g": Symbol(FUTURE_SHIFTED_RED_GREEN_MANA),
    "g/r": Symbol(FUTURE_SHIFTED_RED_GREEN_MANA),
    "r/w": Symbol(FUTURE_SHIFTED_RED_WHITE_MANA),
    "w/r": Symbol(FUTURE_SHIFTED_RED_WHITE_MANA),
    "g/w": Symbol(FUTURE_SHIFTED_GREEN_WHITE_MANA),
    "w/g": Symbol(FUTURE_SHIFTED_GREEN_WHITE_MANA),
    "g/u": Symbol(FUTURE_SHIFTED_GREEN_BLUE_MANA),
    "u/g": Symbol(FUTURE_SHIFTED_GREEN_BLUE_MANA),
    # Variable Mana
    "x": Symbol(FUTURE_SHIFTED_X_MANA),
}

PLAYTEST_SYMBOL_PLACEHOLDER_KEY = {
    # Mono-Colored Mana
    "w": Symbol(PLAYTEST_WHITE_MANA),
    "u": Symbol(PLAYTEST_BLUE_MANA),
    "b": Symbol(PLAYTEST_BLACK_MANA),
    "r": Symbol(PLAYTEST_RED_MANA),
    "g": Symbol(PLAYTEST_GREEN_MANA),
    "c": Symbol(PLAYTEST_COLORLESS_MANA),
    # Numbered Mana
    "0": Symbol(PLAYTEST_ZERO_MANA),
    "1": Symbol(PLAYTEST_ONE_MANA),
    "2": Symbol(PLAYTEST_TWO_MANA),
    "3": Symbol(PLAYTEST_THREE_MANA),
    "4": Symbol(PLAYTEST_FOUR_MANA),
    "5": Symbol(PLAYTEST_FIVE_MANA),
    "6": Symbol(PLAYTEST_SIX_MANA),
    "7": Symbol(PLAYTEST_SEVEN_MANA),
    "8": Symbol(PLAYTEST_EIGHT_MANA),
    "9": Symbol(PLAYTEST_NINE_MANA),
    "10": Symbol(PLAYTEST_TEN_MANA),
    "11": Symbol(PLAYTEST_ELEVEN_MANA),
    "12": Symbol(PLAYTEST_TWELVE_MANA),
    "13": Symbol(PLAYTEST_THIRTEEN_MANA),
    "14": Symbol(PLAYTEST_FOURTEEN_MANA),
    "15": Symbol(PLAYTEST_FIFTEEN_MANA),
    "16": Symbol(PLAYTEST_SIXTEEN_MANA),
    "17": Symbol(PLAYTEST_SEVENTEEN_MANA),
    "18": Symbol(PLAYTEST_EIGHTEEN_MANA),
    "19": Symbol(PLAYTEST_NINETEEN_MANA),
    "20": Symbol(PLAYTEST_TWENTY_MANA),
    # Variable Mana
    "x": Symbol(PLAYTEST_X_MANA),
    "y": Symbol(PLAYTEST_Y_MANA),
    "z": Symbol(PLAYTEST_Z_MANA),
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

# Future Shifted
FUTURE_SHIFTED_TYPE_ICON_KEY = {
    "artifact": Symbol(open_image(f"{FRAMES_PATH}/showcase/future/type_icon/artifact.png")),
    "creature": Symbol(open_image(f"{FRAMES_PATH}/showcase/future/type_icon/creature.png")),
    "enchantment": Symbol(open_image(f"{FRAMES_PATH}/showcase/future/type_icon/enchantment.png")),
    "instant": Symbol(open_image(f"{FRAMES_PATH}/showcase/future/type_icon/instant.png")),
    "land": Symbol(open_image(f"{FRAMES_PATH}/showcase/future/type_icon/land.png")),
    "planeswalker": Symbol(open_image(f"{FRAMES_PATH}/showcase/future/type_icon/planeswalker.png")),
    "sorcery": Symbol(open_image(f"{FRAMES_PATH}/showcase/future/type_icon/sorcery.png")),
    "multitype": Symbol(open_image(f"{FRAMES_PATH}/showcase/future/type_icon/multitype.png")),
}

# Other
RULES_DIVIDING_LINE = Symbol(open_image("images/other/divider.png"))
LIGHT_RULES_DIVIDING_LINE = Symbol(open_image("images/other/light_divider.png"))
ARTIST_BRUSH = Symbol(open_image("images/collector_info/artist_brush.png"), 1.25)
