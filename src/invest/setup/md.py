import tomllib
from typing import Annotated, Optional
from pathlib import Path
import typer
import os

def check_setup():
    assert os.path.isfile('.invest'), ".invest is missing are you in the project root directory"

    file = open(".invest", "r")
    lines = file.readlines()

    set = False 
    for line in lines: 
        if line.startswith('SETUP'):
            if line.strip().endswith("yes"):
                set = True

    assert set, "Looks like you haven't setup the database yet" 


app = typer.Typer()

@app.command()
def markdown(
    config: Annotated[
        Optional[Path],
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            callback=check_setup, 
        ),
    ],
    verbose: bool =  False,
    ):

    if config is None:
        print("No config provided") 
        raise typer.Abort()
    if config.is_file() and config.suffix == "toml":
        with config.open( "rb") as f:
            con_par = tomllib.load(f)
    else: 
        print("Couldn't find the file. Where's the toml at?")



