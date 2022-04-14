
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
        if xshift > 0 and not starships[-1].can_move_by(xshift):
            # Prevent moving off the right edge
            return
        if xshift < 0 and not starships[0].can_move_by(xshift):
            # Prevent moving off the left edge
            return
        for starship in starships:
            starship.move_by(xshift)

    def tick(self, app):
        self.cleanup_entities()
        self.dance_aliens()
        self.move_all_shots(app)

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
        for incomingAlien in self.incomingAliens:
            if incomingAlien.is_alive():
                incomingAlien.dance_along()

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
