
import position
import drawing

class Starship(object):
    def __init__(self, initialPosition):
        self.position = initialPosition

    # Moves this starship by the given amount of galaga pixels
    def moveBy(self, xshift: int) -> None:
        self.position += position.Position(xshift, 0)

    def drawOn(self, app, canvas) -> None:
        gallery = app.galaga.gallery
        (x, y) = self.position.to_canvas_coords(app)
        canvas.create_image(x, y, image = gallery.get_tkinter_image(app, "starship"))

    def __repr__(self):
        return f"Starship(position={self.position})"

    def create_shot(self):
        return Shot(self.position)

class Shot(object):
    def __init__(self, initialPosition):
        self.position = initialPosition

    def drawOn(self, app, canvas) -> None:
        (x1, y1) = self.position.to_canvas_coords(app)
        (x2, y2) = (self.position + position.Position(1, 1)).to_canvas_coords(app)
        canvas.create_oval(x1, y1, x2, y2, fill = "red")
