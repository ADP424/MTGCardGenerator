from PIL import Image


class Symbol:
    """
    A single image of a symbol that can show up on a card.

    Attributes
    ----------
    image: Image
        The image of the symbol.

    size_ratio: float | tuple[float, float], default: 1.0
        The ratio of the size of this symbol to the regular size the symbol would appear as.
        If given as a tuple of (width, height), width and height ratios are computed separately.

    recolorable: bool, default: False
        Whether this symbol is a flat-colored glyph that should be tinted to match surrounding
        text color, rather than a full-color icon (e.g. mana symbols) that should never be recolored.
    """

    def __init__(
        self,
        image: Image.Image,
        size_ratio: float = 1.0,
        recolorable: bool = False,
    ):
        self.image = image
        self.size_ratio = size_ratio if isinstance(size_ratio, tuple) else (size_ratio, size_ratio)
        self.recolorable = recolorable

    def get_formatted_image(
        self,
        new_width: int = -1,
        new_height: int = -1,
        outline_size: int = 0,
        outline_color: tuple[int, int, int] = (0, 0, 0),
        ignore_size_ratio: bool = False,
        tint_color: str | tuple[int, int, int] | None = None,
    ) -> Image.Image:
        """
        Returns a resized, formatted version of the image based on the options passed into the constructor.

        Parameters
        ----------
        new_width: int, optional
            The width to resize the image to. Keeps its original width if left blank.

        new_height: int, optional
            The height to resize the image to. Keeps its original height if left blank.

        outline_size: int, default: 0
            The size of the outline to draw around the image.

        outline_color: tuple[int, int, int]: default: (0, 0, 0)
            The color of the outline to draw around the image.

        ignore_size_ratio: bool, default: False
            Whether to ignore the size ratio passed into the constructor and just render the image at its normal size.

        tint_color: str | tuple[int, int, int] | None, default: None
            The color to tint this symbol to. Ignored unless `recolorable` was set on the constructor.

        Returns
        -------
        Image
            The newly formatted image.
        """

        if new_width < 0:
            new_width = self.image.width

        if new_height < 0:
            new_height = self.image.height

        size_ratio = self.size_ratio if not ignore_size_ratio else (1, 1)

        # resize
        resized_image = self.image.resize(
            (int(new_width * size_ratio[0]), int(new_height * size_ratio[1])),
            Image.LANCZOS,
        )

        # tint
        if self.recolorable and tint_color is not None:
            tinted_image = Image.new("RGBA", resized_image.size, tint_color)
            tinted_image.putalpha(resized_image.getchannel("A"))
            resized_image = tinted_image

        # add outline
        alpha = resized_image.getchannel("A")
        outlined_image = Image.new(
            "RGBA",
            (
                resized_image.width + 2 * outline_size,
                resized_image.height + 2 * outline_size,
            ),
            (0, 0, 0, 0),
        )
        for dx in range(-outline_size, outline_size + 1):
            for dy in range(-outline_size, outline_size + 1):
                if dx**2 + dy**2 <= outline_size**2:
                    outlined_image.paste(
                        outline_color,
                        (dx + outline_size, dy + outline_size),
                        mask=alpha,
                    )
        outlined_image.paste(resized_image, (outline_size, outline_size), mask=alpha)

        return outlined_image
