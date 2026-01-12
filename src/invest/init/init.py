import typer
from typing import Optional 
from pathlib import Path

app  = typer.Typer()

@app.command()
def init(name: Optional[str] = None, force:bool = False) -> None :

    env = Path(".env").absolute()
    if env.is_file() and not force:
        typer.echo( "This folder already has an .env file, use -force if you want to proceed")
        return
    if name is None:
        root = env.parent
    else: 
        root = env.parent / name
    with open(str(root / ".env"), mode='w') as f:
        f.write(f"INVEST_INIT=yes\n")
        f.write(f"INVEST_ROOT={root}\n")
