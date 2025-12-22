import typer
from os import path as os_path
from .md import app as md_app

def check_setup(ctx: typer.Context):

    if ctx.resilient_parsing:
        return
    assert os_path.isfile('.invest'), ".invest is missing are you in the project root directory"

    file = open(".invest", "r")
    lines = file.readlines()

    set = False 
    for line in lines: 
        if line.startswith('SETUP'):
            if line.strip().endswith("yes"):
                set = True

    assert set, "Looks like you haven't setup the database yet" 

app = typer.Typer(callback=check_setup)

app.add_typer(md_app)

