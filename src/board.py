
import math, copy

# View: Galaga uses a 288 x 224 pixel board
MAX_PIXEL_X = 224
MAX_PIXEL_Y = 288

# A position is defined in terms of Galaga coordinates - which are Cartesian
# May represent either an absolute position or a difference between positions
class Position(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    # Turns galaga coordinates into canvas coordinates
    def to_canvas_coords(self, app) -> (int, int):
        # Galaga uses cartesian coordinates, but on the canvas "up is down"
        (x, y) = (self.x, MAX_PIXEL_Y - self.y)
        (pixel_width, pixel_height) = board_pixel_size(app)
        return (x * pixel_width, y * pixel_height)

    # Creates galaga coordinates from canvas coordinates
    @staticmethod
    def from_canvas_coords(app, coords: (int, int)):
        (pixelWidth, pixelHeight) = board_pixel_size(app)
        (canvasX, canvasY) = coords
        (x, y) = (canvasX / pixelWidth, canvasY / pixelHeight)
        y = MAX_PIXEL_Y - y
        return Position(x, y)

    # Adds a position as a difference to this position
    def __add__(self, rhs):
        return Position(self.x + rhs.x, self.y + rhs.y)

    # Subtracts as position from this one, yielding a difference
    def __sub__(self, rhs):
        return Position(self.x - rhs.x, self.y - rhs.y)

    # Multiplies this position by an integer
    def __mul__(self, rhs):
        return Position(self.x * rhs, self.y * rhs)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Position):
            return False
        EPSILON = 10**-8
        return abs(self.x - other.x) < EPSILON and abs(self.y - other.y) < EPSILON

    def __hash__(self):
        return hash((round(self.y), round(self.y)))

    def is_out_of_bounds(self) -> bool:
        return (self.x < 0 or self.y < 0 or
                self.x > MAX_PIXEL_X or self.y > MAX_PIXEL_Y)

    def to_direction_radians(self) -> float:
        (x, y) = (self.x, self.y)
        if x == 0:
            return math.pi / 2 if y > 0 else 3 * math.pi / 2
        arctan = math.atan(y / x)
        return arctan if x > 0 else math.pi + arctan

    def to_direction(self):
        return Direction(self.to_direction_radians())

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    @staticmethod
    def board_top_left():
        return Position(0, MAX_PIXEL_Y)

# Returns (width, height) of pixel size
def board_pixel_size(app) -> (int, int):
    return (app.width / MAX_PIXEL_X, app.height / MAX_PIXEL_Y)

# A radian direction which handles float precision checks
class Direction(object):
    def __init__(self, radians: float):
        self.radians = radians

    def __eq__(self, other) -> bool:
        if not isinstance(other, Direction):
            return False
        EPSILON = 10**-5
        return abs(self.radians - other.radians) < EPSILON

    def __hash__(self):
        return hash(self.radians)

    def __repr__(self) -> str:
        fractionOfPi = self.radians / math.pi
        return f"{fractionOfPi}π"

def maxmin(*values):
    return (max(*values), min(*values))

class LineSegment(object):
    def __init__(self, position1, position2):
        self.position1 = position1
        self.position2 = position2

    def max_min_bounds(self) -> tuple:
        return (maxmin(self.position1.x, self.position2.x),
                maxmin(self.position1.y, self.position2.y))

    def slope_and_intercept(self):
        (position1, position2) = (self.position1, self.position2)
        if position1.x == position2.x:
            return (None, position1.x)
        slope = (position1.y - position2.y) / (position1.x - position2.x)
        intercept = position1.y - slope * position1.x # y - mx
        return (slope, intercept)

    # Similar to fit_within except used for testing purposes
    # Is non-destructive and takes different parameters
    def test_fit_within(self, scanBounds):
        (((scanMinX, scanMinY), (scanMaxX, scanMaxY))) = scanBounds
        selfCopy = copy.deepcopy(self)
        selfCopy.fit_within(((scanMaxX, scanMinX), (scanMaxY, scanMinY)), True)
        return selfCopy

    # Destructive method which fits this segment within the given image
    # Returns False if this segment cannot fit
    def fit_within(self, image) -> bool:
        ((maxX, minX), (maxY, minY)) = self.max_min_bounds()
        (imageBoxBottomLeft, imageBoxTopRight) = image.boundingBox
        if maxX < imageBoxBottomLeft.x or minX > imageBoxTopRight.x:
            return False
        if maxY < imageBoxBottomLeft.y or minY > imageBoxTopRight.y:
            return False
        upperBoundX = min(maxX, imageBoxTopRight.x)
        lowerBoundX = max(minX, imageBoxBottomLeft.x)
        upperBoundY = min(maxY, imageBoxTopRight.y)
        lowerBoundY = max(minY, imageBoxBottomLeft.y)
        (slope, intercept) = self.slope_and_intercept()
        if slope == None:
            xline = intercept
            self.position1 = Position(xline, upperBoundY)
            self.position2 = Position(xline, lowerBoundY)
            return True
        (position1, position2) = (self.position1, self.position2)
        rightMostPosition = position1 if position1.x >= position2.x else position2
        leftMostPosition = position2 if rightMostPosition == position1 else position1
        if image.assertions:
            assert len({rightMostPosition, leftMostPosition}) == 2
        yAtRightMostX = slope * upperBoundX + intercept
        yAtLeftMostX = slope * lowerBoundX + intercept
        if yAtRightMostX <= upperBoundY and yAtRightMostX >= lowerBoundY:
            # Bounded by x on the right
            rightMostPosition.x = upperBoundX
            rightMostPosition.y = yAtRightMostX
        else:
            # Bounded by y on the right
            # Determine whether this is an upper or lower bound
            whichBoundY = upperBoundY if slope > 0 else lowerBoundY
            rightMostPosition.y = whichBoundY
            rightMostPosition.x = (whichBoundY - intercept) / slope
        if yAtLeftMostX <= upperBoundY and yAtLeftMostX >= lowerBoundY:
            # Bounded by x on the left
            leftMostPosition.x = lowerBoundX
            leftMostPosition.y = yAtLeftMostX
        else:
            # Bounded by y on the left
            # Determine whether this is an upper or lower bound
            whichBoundY = upperBoundY if slope < 0 else lowerBoundY
            leftMostPosition.y = whichBoundY
            leftMostPosition.x = (whichBoundY - intercept) / slope
        # All done: self.position1 and self.position2 were mutated
        return True

    def __eq__(self, other) -> bool:
        if not isinstance(other, LineSegment):
            return False
        return {self.position1, self.position2} == {other.position1, other.position2}

    def __repr__(self) -> str:
        return f"From {self.position1} to {self.position2}"

