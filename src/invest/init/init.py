import typer
import os
from typing import Optional 
from pathlib import Path
from dotenv import load_dotenv


# I think that this is basicaly a way to manage a .env file for a given project
# this script it is create the environment variables and then I think 
# maybe we need to add a callback to load it in various places where it makes sense to load


app  = typer.Typer()

@app.command()
def init(name: Optional[str] = None) -> None:
    if name is None:
        root = Path(os.getcwd())

    else: 
        os.mkdir(name)
        root = Path(os.getcwd()) / name

    with open(str(root / ".env")) as f:
        f.write("INIT=yes")
        f.write(f"ROOT={root}")





