from PIL import Image


class Layer:
    """
    A single layer of a card.

    Attributes
    ----------
    image: Image
        The image displayed on the layer.

    position: tuple[int, int], default : (0, 0)
        The position of the layer relative to the top left corner of the image.
    """

    def __init__(self, image: Image.Image, position: tuple[int, int] = (0, 0)):
        self.image = image
        self.position = position
