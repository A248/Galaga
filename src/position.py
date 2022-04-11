
# The original Galaga uses a 288 x 224 pixel board
# Position allows decimal values for increased precision of movement

# A position is defined in terms of Galaga coordinates
# May represent either an absolute position or a difference between positions
class Position(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    # Turns galaga coordinates into canvas coordinates
    def to_canvas_coords(app) -> (int, int):
        return (self.x * app.width / 224, self.y * app.height / 288)

    # Creates galaga coordinates from canvas coordinates
    @staticmethod
    def from_canvas_coords(app, coords: (int, int)):
        (x, y) = coords
        return Position(x * 224 / app.width, y * 288 / app.height)

    # Adds a position as a difference to this position
    def __add__(self, rhs):
        return Position(self.x + rhs.x, self.y + rhs.y)
