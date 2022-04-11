
class Game(object):
    def __init__(self, initialStarship):
        self.starships = [initialStarship]
        self.shots = []

    def moveEachStarship(self, xshift: int) -> None:
        for starship in self.starships:
            starship.moveBy(xshift)

    def fireShot(self) -> None:
        for starship in self.starships:
            self.shots.append(starship.create_shot())
