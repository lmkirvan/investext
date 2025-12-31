import typer
from typing import List, Annotated, Any
from rich import print
from pathlib import Path
import duckdb as ddb 
import polars as pl 
from datetime import datetime

app  = typer.Typer()

def bin_mask(l: List[Any], p: list[bool]):
    assert len(l) == len(p)
    return [item for item, keep in zip(l, p) if keep] 

def read_whole_folder(root: str, items: List[str]):
    text = []
    p = Path(root)
    for i in items:
        text.append((p / i).read_text())
    return {"root": root, 'file': items, "text": text}

@app.command()
def add(
    path: Annotated[
        Path, 
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=True,
            resolve_path=True,
        ), 
    ],
    extension: str = "txt",
    db_name: str = ".data.db", # I only really want this for testing? 
    verbose: bool = False,
    overwrite: bool = False,
):

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
    data = data.with_columns(
        pl.concat_str(['root', 'file'], separator="/").alias("name_key"),
        pl.lit(datetime.now()).alias("date_added")
    )

    db_path = Path(db_name)

    #if there is no database we have to build one from scratch here. 
    if not db_path.exists():
        con = ddb.connect(db_path)
        con.sql("CREATE TABLE docs AS SELECT * FROM data")
        con.sql("ALTER TABLE docs ADD PRIMARY KEY (name_key);")
        con.close()
    else:
        con = ddb.connect(db_path)
        ow = "OR REPLACE" if overwrite else "OR IGNORE"
        con.sql(f"INSERT {ow} INTO docs SELECT * FROM data")
        con.close()
