
import position

def galaga_keyPressed(app, event) -> None:
    game = app.galaga.game
    key = event.key
    if key == 'Right':
        game.moveEachStarship(1)
    elif key == 'Left':
        game.moveEachStarship(-1)
    elif key == 'Space':
        game.fireShot()

def galaga_timerFired(app) -> None:
    for shot in app.galaga.game.shots:
        shot.position += position.Position(0, -1)
