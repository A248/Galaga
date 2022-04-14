

import board
from PIL import Image, ImageTk

class Gallery(object):

    def __init__(self, imageDir: str):
        self.imageDir = imageDir
        self.pilImageCache = dict()
        self.tkImageCache = dict()

    def get_pil_image(self, id: str) -> dict:
        cached_image = self.pilImageCache.get(id)
        if cached_image == None:
            # Image.open taken from cmu_112_graphics
            cached_image = Image.open(f"{self.imageDir}/{id}.png")
            self.pilImageCache[id] = cached_image
        return cached_image

    def get_tkinter_image(self, app, id: str, dimensions: (int, int)):
        cached_image = self.tkImageCache.get(id)
        if cached_image == None:
            cached_image = self.get_tkinter_image_uncached(app, id, dimensions)
            self.tkImageCache[id] = cached_image
        return cached_image

    def get_tkinter_image_uncached(self, app, id: str, dimensions: (int, int)):
        pilImage = self.get_pil_image(id)
        (originalWidth, originalHeight) = pilImage.size
        (targetHeightInPixels, targetWidthInPixels) = dimensions
        (pixelWidth, pixelHeight) = board.board_pixel_size(app)
        # Scale width and height
        newHeight = pixelHeight * targetHeightInPixels
        newWidth = pixelWidth * targetWidthInPixels
        # Use of resize() taken from cmu_112_graphics
        pilImage = pilImage.resize((round(newWidth), round(newHeight)), resample=Image.ANTIALIAS)
        return ImageTk.PhotoImage(pilImage)

def galaga_sizeChanged(app):
    # Purge tkiner image cache, but NOT pil image cache
    app.galaga.gallery.imageCache = dict()

def galaga_redrawAll(app, canvas):
    game = app.galaga.game
    for drawableEntity in game.drawableEntities:
        drawableEntity.draw_on(app, canvas)
    # Make sure to draw the new aliens after the existing ones
    # Draw the dead ones before the alive ones to show explosions in background
    for incomingAlien in game.incomingAliens:
        if not incomingAlien.is_alive():
            incomingAlien.draw_on(app, canvas)
    for incomingAlien in game.incomingAliens:
        if incomingAlien.is_alive():
            incomingAlien.draw_on(app, canvas)

def galaga_keyPressed(app, event) -> None:
    game = app.galaga.game
    key = event.key
    if key == 'Right':
        game.move_each_starship(1)
    elif key == 'Left':
        game.move_each_starship(-1)
    elif key == 'Space':
        game.fire_starship_shot()
