import typer
from .add import app as add_app

app = typer.Typer()

app.add_typer(add_app )
