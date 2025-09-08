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
    """

    def __init__(self, image: Image.Image, size_ratio: float = 1.0):
        self.image = image
        self.size_ratio = size_ratio
