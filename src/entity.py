
from board import Position

class Shape(object):
    def __init__(self, id: str, dimensions: (int, int)):
        self.id = id
        self.dimensions = dimensions
        self.pilImage = None
        self.background_color = (0, 0, 0)

    def set_image_id(self, newId) -> None:
        self.id = newId
        self.pilImage = None

    def get_tkinter_image(self, app):
        pilImage = app.galaga.gallery.get_pil_image(app, self.id, self.dimensions)
        tkinterImage = app.galaga.gallery.get_tkinter_image(app, self.id, self.dimensions, pilImage)
        self.pilImage = pilImage
        return tkinterImage

    def rectangular_dimensions(self):
        return self.dimensions

    def has_point(self, relativePosition: (int, int)) -> bool:
        image = self.pilImage
        if image == None:
            # We haven't drawn yet. This can happen in two scenarios:
            # 1. The game has just begun
            # 2. We are in an image transition
            # In either case, the shape hasn't rendered yet
            return False
        (relativePositionX, relativePositionY) = relativePosition
        # Convert our relative pixel-scale position to image scale
        (dimensionsWidth, dimensionsHeight) = self.dimensions
        boardPixelWidth = image.width / dimensionsWidth
        boardPixelHeight = image.height / dimensionsHeight
        # Calculate the edges of the square inside the image we need to check
        minX = relativePositionX * boardPixelWidth
        maxX = minX + boardPixelWidth - 1
        minY = relativePositionY * boardPixelHeight
        maxY = minY + boardPixelHeight - 1
        # First check the 4 corners: fast-path
        background_color = self.background_color
        for checkCornerX in [minX, maxX]:
            for checkCornerY in [minY, maxY]:
                if image.getpixel((checkCornerX, checkCornerY)) != background_color:
                    return True
        # We only need to check the square's outline, not the entire square
        # This saves a significant amount of pixel checks
        for checkColumn in [minX, maxX]:
            for checkY in range(minY + 1, maxY):
                if image.getpixel((checkColumn, checkY)) != background_color:
                    return True
        for checkRow in [minY, maxY]:
            for checkX in range(minX + 1, maxX):
                if image.getpixel((checkX, checkRow)) != background_color:
                    return True
        return False

class LifeStatus(object):
    MAX_DEATH_ANIMATION = 20

    def __init__(self, deathAnimationSpeed):
        self.alive = True
        self.deathAnimationSpeed = deathAnimationSpeed
        self.deathAnimationTick = 0

    def tick_and_adjust_shape(self, shape):
        if self.alive:
            return
        formerAnimationStage = self.deathAnimationTick // self.deathAnimationSpeed
        self.deathAnimationTick += 1
        newAnimationStage = self.deathAnimationTick // self.deathAnimationSpeed
        if (formerAnimationStage != newAnimationStage and
            newAnimationStage < LifeStatus.MAX_DEATH_ANIMATION):
            shape.set_image_id("death-animations/" + str(1 + newAnimationStage))

    def is_finished(self):
        animationStage = self.deathAnimationTick // self.deathAnimationSpeed
        return animationStage >= LifeStatus.MAX_DEATH_ANIMATION

class Entity(object):
    def __init__(self, initialPosition, shape, lifeStatus):
        self.position = initialPosition
        self.shape = shape
        self.lifeStatus = lifeStatus

    def is_alive(self) -> bool:
        return self.lifeStatus.alive

    def draw_on(self, app, canvas) -> None:
        (x, y) = self.position.to_canvas_coords(app)
        canvas.create_image(x, y, image = self.shape.get_tkinter_image(app))

    def rectangular_bounding_box(self, atPosition = None):
        if atPosition == None:
            atPosition = self.position
        (boxWidth, boxHeight) = self.shape.rectangular_dimensions()
        shapeTopLeft = atPosition - Position(boxWidth / 2, boxHeight / 2)
        shapeBottomRight = shapeTopLeft + Position(boxWidth, boxHeight)
        return (shapeTopLeft, shapeBottomRight)

    def collides_with(self, movableShot) -> bool:
        shotPosition = movableShot.position
        (shapeTopLeft, shapeBottomRight) = self.rectangular_bounding_box()
        if shotPosition.x < shapeTopLeft.x or shotPosition.y < shapeTopLeft.y:
            return False
        if shotPosition.x > shapeBottomRight.x or shotPosition.y > shapeBottomRight.y:
            return False
        relativePosition = (shotPosition.x - shapeTopLeft.x, shotPosition.y - shapeTopLeft.y)
        return self.shape.has_point(relativePosition)

    def could_be_located_at(self, newPosition) -> None:
        (shapeTopLeft, shapeBottomRight) = self.rectangular_bounding_box(newPosition)
        return not (shapeTopLeft.is_out_of_bounds() or shapeBottomRight.is_out_of_bounds())

    def destroy(self) -> None:
        self.lifeStatus.alive = False
        # From https://www.hiclipart.com/free-transparent-background-png-clipart-beklu
        self.shape.set_image_id("death-animations/0")

    def tick(self) -> None:
        self.lifeStatus.tick_and_adjust_shape(self.shape)

    def is_finished(self) -> bool:
        return self.lifeStatus.is_finished()

class Starship(Entity):

    STARSHIP_SHAPE = Shape("starship", (16, 16))

    def __init__(self, initialPosition):
        super().__init__(initialPosition, Starship.STARSHIP_SHAPE, LifeStatus(5))

    # Moves this starship by the given amount of galaga pixels
    def move_by(self, xshift: int) -> None:
        self.position += Position(xshift, 0)

    # Determines whether this starship would be able to move by the given amount
    def can_move_by(self, xshift: int) -> bool:
        return self.could_be_located_at(self.position + Position(xshift, 0))

    def __repr__(self):
        return f"Starship(position={self.position})"

    def create_shot(self):
        return Shot(self.position, (0, -1), lambda eType: eType == Alien)

class Alien(Entity):
    def __init__(self, initialPosition, positionAtRest, alienSoul):
        super().__init__(initialPosition, alienSoul.shape, LifeStatus(1))
        self.positionAtRest = positionAtRest
        self.alienSoul = alienSoul
        alienSoul.initialize_entity(self)

    def dance_along(self) -> None:
        self.alienSoul.dance_entity(self)

    def is_incoming(self) -> bool:
        return self.alienSoul.is_entity_incoming(self)

    def __repr__(self):
        return f"Alien(position={self.position})"

    def create_shot(self):
        return Shot(self.position, (0, 1), lambda eType: eType == Starship)

    def score_when_killed(self, currentLevel: int) -> int:
        return self.alienSoul.score_when_killed(currentLevel)

class Shot(object):
    def __init__(self, initialPosition, direction, affectsWhichEntities):
        self.position = initialPosition
        self.direction = direction
        self.affectsWhichEntities = affectsWhichEntities

    def affects_entity_type(self, entityType) -> bool:
        return self.affectsWhichEntities(entityType)

    def move(self) -> None:
        self.position += Position(*self.direction)

    def draw_on(self, app, canvas) -> None:
        (x1, y1) = self.position.to_canvas_coords(app)
        (x2, y2) = (self.position + Position(1, 1)).to_canvas_coords(app)
        canvas.create_rectangle(x1, y1, x2, y2, fill = "red", outline = "red")
