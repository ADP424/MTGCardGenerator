from PIL import Image


class Symbol:
    """
    A single image of a symbol that can show up on a card.

    Attributes
    ----------
    image: Image
        The image of the symbol.

    size_ratio: float, default: 1.0
        The ratio of the size of this symbol to the regular size the symbol would appear as.

    outline_size: int, default: 0
        The size of the outline to draw around the image.

    outline_color: tuple[int, int, int]: default: (0, 0, 0)
        The color of the outline to draw around the image.
    """

    def __init__(
        self,
        image: Image.Image,
        size_ratio: float = 1.0,
        outline_size: int = 0,
        outline_color: tuple[int, int, int] = (0, 0, 0),
    ):
        self.image = image
        self.size_ratio = size_ratio
        self.outline_size = outline_size
        self.outline_color = outline_color

    def get_formatted_image(self, new_width: int = -1, new_height: int = -1) -> Image.Image:
        """
        Returns a resized, formatted version of the image based on the options passed into the constructor.

        Parameters
        ----------
        new_width: int, optional
            The width to resize the image to. Keeps its original width if left blank.

        new_height: int, optional
            The height to resize the image to. Keeps its original height if left blank.

        Returns
        -------
        Image
            The newly formatted image.
        """

        if new_width < 0:
            new_width = self.image.width

        if new_height < 0:
            new_height = self.image.height

        # resize
        resized_image = self.image.resize(
            (int(new_width * self.size_ratio), int(new_height * self.size_ratio)), Image.LANCZOS
        )

        # add outline
        alpha = resized_image.getchannel("A")
        outlined_image = Image.new(
            "RGBA",
            (resized_image.width + 2 * self.outline_size, resized_image.height + 2 * self.outline_size),
            (0, 0, 0, 0),
        )
        for dx in range(-self.outline_size, self.outline_size + 1):
            for dy in range(-self.outline_size, self.outline_size + 1):
                if dx**2 + dy**2 <= self.outline_size**2:
                    outlined_image.paste(
                        self.outline_color, (dx + self.outline_size, dy + self.outline_size), mask=alpha
                    )
        outlined_image.paste(resized_image, (self.outline_size, self.outline_size), mask=alpha)

        return outlined_image
