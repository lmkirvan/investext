import typer
from .build import app as build_app
from .md import app as md_app

app = typer.Typer()

app.add_typer(build_app)
app.add_typer(md_app)


