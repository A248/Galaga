
class Starship(object):
    def __init__(self, initialPositio):
        self.position = initialPosition

    # Moves this starship by the given amount of galaga pixels
    def moveBy(self, xshift: int) -> None:
        self.position += Position(xshift, 0)

    def drawOn(self, app, canvas) -> None:
        pass
