import typer
from .start  import app as setup_app 
from .md import app as md_app

app = typer.Typer()

app.add_typer(setup_app)
app.add_typer(md_app,   name='markdown')
