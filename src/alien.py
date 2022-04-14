
class AlienSoul(object):
    def __init__(self, shape):
        self.shape = shape

class Bee(AlienSoul):
    def __init__(self):
        super().__init__(Shape("bee", (16, 16)))

    def initial_position(self):
        return Position(0, 0)

    def score_when_killed(self, currentLevel: int) -> int:
        return 10 * (currentLevel**2)

class Boss(AlienSoul):
    def __init__(self):
        super().__init__(Shape("boss", (16, 16)))

    def score_when_killed(self, currentLevel: int) -> int:
        return 100 * currentLevel

class Abductor(AlienSoul):
    def __init__(self):
        super().__init__(Shape("abductor", (16, 16)))
        self.has_starship = False

    def score_when_killed(self, currentLevel: int) -> int:
        return 20 * (currentLevel ** 3) if self.has_starship else currentLevel
