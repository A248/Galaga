
from board import Position
from entity import Shape
import copy, math, random

class AlienSoul(object):
    def __init__(self, shape):
        self.shape = shape

    def shape(self):
        return self.shape

    def dance_entity(self, alienEntity) -> None:
        (positionDelta, newDance) = alienEntity.dance_stage.advance(alienEntity.position)
        alienEntity.position += positionDelta
        alienEntity.dance_stage = newDance
        alienEntity.shape.set_rotation(positionDelta.to_direction())

    def score_when_killed(self, currentLevel: int) -> int:
        return 10 * (currentLevel**2)

class BeeSoul(AlienSoul):
    def __init__(self):
        super().__init__(Shape("bee", (16, 16)))

    def initialize_entity(self, alienEntity) -> None:
        alienEntity.dance_stage = BeeSpiral(
            BeeBackAndForth(5), alienEntity.position, alienEntity.positionAtRest)

    def is_entity_incoming(self, alienEntity) -> bool:
        return alienEntity.dance_stage.is_incoming()

    def shot_creation_chance(self) -> int:
        return 20

class BossSoul(AlienSoul):
    def __init__(self, game):
        super().__init__(Shape("boss", (16, 16)))
        self.game = game

    def initialize_entity(self, alienEntity) -> None:
        alienEntity.dance_stage = BossAvoidShots(self.game)

    def score_when_killed(self, currentLevel: int) -> int:
        return 100 * currentLevel

    def shot_creation_chance(self) -> int:
        return 50

class AbductorSoul(AlienSoul):
    def __init__(self):
        super().__init__(Shape("abductor", (16, 16)))
        self.has_starship = False

class DanceStage(object):
    def __init__(self, isIncoming, nextDance):
        self.isIncoming = isIncoming
        self.nextDance = nextDance

    # Returns a tuple of (positionDelta, newDance) after advancing
    def advance(self, position):
        (positionDelta, shouldCede) = self.advance_or_cede(position)
        newDance = self.nextDance if shouldCede else self
        if newDance == None:
            raise ValueError("Internal implementation failure")
        return (positionDelta, newDance)

    # Returns a tuple of (positionDelta, bool) to be implemented by sub-types
    # The bool is true if to yield the next dance stage
    def advance_or_cede(self):
        raise Error("Must be implemented by sub-types")

# Uses the formula r = theta to create a spiral
# Then dr/dtheta = 1
class BeeSpiral(DanceStage):
    def __init__(self, nextDance, startPosition, endPosition, timeToReach = 32):
        super().__init__(True, nextDance)
        # We start at 2π/3 then move to 0
        self.theta = 2 * math.pi / 3
        # The amount of moves to reach the destination
        self.timeToReach = timeToReach
        # These will be later used to convert unit circle -> galaga position
        targetXdiff = endPosition.x - startPosition.x
        targetYdiff = endPosition.y - startPosition.y
        formulaXdiff = (-1) * (2 * math.pi / 3) * math.cos(2 * math.pi / 3)
        formulaYdiff = (-1) * (2 * math.pi / 3) * math.sin(2 * math.pi / 3)
        self.xscale = targetXdiff / formulaXdiff
        self.yscale = targetYdiff / formulaYdiff

    def advance_or_cede(self, position):
        thetaInitial = self.theta
        thetaFinal = thetaInitial - 2 * math.pi / (3 * self.timeToReach)
        self.theta = thetaFinal

        # Calculate dx, dy given dr and thetas
        # Note that r = theta => dr = dtheta simplifies the mathematics here
        (x0, y0) = (thetaInitial * math.cos(thetaInitial), thetaInitial * math.sin(thetaInitial))
        (x1, y1) = (thetaFinal * math.cos(thetaFinal), thetaFinal * math.sin(thetaFinal))
        positionDelta = Position((x1 - x0) * self.xscale, (y1 - y0) * self.yscale)
        # We've reached the end of the spiral if theta <= 0
        return (positionDelta, thetaFinal <= 0)

# Very simple X steps right, X steps left dance
class BeeBackAndForth(DanceStage):
    def __init__(self, stepAmount):
        super().__init__(False, None)
        self.stage = 0
        self.stepAmount = stepAmount

    def advance_or_cede(self, position):
        xdiff = 1 if self.stage < self.stepAmount else -1
        self.stage += 1
        self.stage %= (self.stepAmount*2)
        positionDelta = Position(xdiff, 0)
        # The back-and-forth never stops
        return (positionDelta, False)

class BossAvoidShots(DanceStage):
    def __init__(self, game):
        super().__init__(False, None)
        self.game = game

    def advance_or_cede(self, bossPosition):
        shotsToTheLeft = 0
        shotsToTheRight = 0
        for shot in self.game.shots:
            if shot.position.x > bossPosition.x:
                shotsToTheRight += 1
            else:
                shotsToTheLeft += 1
        if bossPosition.x < 20 or bossPosition.x > 200:
            xdiff = 0
        else:
            xdiff = -2 if shotsToTheRight > shotsToTheLeft else 2
        positionDelta = Position(xdiff, 0)
        if (positionDelta + bossPosition).is_out_of_bounds():
            positionDelta = Position(0, 0)
        return (positionDelta, False)

# Tests the spiral
def testBeeSpiral() -> None:
    print("Testing testBeeSpiral()...")
    nextDance = BeeBackAndForth(5)
    spiral = BeeSpiral(nextDance, Position(0, 0), Position(1, 1), 4)
    (delta1, _) = spiral.advance()
    (delta2, _) = spiral.advance()
    (delta3, _) = spiral.advance()
    (delta4, _) = spiral.advance()
    resultPosition = delta1 + delta2 + delta3 + delta4
    assert resultPosition == Position(1, 1), f"Really {resultPosition}"
    print("Passed")
