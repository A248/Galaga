
def galaga_redrawAll(app, canvas):
    for starship in app.galaga.game.starships:
        starship.drawOn(app, canvas)
