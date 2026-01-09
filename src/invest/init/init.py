import typer
import os
from typing import Optional 
from pathlib import Path
from dotenv import load_dotenv

app  = typer.Typer()

@app.command()
def init(name: Optional[str] = None, force:bool = False) -> None :

    env = Path(".env")
    if env.is_file() and not force:
        typer.echo( "This folder already has an .env file, use -force if you want to proceed")
        return 

    if name is None:
        root = Path(os.getcwd())
        name = root.name

    else: 
        os.mkdir(name)
        root = Path(os.getcwd()) / name

    with open(str(root / ".env"), mode='w') as f:
        f.write(f"{name.upper()}_INIT=yes")
        f.write(f"ROOT={root}")
