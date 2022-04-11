
def galaga_keyPressed(app) -> None:
    game = app.galaga.game
    if key == 'Right':
        game.moveEachStarship(1)
    elif key == 'Left':
        game.moveEachStarship(-1)
