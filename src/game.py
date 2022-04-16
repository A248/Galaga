
from entity import *
import copy

class Game(object):
    def __init__(self, initialStarship):
        self.drawableEntities = set()
        self.starships = []
        self.aliens = set()
        self.incomingAliens = set()
        self.shots = set()
        self.add_starship(initialStarship)
        self.moveShotsByPixels = 8

    def add_starship(self, starship) -> None:
        self.starships.append(starship)
        self.drawableEntities.add(starship)

    def remove_starship(self, starship) -> None:
        self.starships.remove(starship)
        self.drawableEntities.remove(starship)

    def add_alien(self, alien) -> None:
        self.aliens.add(alien)
        self.drawableEntities.add(alien)

    def remove_alien(self, alien) -> None:
        self.aliens.remove(alien)
        self.drawableEntities.remove(alien)

    def fire_starship_shot(self) -> None:
        for starship in self.starships:
            shot = starship.create_shot()
            self.shots.add(shot)
            self.drawableEntities.add(shot)

    def remove_shot(self, shot) -> None:
        self.shots.remove(shot)
        self.drawableEntities.remove(shot)

    def move_each_starship(self, xshift: int) -> None:
        starships = self.starships
        if starships == []:
            return
        for starship in starships:
            if not starship.can_move_by(xshift):
                return
        for starship in starships:
            starship.move_by(xshift)

    def cleanup_entities(self) -> None:
        def cleanup_certain_entities(entities) -> None:
            # entities may be a set or a list
            for entity in copy.copy(entities):
                if entity.is_finished():
                    entities.remove(entity)
        cleanup_certain_entities(self.starships)
        cleanup_certain_entities(self.aliens)
        cleanup_certain_entities(self.incomingAliens)

    def dance_aliens(self):
        for incomingAlien in copy.copy(self.incomingAliens):
            if incomingAlien.is_alive():
                incomingAlien.dance_along()
                if not incomingAlien.is_incoming():
                    self.incomingAliens.remove(incomingAlien)
                    self.aliens.add(incomingAlien)
        for alien in copy.copy(self.aliens):
            if alien.is_alive():
                alien.dance_along()

    def move_shots(self, collidables, collidable_type, collision_handler) -> None:
        for shot in copy.copy(self.shots):
            if not shot.affects_entity_type(collidable_type):
                continue
            shot.move()
            if shot.position.is_out_of_bounds():
                self.shots.remove(shot)
                continue
            for collidable in collidables:
                if collidable.is_alive() and collidable.collides_with(shot):
                    collidable.destroy()
                    collision_handler(shot, collidable)
                    self.remove_shot(shot)

    def move_all_shots(self, app):
        galaga = app.galaga
        def handle_starship_shot_collision(starshipShot, alien) -> None:
            galaga.score += alien.score_when_killed(galaga.currentLevel)

        def handle_alien_shot_collision(alienShot, starship) -> None:
            if len(self.starships) == 1:
                galaga.game_over = True

        self.move_shots(self.aliens, Alien, handle_starship_shot_collision)
        self.move_shots(self.starships, Starship, handle_alien_shot_collision)
