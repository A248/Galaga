
import math
from board import Position, Direction, LineSegment, CollisionPath, DrawnImage
from image_cache import ImageResizer, ImageRotator, CombinedImageHandler

class Shape(object):
    def __init__(self, id: str, dimensions: (int, int)):
        self.id = id
        self.dimensions = dimensions
        self.pilImage = None
        self.backgroundColor = None
        self.rotation = Direction(math.pi / 2)

    def set_image_id(self, newId) -> None:
        self.id = newId
        self.pilImage = None

    def set_rotation(self, newRotation) -> None:
        self.rotation = newRotation
        self.pilImage = None

    def get_tkinter_image(self, app):
        imageHandler = CombinedImageHandler(ImageRotator(self.rotation), ImageResizer(self.dimensions))
        pilImage = app.galaga.gallery.get_pil_image(app, self.id, imageHandler)
        tkinterImage = app.galaga.gallery.get_tkinter_image(app, self.id, imageHandler, pilImage)
        self.pilImage = pilImage
        self.backgroundColor = app.backgroundColor
        return tkinterImage

    def rectangular_dimensions(self):
        return self.dimensions

    def obtain_image_and_background(self):
        pilImage = self.pilImage
        if pilImage == None:
            return (None, None)
        return (pilImage, self.backgroundColor)

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
            imageName = "row-" + str(1 + newAnimationStage // 5) + "-column-" + str(1 + newAnimationStage % 5)
            shape.set_image_id("death-animations/" + imageName)

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
        shapeBottomLeft = atPosition - Position(boxWidth / 2, boxHeight / 2)
        shapeTopRight = shapeBottomLeft + Position(boxWidth, boxHeight)
        return (shapeBottomLeft, shapeTopRight)

    def collides_with(self, collisionPath) -> bool:
        (pilImage, backgroundColor) = self.shape.obtain_image_and_background()
        if pilImage == None:
            # We haven't drawn yet. This can happen in two scenarios:
            # 1. The game has just begun
            # 2. We are in an image transition
            # In either case, the shape hasn't rendered yet
            return False
        boundingBox = self.rectangular_bounding_box()
        image = DrawnImage(pilImage, boundingBox, backgroundColor)
        return collisionPath.intersects_with_image(image)

    def could_be_located_at(self, newPosition) -> None:
        (shapeBottomLeft, shapeTopRight) = self.rectangular_bounding_box(newPosition)
        return not (shapeBottomLeft.is_out_of_bounds() or shapeTopRight.is_out_of_bounds())

    def destroy(self) -> None:
        self.lifeStatus.alive = False
        # From https://www.hiclipart.com/free-transparent-background-png-clipart-beklu
        self.shape.set_image_id("death-animations/row-1-column-1")

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
        return Shot(self.position, (0, 1), lambda eType: eType == Alien)

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
        return Shot(self.position, (0, -1), lambda eType: eType == Starship)

    def score_when_killed(self, currentLevel: int) -> int:
        return self.alienSoul.score_when_killed(currentLevel)

    def shot_creation_chance(self) -> int:
        return self.alienSoul.shot_creation_chance()

class Shot(object):
    def __init__(self, initialPosition, direction, affectsWhichEntities):
        self.position = initialPosition
        self.direction = direction
        self.affectsWhichEntities = affectsWhichEntities

    def affects_entity_type(self, entityType) -> bool:
        return self.affectsWhichEntities(entityType)

    def move(self, byPixels: int):
        oldPosition = self.position
        newPosition = oldPosition + Position(*self.direction) * byPixels
        self.position = newPosition
        return CollisionPath(oldPosition, newPosition)

    def draw_on(self, app, canvas) -> None:
        (x1, y1) = self.position.to_canvas_coords(app)
        (x2, y2) = (self.position + Position(1, 1)).to_canvas_coords(app)
        (directionX, directionY) = self.direction
        color = "red" if directionY <= 0 else "blue"
        canvas.create_rectangle(x1, y1, x2, y2, fill = color, outline = color)

    def tick(self) -> None:
        pass
