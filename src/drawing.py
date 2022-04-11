

from PIL import Image, ImageTk

class Gallery(object):

    image_data = {
        # From https://www.pngjoy.com/preview/p6k6i7z7t7l9c2_space-ship-galaga-ship-no-background-png-download/
        # Originally starship.webp
        "starship":16
    }

    def __init__(self, dir):
        self.images = Gallery.load_images(dir)

    @staticmethod
    def load_images(dir: str) -> dict:
        images = dict()
        for imageId in Gallery.image_data:
            # Image.open taken from cmu_112_graphics
            pilImage = Image.open(f"{dir}/{imageId}.png")
            images[imageId] = pilImage
        return images

    def get_tkinter_image(self, app, id: str):
        imageHeightInPixels = Gallery.image_data[id]
        pilImage = self.images[id]
        (originalWidth, originalHeight) = pilImage.size
        (pixelWidth, pixelHeight) = board_pixel_size(app)
        # Scale width and height
        newHeight = pixelHeight * imageHeightInPixels
        newWidth = originalWidth * (newHeight / originalHeight)
        # Use of resize() taken from cmu_112_graphics
        pilImage = pilImage.resize((round(newWidth), round(newHeight)), resample=Image.ANTIALIAS)
        return ImageTk.PhotoImage(pilImage)


# View: Galaga uses a 288 x 224 pixel board
# Returns (width, height) of pixel size
def board_pixel_size(app) -> (int, int):
    return (app.width / 224, app.height / 288)


def galaga_redrawAll(app, canvas):
    for starship in app.galaga.game.starships:
        starship.drawOn(app, canvas)
    for shot in app.galaga.game.shots:
        shot.drawOn(app, canvas)
