
from entity import *
from game import *
from gui import *
from cmu_112_graphics import *

class Galaga(object):
    def __init__(self, game, gallery):
        self.game = game
        self.gallery = gallery
        self.currentLevel = 0
        self.timeSinceLevelStart = 0

    def tick(self, app) -> None:
        self.timeSinceLevelStart += 1
        self.game.tick(app)
        self.spawn_new_aliens()

    def spawn_new_aliens(self):
        if self.timeSinceLevelStart == 1:
            self.game.add_alien(Alien(Position(4, 4), 5))

def main():
    starship = Starship(Position(112, 270))
    galaga = Galaga(Game(starship), Gallery("images"))
    app = runApp(fnPrefix = 'galaga_', autorun = False)
    app.timerDelay = 50 # 20 ticks per second
    app.galaga = galaga
    app.run()

def galaga_timerFired(app) -> None:
    app.galaga.tick(app)

main()
