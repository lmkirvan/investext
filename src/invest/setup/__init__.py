import typer
from .build import app as build_app

app = typer.Typer()

app.add_typer(build_app)


