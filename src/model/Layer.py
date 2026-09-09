from PIL import Image


class Layer:
    """
    A single layer of a card.

    Attributes
    ----------
    image: Image
        The image displayed on the layer.

    position: tuple[int, int], default: (0, 0)
        The position of the layer relative to the top left corner of the image.

    base_size: tuple[int, int], optional
        The (width, height) the layer's image and position were authored at, if it was loaded from
        a frame path (see `constants.FRAME_DIRECTORY_BASE_SIZES`). `None` for layers that aren't
        full-card frame images (art, text, collector info, etc.), which are never rescaled.
        When set and it doesn't match the card's own canvas size, `render_card` scales the image
        and position by the ratio between them right before compositing, so frame families authored
        at different resolutions (e.g. legacy 1500x2100 vs. 2010x2814) can be mixed on one card.
    """

    def __init__(self, image: Image.Image, position: tuple[int, int] = (0, 0), base_size: tuple[int, int] = None):
        self.image = image
        self.position = position
        self.base_size = base_size
