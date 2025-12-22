import typer

from .setup import app as setup_app

app = typer.Typer()
app.add_typer(setup_app, name="setup")

