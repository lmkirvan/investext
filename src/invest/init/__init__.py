import typer
from .init import app as init_app

app = typer.Typer()

app.add_typer(init_app)
