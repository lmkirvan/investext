import tomllib
import typer
from typing import Annotated, Optional
from pathlib import Path
from enum import Enum


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
        ),
    ]
):
    print(config)
    if config is None:
        print("No config provided") 
        raise typer.Abort()
    if config.is_file() and config.suffix == ".toml":
        print('reading file')
        with config.open( "rb") as f:
            con_par = tomllib.load(f)
    else: 
        print("Couldn't find the file. Where's the toml at?")
        raise typer.Abort()

    Starts = Enum("starts_with", con_par["starts_with"])

