
def galaga_keyPressed(app, event) -> None:
    game = app.galaga.game
    key = event.key
    if key == 'Right':
        game.moveEachStarship(1)
    elif key == 'Left':
        game.moveEachStarship(-1)
