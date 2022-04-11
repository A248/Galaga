
class Game(object):
    def __init__(self, initialStarship):
        self.starships = [initialStarship]

    def moveEachStarship(self, xshift: int) -> None:
        for starship in self.starships:
            starship.moveBy(xshift)
