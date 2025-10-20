import re
from PIL import Image


def open_image(filepath: str) -> Image.Image | None:
    """
    Open the image file at the given path and do the necessary conversions.
    If no image is found, return None instead.

    Parameters
    ----------
    filepath: str
        The path to the image to open.

    Returns
    -------
    Image | None
        The image at the given filepath, or None if not found.
    """

    try:
        return Image.open(filepath).convert("RGBA")
    except FileNotFoundError:
        return None


def paste_image(image: Image.Image, base_image: Image.Image, position: tuple[int, int]) -> Image.Image:
    """
    Paste an image onto the given base image.

    Parameters
    ----------
    image: Image
        The image to paste onto the `base_image`.

    base_image: Image
        The image to paste `image` onto at the given `position`.

    position: tuple[int, int]
        The position to paste `image` onto `base_image` as (x, y).

    Returns
    -------
    Image
        The result of `image` pasted onto `base_image` at `position`.
        Returns the base_image unchanged if `image` is None.
    """

    if image is not None:
        temp = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
        temp.paste(image, position)
        return Image.alpha_composite(base_image, temp)
    return base_image


def replace_ticks(word: str) -> str:
    """
    Replace ticks `'` and double ticks `"` with correctly facing apostrophes and quotation marks.

    Parameters
    ----------
    word: str
        The word to replace the ticks in.

    Returns
    -------
    str
        The converted word.
    """

    if word.startswith('"'):
        word = "“" + word[1:]
    elif word.startswith("'"):
        word = "‘" + word[1:]

    if '"' in word:

        # Handle trailing punctuation
        match = re.match(r'^(.*?)(["\'])(\W*)$', word)
        if match:
            core, quote, punct = match.groups()
            if quote == '"':
                word = core + "”" + punct
            else:
                word = core + "’" + punct
        else:
            word = word.replace('"', "“").replace("'", "‘")

    word = word.replace('"', "”").replace("'", "’")

    return word


def cardname_to_filename(card_name: str) -> str:
    """
    Return `card_name` with all characters not allowed in a file name replaced.

    Parameters
    ----------
    card_name: str
        The card name to convert to a legal file name.

    Returns
    -------
    str
        The card name converted to a legal file name.
    """

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
        "\n": "{N}",
    }

    file_name = card_name
    for bad_char in CHAR_TO_TITLE_CHAR.keys():
        file_name = file_name.replace(bad_char, CHAR_TO_TITLE_CHAR[bad_char])

    return file_name


def get_card_key(card_title: str, card_additional_titles: str | list[str] = [], card_descriptor: str = "") -> str:
    """
    Return a card's unique identifier based on its title, additional titles, and descriptor.
    Removes any formatting placeholders like "{UCS}".

    Parameters
    ----------
    card_title: str
        The primary title of the card.

    card_additional_titles: str | list[str], optional
        Any additional titles the card has, either as a list of string with titles separated with newlines.

    card_descriptor: str, optional
        The extra descriptor of the card, if it has one.

    Returns
    -------
    str
        The completed key, with the title/additional titles(s)/descriptor all separated by hyphens.
    """

    if isinstance(card_additional_titles, str):
        card_additional_titles = card_additional_titles.split("\n")

    card_key = re.sub(r"{.*?}", "", card_title)
    for title in card_additional_titles:
        title = re.sub(r"{.*?}", "", title.strip())
        if len(title) > 0:
            card_key += f" - {title}"
    card_key += f" - {re.sub(r"{.*?}", "", card_descriptor)}" if len(card_descriptor) > 0 else ""

    return card_key


def int_to_roman_numeral(num: int) -> str:
    """
    Convert an integer to its Roman numeral representation. Can handle values between 1 and 3999 (inclusive).

    Parameters
    ----------
    num: int
        The number to convert to a Roman numeral. Returns an empty string if not 1 <= `num` <= 3999.
    """

    if not (1 <= num <= 3999):
        return ""

    numeral_map = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    roman_numeral = ""
    for value, symbol in numeral_map:
        while num >= value:
            roman_numeral += symbol
            num -= value
    return roman_numeral


def add_drop_shadow(image: Image.Image, offset: tuple[int, int]) -> Image.Image:
    """
    Apply drop shadow to an image.

    Parameters
    ----------
    symbol_image: Image
        The image to add drop shadow to.

    offset: tuple[float, float]
        Offset of the shadow relative to the image in the form (x, y).

    Returns
    -------
    Image
        The image provided, now with a drop shadow.
    """

    if offset == (0, 0):
        return image

    alpha = image.getchannel("A")
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    black = Image.new("L", image.size)
    shadow.paste(black, mask=alpha)

    # Make a new image big enough for shadow to fit with the symbol
    total_width = int(image.width + abs(offset[0]))
    total_height = int(image.height + abs(offset[1]))
    result = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))

    # Paste shadow first, then the symbol over it
    if offset[0] >= 0:
        symbol_x = 0
        shadow_x = offset[0]
    else:
        symbol_x = -offset[0]
        shadow_x = 0
    if offset[1] >= 0:
        symbol_y = 0
        shadow_y = offset[1]
    else:
        symbol_y = -offset[1]
        shadow_y = 0

    result.alpha_composite(shadow, (shadow_x, shadow_y))
    result.alpha_composite(image, (symbol_x, symbol_y))

    return result
