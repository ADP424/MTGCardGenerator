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

    if word.endswith('"'):
        word = word[:-1] + "”"
    word = word.replace('"', "“")
    if word.startswith("'"):
        word = "‘" + word[1:]
    word = word.replace("'", "’")

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