class CollisionPath(object):
    def __init__(self, position1, position2):
        self.segment = LineSegment(position1, position2)

    def intersects_with_image(self, image) -> bool:
        image.assertions = self.isDebugging
        # Squeeze the segment to be bounded by the image box
        segment = copy.deepcopy(self.segment)
        if not segment.fit_within(image):
            return False
        # segment is now be bounded by the image box
        ((scanMaxX, scanMinX), (scanMaxY, scanMinY)) = segment.max_min_bounds()
        (slope, intercept) = segment.slope_and_intercept()
        if slope == None:
            scanX = intercept
            for scanY in range(math.ceil(scanMinY), math.floor(scanMaxY)):
                if image.position_is_part_of_image(scanX, scanY):
                    return True
        else:
            for scanX in range(math.ceil(scanMinX), math.floor(scanMaxX)):
                scanY = slope * scanX + intercept
                if image.assertions:
                    assert scanY <= scanMaxY and scanY >= scanMinY
                if image.position_is_part_of_image(scanX, scanY):
                    return True
        return False

class DrawnImage(object):
    def __init__(self, pilImage, boundingBox, backgroundColor, assertions = True):
        self.pilImage = pilImage
        self.boundingBox = boundingBox
        self.backgroundColor = backgroundColor
        self.assertions = True

    def position_is_part_of_image(self, positionX: int, positionY: int) -> bool:
        image = self.pilImage
        (boxBottomLeft, boxTopRight) = self.boundingBox
        (width, height) = (boxTopRight.x - boxBottomLeft.x, boxTopRight.y - boxBottomLeft.y)
        (imageWidth, imageHeight) = (image.width -1, image.height - 1)
        (relativeX, relativeY) = (positionX - boxBottomLeft.x, positionY - boxBottomLeft.y)
        assert relativeX <= width and relativeX >= 0
        assert relativeY <= height and relativeY >= 0
        pixelX = (relativeX / width) * imageWidth
        pixelY = (relativeY / height) * imageHeight
        # Up is down
        pixelY = imageHeight - pixelY
        return image.getpixel((pixelX, pixelY)) != self.backgroundColor

# Tests the Position class
def testPosition() -> None:
    print("Testing testPosition()...")
    position1 = Position(1, 1)
    almostOne = 0.9999999999
    assert position1 == Position(almostOne, almostOne), f"Equality precision"
    assert position1.to_direction_radians() == math.pi / 4
    assert Position(-1, -1).to_direction_radians() == 5 * math.pi / 4
    print("Passed")

def assertEquals(expected, actual) -> None:
    assert expected == actual, f"Expected {expected} but was {actual}"

# Tests the LineSegment class
def testLineSegment() -> None:
    print("Testing testLineSegment()...")
    segment = LineSegment(Position(0, 0), Position(3, 6))
    assert segment.max_min_bounds() == ((3, 0), (6, 0))
    # Already within the bound
    #assertEquals(segment, segment.test_fit_within(((-1, -1), (4, 7))))
    # X-bound to X-bound
    #assertEquals(LineSegment(Position(1, 2), Position(2, 4)), segment.test_fit_within(((1, -5), (2, 10))))
    # Y-bound to Y-bound
    #assert segment.test_fit_within(((-5, 1), (10, 2))) == LineSegment(Position(0.5, 1), Position(1, 2))
    # X-bound to Y-bound
    #assert segment.test_fit_within(((1, -5), (10, 3))) == LineSegment(Position(1, 2), Position(1.5, 3))
    print("Passed")
