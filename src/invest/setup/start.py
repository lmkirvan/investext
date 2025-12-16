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
    res = {} 
    p = Path(root)
    for i in items:
        text = (p / i).read_text()
        res[i] = {"root": root, "file": i, "text": text}

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
    # we onlyl care about the roots with some kind of text files in them 
    structure = {k: v for k,v in structure.items() if len(v) != 0}  

    res = {} 
    for k,v in structure.items():
        res[k] = read_whole_folder(k, v)

    print(res)     
    dfs = []
    for v in res.values(): dfs.append(  pl.from_dicts( v  ) )

    
    data = pl.concat(dfs)
    
    with tf.NamedTemporaryFile(mode = 'w+t', delete=True, ) as fp:
        data.write_json(fp.name)
        con = ddb.connect(".data.db")
        con.sql(f"CREATE TABLE main AS SELECT * FROM read_json('{fp.name}', maximum_object_size=1073741824)")
        con.close()
        
