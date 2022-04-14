
# View: Galaga uses a 288 x 224 pixel board
MAX_PIXEL_X = 224
MAX_PIXEL_Y = 288

# A position is defined in terms of Galaga coordinates
# May represent either an absolute position or a difference between positions
class Position(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    # Turns galaga coordinates into canvas coordinates
    def to_canvas_coords(self, app) -> (int, int):
        (pixel_width, pixel_height) = board_pixel_size(app)
        return (self.x * pixel_width, self.y * pixel_height)

    # Creates galaga coordinates from canvas coordinates
    @staticmethod
    def from_canvas_coords(app, coords: (int, int)):
        (pixel_width, pixel_height) = board_pixel_size(app)
        (x, y) = coords
        return Position(x / pixel_width, y / pixel_height)

    # Adds a position as a difference to this position
    def __add__(self, rhs):
        return Position(self.x + rhs.x, self.y + rhs.y)

    def is_out_of_bounds(self) -> bool:
        return (self.x < 0 or self.y < 0 or
                self.x > MAX_PIXEL_X or self.y > MAX_PIXEL_Y)

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

# Returns (width, height) of pixel size
def board_pixel_size(app) -> (int, int):
    return (app.width / MAX_PIXEL_X, app.height / MAX_PIXEL_Y)
