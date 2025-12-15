import typer
from typing import List, Annotated, Any
from rich import print
from pathlib import Path
import json 


app  = typer.Typer()

def bin_mask(l: List[Any], p: list[bool]):
    assert len(l) == len(p)
    return [item for item, keep in zip(l, p) if keep] 


def read_whole_folder(root: str, items: List[str]):
    res = {} 
    p = Path(root)
    for i in items:
        text = (p / i).read_text()
        res[i] = text

    return res
    

@app.command(name = 'setup')
def setup(
    path: Annotated[
        Path, 
        typer.Option(
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
        ), 
    ],
    extension: str = "txt",
    verbose: bool = False
):

    if verbose:
        v = print
    else:
        v = None
 
    structure = {}
    for root, _, file in path.walk(on_error=v):

        flgl = [True if f.endswith(extension) else False for f in file]
        structure[str(root)] = bin_mask(file, flgl)
    # we onlyl care about the roots with some kind of text files in them 
    structure = {k: v for k,v in structure.items() if len(v) != 0}  

    res = {}

    for k,v in structure.items():
        res[k] = read_whole_folder(k, v)


    with open("data.json", "w") as f:
        json.dump(res, f)
 
@app.callback()
def create():
    pass
