import typer
from typing import List, Annotated, Any
from rich import print
from pathlib import Path
import json 
import duckdb as ddb 
import tempfile as tf 
import polars as pl 


app  = typer.Typer()

def bin_mask(l: List[Any], p: list[bool]):
    assert len(l) == len(p)
    return [item for item, keep in zip(l, p) if keep] 


def read_whole_folder(root: str, items: List[str]):
    text = []
    p = Path(root)
    for i in items:
        text.append((p / i).read_text())
    return {"root": root, 'files': items, "text": text}

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
    verbose: bool = False,
    force: bool = False
):

    if not force:
        db = Path(".data.db")
        assert not db.is_file()
    else:
        db = Path(".data.db")
        if db.exists():
            db.unlink()

    if verbose:
        v = print
    else:
        v = None
 
    structure = {}
    for root, _, file in path.walk(on_error=v):
        flgl = [True if f.endswith(extension) else False for f in file]
        structure[str(root)] = bin_mask(file, flgl)
   
    structure = {k: v for k,v in structure.items() if len(v) != 0}  

    res = {} 
    for k,v in structure.items():
        res[k] = read_whole_folder(k, v)
    
    dfs = []
    for v in res.values(): dfs.append(pl.from_dicts(v))
    
    data = pl.concat(dfs)
    data = data.with_row_index(name = "id") 
    con = ddb.connect(".data.db")
    con.sql("CREATE TABLE main AS SELECT * FROM data")
    con.close() 
