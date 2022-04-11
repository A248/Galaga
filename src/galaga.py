
from controls import *
from drawing import *
from game import *
from position import *
from starship import *
from cmu_112_graphics import *

class Galaga(object):
    def __init__(self, game, gallery):
        self.game = game
        self.gallery = gallery
        self.currentLevel = 0

def main():
    starship = Starship(Position(112, 270))
    galaga = Galaga(Game(starship), Gallery("images"))
    app = runApp(fnPrefix = 'galaga_', autorun = False)
    app.galaga = galaga
    app.run()

main()
