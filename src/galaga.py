
from alien import *
from board import *
from entity import *
from game import *
from gui import *
from cmu_112_graphics import *

class Galaga(object):
    def __init__(self, game, gallery, waitingAliens):
        self.game = game
        self.gallery = gallery
        self.currentLevel = 0
        self.score = 0
        self.waitingAliens = waitingAliens
        self.state = 0 # 0 - playing, 1 - game over, 2 - victory

    def tick(self, app) -> None:
        game = self.game
        game.regulator.tick()
        game.tick(app)
        if game.regulator.should_cleanup_entities():
            game.cleanup_entities()
        self.harangue_aliens_to_action()

    def harangue_aliens_to_action(self) -> None:
        game = self.game
        if game.regulator.should_dance_aliens():
            self.game.dance_aliens()
        if game.regulator.should_spawn_aliens() and len(game.aliens) == 0:
            waitingAliens = self.waitingAliens
            if len(waitingAliens) == 0:
                self.state = 2
                return
            nextUp = waitingAliens.pop()
            for alien in nextUp(self):
                self.game.add_alien(alien)
            self.currentLevel += 1

    def game_over(self) -> None:
        self.state = 1

    def stop_controls(self) -> bool:
        return self.title_overlay() != None

    # If won or game over, returns a title, otherwise None
    def title_overlay(self) -> str:
        if self.state == 1:
            return "Game Over"
        if self.state == 2:
            return "Victory"
        return None

def main():
    def gen_bee(endPosition):
        return Alien(Position.board_top_left(), endPosition, BeeSoul())
    def gen_boss(endPosition, galaga):
        return Alien(endPosition, endPosition, BossSoul(galaga.game))
    waitingAliens = [
        lambda galaga: [ gen_bee(Position(x, 220)) for x in range(32, 200, 32) ] + [ gen_boss(Position(112, 250), galaga) ],
        lambda galaga: [ gen_bee(Position(x, 220)) for x in range(32, 200, 64) ],
        lambda galaga: [ gen_bee(Position(32, 220)) ],
        lambda galaga: [ gen_boss(Position(112, 250), galaga) ]
    ]
    starship = Starship(Position(112, 15))
    galaga = Galaga(Game(GameplayRegulator(), starship), Gallery("images"), waitingAliens)
    app = runApp(fnPrefix = 'galaga_', autorun = False)
    app.timerDelay = 50 # 20 ticks per second
    app.backgroundColor = (0, 0, 0)
    app.galaga = galaga
    app.run()

def galaga_timerFired(app) -> None:
    app.galaga.tick(app)

def testAll() -> None:
    testPosition()
    testLineSegment()
    testBeeSpiral()
    print("All tests passed")

#testAll()

main()
