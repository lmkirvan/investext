import typer
from .tag import app as tag_app

app = typer.Typer()

app.add_typer(tag_app)
