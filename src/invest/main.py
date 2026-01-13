import typer

from .add import app as add_app
from .output import app as output_app
from .init import app as init_app
from .augment import app as augment_app

app = typer.Typer()

app.add_typer(init_app)
app.add_typer(add_app)
app.add_typer(augment_app)
app.add_typer(output_app, name="output")


