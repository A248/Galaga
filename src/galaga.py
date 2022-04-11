
from controls import *
from game import *
from position import *
from starship import *

class Galaga(object):
    def __init__(self, game):
        self.game = Game()
        self.currentLevel = 0

def main():
    galaga = Galaga()
    starship = Starship(Position(112, 270))
    app = runApp(fnPrefix = 'galaga_', autorun = False)
    app.galaga = galaga
    app.run()

main()
