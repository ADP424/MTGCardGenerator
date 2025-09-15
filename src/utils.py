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

    file_name = card_name.replace("’", "'")
    for bad_char in CHAR_TO_TITLE_CHAR.keys():
        file_name = file_name.replace(bad_char, CHAR_TO_TITLE_CHAR[bad_char])
    return file_name


# def get_token_full_name(token: dict[str, str]) -> str:
#     color = token[CARD_COLOR]
#     token_color = ""
#     if "Colorless" in color:
#         token_color = "Colorless "
#     else:
#         for char in color.strip():
#             try:
#                 token_color += f"{COLORS[char]} "
#             except:
#                 log(f"""Token "{token[CARD_NAME]}" has an invalid color identity.""")
#                 token_color = ""
#                 break

#     if len(token_color) == 0:
#         log(f"""Token "{token[CARD_NAME]}" has an invalid color identity.""")
#         return None

#     token_descriptor = token[DESCRIPTOR].strip()
#     if len(token_descriptor) > 0:
#         token_descriptor = f" - {token_descriptor}"

#     token_supertypes = token[CARD_SUPERTYPES]
#     token_types = token[CARD_TYPESS]
#     return f"{token_color}{token_supertypes} {token[CARD_NAME]} {token_types}{token_descriptor}"
