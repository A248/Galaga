import math
import board
from PIL import Image

class Cache(object):
    def __init__(self):
        self.cache = dict()

    def get_or_load(self, key, loadFn):
        value = self.cache.get(key)
        if value == None:
            value = loadFn(key)
            self.cache[key] = value
        return value

    def purge(self):
        self.cache = dict()

class ImageHandler(object):
    def __eq__(self, other) -> bool:
        if not isinstance(other, ImageHandler):
            return False
        return self.cache_key() == other.cache_key()

    def __hash__(self):
        return hash(self.cache_key())

    # Handles a pil image, returning a new image
    def handle_image(self, app, pilImage):
        raise Error("Must be implemented by sub-classes")

    # Returns an object implementing __eq__ to be used as a cache key
    def cache_key(self, pilImage):
        raise Error("Must be implemented by sub-classes")

class ImageResizer(ImageHandler):
    def __init__(self, dimensions: (int, int)):
        self.dimensions = dimensions

    def handle_image(self, app, pilImage):
        (originalWidth, originalHeight) = pilImage.size
        (targetHeightInPixels, targetWidthInPixels) = self.dimensions
        (pixelWidth, pixelHeight) = board.board_pixel_size(app)
        # Scale width and height
        newHeight = pixelHeight * targetHeightInPixels
        newWidth = pixelWidth * targetWidthInPixels
        # Use of resize() taken from cmu_112_graphics
        return pilImage.resize((round(newWidth), round(newHeight)), resample=Image.ANTIALIAS)

    def cache_key(self):
        return self.dimensions

class ImageRotator(ImageHandler):
    def __init__(self, direction):
        self.direction = direction

    def handle_image(self, app, pilImage):
        # pilImage.rotate() uses clockwise degrees
        clockwiseRadians = -math.pi / 2 + self.direction.radians
        if abs(clockwiseRadians) < 10**-5:
            # Fast path: skip no-op rotation
            return pilImage
        clockwiseDegrees = clockwiseRadians * 180 / math.pi
        return pilImage.rotate(clockwiseDegrees, fillcolor = app.backgroundColor)

    def cache_key(self):
        return self.direction

class CombinedImageHandler(ImageHandler):
    def __init__(self, *handlers):
        self.handlers = handlers

    def handle_image(self, app, pilImage):
        for handler in self.handlers:
            pilImage = handler.handle_image(app, pilImage)
        return pilImage

    def cache_key(self):
        cacheKeys = [ handler.cache_key() for handler in self.handlers ]
        return tuple(cacheKeys)
