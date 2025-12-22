import typer

from .setup import app as setup_app
from .output import app as output_app

app = typer.Typer()

app.add_typer(setup_app)
app.add_typer(output_app, name="output")
