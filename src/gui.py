

import board
from image_cache import Cache
from PIL import Image, ImageTk

class Gallery(object):

    def __init__(self, imageDir: str):
        self.imageDir = imageDir
        self.rawPilImageCache = Cache()
        self.pilImageCache = Cache()
        self.tkImageCache = Cache()

    def get_raw_pil_image(self, id: str):
        # Use of Image.open() taken from cmu_112_graphics
        return self.rawPilImageCache.get_or_load(id, lambda id: Image.open(f"{self.imageDir}/{id}.png"))

    def get_pil_image(self, app, id: str, handler):
        def load_pil_image(idAndHandler):
            (id, handler) = idAndHandler
            pilImage = self.get_raw_pil_image(id)
            return handler.handle_image(app, pilImage)
        return self.pilImageCache.get_or_load((id, handler), load_pil_image)

    def get_tkinter_image(self, app, id: str, handler, pilImage = None):
        def load_tkinter_image(idAndHandler):
            (id, handler) = idAndHandler
            nonlocal pilImage
            if pilImage == None:
                pilImage = self.get_pil_image(app, id, handler)
            return ImageTk.PhotoImage(pilImage)
        return self.tkImageCache.get_or_load((id, handler), load_tkinter_image)

def galaga_sizeChanged(app):
    # Purge tkinter image and pil image cache, but NOT raw pil image cache
    gallery = app.galaga.gallery
    gallery.pilImageCache.purge()
    gallery.tkImageCache.purge()

def rgb_to_hex(rgb: (int, int, int)):
    def format_hex(value: int) -> str:
        return hex(value)[2:]
    (r, g, b) = rgb
    (r, g, b) = (format_hex(r), format_hex(g), format_hex(b))
    return f"#{r}{g}{b}"

def galaga_redrawAll(app, canvas):
    galaga = app.galaga
    game = galaga.game
    canvas.create_rectangle(0, 0, app.width, app.height,
                            fill = rgb_to_hex(app.backgroundColor))
    canvas.create_text(0, 0,
                        text = f"Level: {galaga.currentLevel}  Score: {galaga.score}",
                        fill = "white", anchor = "nw")
    for drawableEntity in game.drawableEntities:
        drawableEntity.draw_on(app, canvas)
    # Make sure to draw the aliens in the correct order
    # Draw the incoming aliens before the existing ones
    for alienGroup in [game.incomingAliens, game.aliens]:
        # Draw the alive ones before the dead ones to show explosions in background
        for liveStatus in [True, False]:
            draw_aliens(app, canvas, alienGroup, liveStatus)
    titleOverlay = galaga.title_overlay()
    if titleOverlay != None:
        canvas.create_text(app.width / 2, app.height / 2, text = titleOverlay, fill = "white")

def draw_aliens(app, canvas, aliens: set, alive: bool) -> None:
    for alien in aliens:
        if alien.is_alive() == alive:
            alien.draw_on(app, canvas)

def galaga_keyPressed(app, event) -> None:
    galaga = app.galaga
    if galaga.stop_controls():
        return
    key = event.key
    if key == 'Right':
        galaga.game.move_each_starship(1)
    elif key == 'Left':
        galaga.game.move_each_starship(-1)
    elif key == 't' and galaga.game.regulator.isDebugging:
        galaga.tick(app)
    elif key == 'g':
        regulator = galaga.game.regulator
        regulator.isDebugging = not regulator.isDebugging

def galaga_mousePressed(app, event) -> None:
    galaga = app.galaga
    if galaga.stop_controls():
        return
    galaga.game.fire_starship_shot()
