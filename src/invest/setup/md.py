import tomllib
from typing import Annotated
from pathlib import Path
import typer
import os

# I think this is kidn of stupid, but maybe I'll just let it ride for now. 
# the basic idea is make sure that commands run from the root directoy
# this will be handled differently in an actual application I suppose 
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


app = typer.Typer(callback=check_setup)

@app.command()
def markdown(
    config: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            callback=check_setup, 
        ),
    ],
    verbose: bool =  False,
    force: bool = False ):

    config = Path(config) 
    assert config.exists(), "did you mistype the config?"

    with config.open( "rb") as f:
        con_par = tomllib.load(f)

    if verbose:
        print(con_par) 




