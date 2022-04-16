
from alien import *
from board import *
from entity import *
from game import *
from gui import *
from cmu_112_graphics import *

class Galaga(object):
    def __init__(self, game, gallery):
        self.game = game
        self.gallery = gallery
        self.currentLevel = 0
        self.score = 0
        self.timeSinceLevelStart = 0
        # Gameplay parameters
        self.moveShotsEveryThisTicks = 1
        self.danceEveryThisTicks = 10

    def tick(self, app) -> None:
        self.timeSinceLevelStart += 1
        self.move_shots(app)
        self.harangue_aliens_to_action()
        if self.timeSinceLevelStart % 40 == 0:
            self.game.cleanup_entities()

    def move_shots(self, app) -> None:
        if self.timeSinceLevelStart % self.moveShotsEveryThisTicks == 0:
            self.game.move_all_shots(app)

    def harangue_aliens_to_action(self) -> None:
        if self.timeSinceLevelStart % self.danceEveryThisTicks == 0:
            self.game.dance_aliens()
        if self.timeSinceLevelStart == 1:
            self.game.add_alien(Alien(Position(0, 0), Position(32, 32), BeeSoul()))

def main():
    starship = Starship(Position(112, 270))
    galaga = Galaga(Game(starship), Gallery("images"))
    app = runApp(fnPrefix = 'galaga_', autorun = False)
    app.timerDelay = 50 # 20 ticks per second
    app.galaga = galaga
    app.run()

def galaga_timerFired(app) -> None:
    app.galaga.tick(app)

def testAll() -> None:
    testPosition()
    testBeeSpiral()
    print("All tests passed")

#testAll()

main()
