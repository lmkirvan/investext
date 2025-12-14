import typer
from typing import List, Optional, Annotated
from rich import print
import random

data  = {
        "name" : "Rick",
        "age" : 44,
        "items" : [{"name": "Portal Gun"}, {"name": "Plumbus"}],
        "active": True,
        "affiliation": None
}

app = typer.Typer()

# you can use a function or a just a variable to provide default arguments 
def get_name() -> str :
    return random.choice(["Dave", "Lewis", "Beatrice"])

# arguments should probably get their own data container thing? 
@app.command()
def main(name: Annotated[
	 str,
	typer.Argument(
         default_factory=get_name
         , help="provide a name for a personalized greeting")
         ]):

    print(f"Hello, {name}, here's the data")
    print(data)

