import typer

from .augment import app as augment_app

app = typer.Typer()
app.add_typer(augment_app)
