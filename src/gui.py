

import board
from cache import Cache
from PIL import Image, ImageTk

class Gallery(object):

    def __init__(self, imageDir: str):
        self.imageDir = imageDir
        self.rawPilImageCache = Cache()
        self.pilImageCache = Cache()
        self.tkImageCache = Cache()

    def get_raw_pil_image(self, id: str):
        return self.rawPilImageCache.get_or_load(id, lambda id: Image.open(f"{self.imageDir}/{id}.png"))

    def get_pil_image(self, app, id: str, dimensions: (int, int)):
        def load_pil_image(id: str):
            pilImage = self.get_raw_pil_image(id)
            (originalWidth, originalHeight) = pilImage.size
            (targetHeightInPixels, targetWidthInPixels) = dimensions
            (pixelWidth, pixelHeight) = board.board_pixel_size(app)
            # Scale width and height
            newHeight = pixelHeight * targetHeightInPixels
            newWidth = pixelWidth * targetWidthInPixels
            # Use of resize() taken from cmu_112_graphics
            pilImage = pilImage.resize((round(newWidth), round(newHeight)), resample=Image.ANTIALIAS)
            return pilImage
        return self.pilImageCache.get_or_load(id, load_pil_image)

    def get_tkinter_image(self, app, id: str, dimensions: (int, int), pilImage = None):
        def load_tkinter_image(id: str):
            nonlocal pilImage
            if pilImage == None:
                pilImage = self.get_pil_image(app, id, dimensions)
            return ImageTk.PhotoImage(pilImage)
        return self.tkImageCache.get_or_load(id, load_tkinter_image)

def galaga_sizeChanged(app):
    # Purge tkinter image and pil image cache, but NOT raw pil image cache
    gallery = app.galaga.gallery
    gallery.pilImageCache.purge()
    gallery.tkImageCache.purge()

def galaga_redrawAll(app, canvas):
    game = app.galaga.game
    for drawableEntity in game.drawableEntities:
        drawableEntity.draw_on(app, canvas)
    # Make sure to draw the aliens in the correct order
    # Draw the incoming aliens before the existing ones
    for alienGroup in [game.incomingAliens, game.aliens]:
        # Draw the alive ones before the dead ones to show explosions in background
        for liveStatus in [True, False]:
            draw_aliens(app, canvas, alienGroup, liveStatus)

def draw_aliens(app, canvas, aliens: set, alive: bool) -> None:
    for alien in aliens:
        if alien.is_alive() == alive:
            alien.draw_on(app, canvas)

def galaga_keyPressed(app, event) -> None:
    game = app.galaga.game
    key = event.key
    if key == 'Right':
        game.move_each_starship(1)
    elif key == 'Left':
        game.move_each_starship(-1)
    elif key == 'Space':
        game.fire_starship_shot()
