import re
from datetime import MINYEAR, datetime

from PIL import Image, ImageChops, ImageFont

from log import log


def load_font(filepath: str, size: int) -> ImageFont.FreeTypeFont:
    """
    Load a TrueType font using the Raqm layout engine, which is required for correct shaping
    (conjuncts, ligatures, glyph reordering) of complex scripts like Bengali, Devanagari, Tamil,
    and Arabic. Falls back to Pillow's basic layout if Raqm isn't available in this environment.

    Parameters
    ----------
    filepath: str
        The path to the font file to load.

    size: int
        The font size, in pixels, to load the font at.

    Returns
    -------
    ImageFont.FreeTypeFont
        The loaded font.
    """

    try:
        return ImageFont.truetype(filepath, size, layout_engine=ImageFont.Layout.RAQM)
    except ImportError:
        return ImageFont.truetype(filepath, size)


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


def apply_alpha_mask(image: Image.Image, mask: Image.Image) -> Image.Image:
    """
    Multiply an image's alpha by a mask, preserving RGB to avoid banding.

    Parameters
    ----------
    image: Image
        The image to mask. Converted to RGBA if it isn't already.

    mask: Image
        The mask to multiply the image's alpha by. Resized to `image`'s size if they don't match.

    Returns
    -------
    Image
        `image` with its alpha channel multiplied by `mask`.
    """

    image = image.convert("RGBA")
    r, g, b, alpha = image.split()
    if mask.size != image.size:
        mask = mask.resize(image.size)
    return Image.merge("RGBA", (r, g, b, ImageChops.multiply(alpha, mask)))


def allocate_by_weight(weights: list[float], total: int, minimum: int | list[int]) -> list[int]:
    """
    Split `total` whole units between items with the given weights, never going under each item's
    minimum. Uses the largest-remainder method, breaking ties in favour of heavier items.

    Parameters
    ----------
    weights : list[float]
        The relative share each item wants.

    total : int
        The number of units to hand out.

    minimum : int | list[int]
        The fewest units any one item may get, either one value for all items or one per item.

    Returns
    -------
    list[int]
        A unit count per item, summing to `total` where possible.
    """

    count = len(weights)
    if count == 0:
        return []
    minimums = minimum if isinstance(minimum, list) else [minimum] * count
    safe = [max(weight, 0.01) for weight in weights]
    total_weight = sum(safe)

    ideals = [total * weight / total_weight for weight in safe]
    result = [max(int(ideal), minimums[index]) for index, ideal in enumerate(ideals)]

    difference = total - sum(result)
    if difference > 0:
        order = sorted(range(count), key=lambda i: (ideals[i] - result[i], safe[i]), reverse=True)
        for index in range(difference):
            result[order[index % count]] += 1
    while sum(result) > total:
        shrinkable = [index for index in range(count) if result[index] > minimums[index]]
        if not shrinkable:
            log("Tried to allocate more units than the total allows even at each item's minimum. Some will overflow.")
            break
        result[max(shrinkable, key=lambda i: result[i])] -= 1

    return result


def union_alpha_channel(canvas: Image.Image, alpha: Image.Image, position: tuple[int, int]):
    """
    Union an alpha channel into an "L" canvas, keeping whichever is more opaque.

    Parameters
    ----------
    canvas : Image
        The "L" canvas to union `alpha` into, modified in place.

    alpha : Image
        The alpha channel to union into `canvas`.

    position : tuple[int, int]
        Where `alpha`'s top left corner goes on `canvas`.
    """

    box = (position[0], position[1], position[0] + alpha.width, position[1] + alpha.height)
    canvas.paste(ImageChops.lighter(canvas.crop(box), alpha), box)


