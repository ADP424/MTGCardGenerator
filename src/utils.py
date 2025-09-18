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
    except Exception:
        return None


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
    }

    file_name = card_name
    for bad_char in CHAR_TO_TITLE_CHAR.keys():
        file_name = file_name.replace(bad_char, CHAR_TO_TITLE_CHAR[bad_char])

    return file_name