def subtract_intervals(start: int, end: int, intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Return the parts of [start, end) that no interval covers.

    Parameters
    ----------
    start : int
        The start of the range to cut up.

    end : int
        The end of the range to cut up.

    intervals : list[tuple[int, int]]
        The ranges to remove from it.

    Returns
    -------
    list[tuple[int, int]]
        Whatever is left, left to right.
    """

    pieces = [(start, end)]
    for gap_start, gap_end in intervals:
        remaining: list[tuple[int, int]] = []
        for piece_start, piece_end in pieces:
            if gap_end <= piece_start or gap_start >= piece_end:
                remaining.append((piece_start, piece_end))
                continue
            if gap_start > piece_start:
                remaining.append((piece_start, gap_start))
            if gap_end < piece_end:
                remaining.append((gap_end, piece_end))
        pieces = remaining
    return [piece for piece in pieces if piece[1] > piece[0]]


def alpha_composite_clipped(base: Image.Image, piece: Image.Image, position: tuple[int, int]):
    """
    Alpha composite a piece onto a base image, cropping it to whatever lands on the base image.

    Parameters
    ----------
    base : Image
        The RGBA image to composite `piece` onto, modified in place.

    piece : Image
        The image to composite onto `base`.

    position : tuple[int, int]
        Where `piece`'s top left corner goes on `base`.
    """

    x, y = position
    left = max(-x, 0)
    top = max(-y, 0)
    right = min(piece.width, base.width - x)
    bottom = min(piece.height, base.height - y)
    if right <= left or bottom <= top:
        return
    if (left, top, right, bottom) != (0, 0, piece.width, piece.height):
        piece = piece.crop((left, top, right, bottom))
    base.alpha_composite(piece, dest=(x + left, y + top))


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


def get_card_key(
    card_title: str,
    card_additional_titles: str | list[str] = [],
    card_descriptor: str = "",
    card_spellbook: str = "",
) -> str:
    """
    Return a card's unique identifier based on its title, additional titles, and descriptor.
    Remove any formatting placeholders like "{UCS}".

    Parameters
    ----------
    card_title: str
        The primary title of the card.

    card_additional_titles: str | list[str], optional
        Any additional titles the card has, either as a list of string with titles separated with newlines.

    card_descriptor: str, optional
        The extra descriptor of the card, if it has one.

    card_spellbook: str, optional
        The spellbook this card belongs to, if it belongs to one.

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
    card_key += f" - {re.sub(r"{.*?}", "", card_spellbook)}" if len(card_spellbook) > 0 else ""

    return card_key


def int_to_roman_numeral(num: int) -> str:
    """
    Convert a decimal number to its Roman numeral representation.
    This function handles positive integers. For numbers 4,000 and above, it uses vinculum (overline) notation
    where a bar over numerals means they are multiplied by 1,000. For example, V̅ = 5,000, X̅ = 10,000.

    Parameters:
    -----------
    num: int
        The positive integer to convert.

    Returns:
    --------
    str
        The Roman numeral representation of `num`.

    Raises:
    -------
    ValueError
        If the input is zero or negative.
    """

    if num <= 0:
        raise ValueError("Roman numerals cannot be zero or negative.")

    val_symbol_pairs = [
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

    OVERLINE = "\u0305"

    def convert_under_4000(n: int) -> str:
        """
        Convert a number less than 4000 to Roman numerals.
        """

        result = ""
        for value, symbol in val_symbol_pairs:
            while n >= value:
                result += symbol
                n -= value
        return result

    def add_overline(text: str) -> str:
        """
        Add an overline to each character in the text.
        """

        return "".join(char + OVERLINE for char in text)

    if num < 4000:
        return convert_under_4000(num)

    result = ""

    thousands = num // 1000
    remainder = num % 1000

    if thousands > 0:
        if thousands >= 4000:
            result = add_overline(int_to_roman_numeral(thousands))
        else:
            result = add_overline(convert_under_4000(thousands))

    if remainder > 0:
        result += convert_under_4000(remainder)

    return result


def add_drop_shadow(
    image: Image.Image, offset: tuple[int, int], color: tuple[int, int, int] = (0, 0, 0)
) -> Image.Image:
    """
    Apply drop shadow to an image.

    Parameters
    ----------
    symbol_image: Image
        The image to add drop shadow to.

    offset: tuple[float, float]
        Offset of the shadow relative to the image in the form (x, y).

    color: tuple[int, int, int], default: (0, 0, 0)
        The color of the drop shadow.

    Returns
    -------
    Image
        The image provided, now with a drop shadow.
    """

    if offset == (0, 0):
        return image

    alpha = image.getchannel("A")
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    solid_color = Image.new("RGB", image.size, color)
    shadow.paste(solid_color, mask=alpha)

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


def str_to_int(string: str, default: int = 0) -> int:
    """
    Convert a string to an int if able. Otherwise, return the default.

    Parameters
    ----------
    string: str
        The string to convert to an integer.

    default: int, default: 0
        The integer to return if the conversion isn't possible.

    Returns
    -------
    int
        The `string` converted to an int, or `default` if conversion failed.
    """

    try:
        return int(string)
    except ValueError:
        return default


def str_to_float(string: str, default: float = 0) -> float:
    """
    Convert a string to a float if able. Otherwise, return the default.

    Parameters
    ----------
    string: str
        The string to convert to an integer.

    default: float, default: 0
        The float to return if the conversion isn't possible.

    Returns
    -------
    float
        The `string` converted to a float, or `default` if conversion failed.
    """

    try:
        return float(string)
    except ValueError:
        return default


def str_to_datetime(
    string: str,
    default: datetime = datetime(MINYEAR, 1, 1),
    str_format: str = "%m/%d/%Y",
) -> datetime:
    """
    Convert a string to a datetime object of the given form if able. Otherwise, return the default.

    Parameters
    ----------
    string: str
        The string to convert to a datetime object.

    default: datetime, default: datetime(MINYEAR, 1, 1)
        The datetime to return if the conversion isn't possible.

    str_format: str, default: "%m/%d/%Y"
        The format of the date in `string`.

    Returns
    -------
    int
        The `string` converted to a datetime object, or `default` if conversion failed.
    """

    try:
        return datetime.strptime(string, str_format)
    except ValueError:
        return default
