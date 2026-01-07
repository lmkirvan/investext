import typer
from typing import List, Annotated, Any, Dict
from rich import print
from pathlib import Path
import duckdb as ddb 
import polars as pl 
from datetime import datetime

app  = typer.Typer()

def bin_mask(l: List[Any], p: List[bool]) -> List[Any]:
    assert len(l) == len(p)
    return [item for item, keep in zip(l, p) if keep] 

def read_whole_folder(root: str, items: List[str]) -> Dict:
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
            file_okay=False,
            dir_okay=True,
            resolve_path=False,
        ), 
    ],
    extension: str = "txt",
    db_name: str = ".data.db", # out put in the calling directory? I think so.
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
    
    # maybe add some more metadata stuff here? 
    # ntokens, file size 
    # for now just keep doing everything but eventuall can have the logic be to first
    # intersect before making the data
    data = pl.concat(dfs)
    data = data.with_row_index(name = "id")
    data = data.with_columns(
        pl.concat_str(['root', 'file'], separator="/").alias("name_key"),
        pl.lit(datetime.now()).alias("date_added")
    )

    # this creates a db in the parent directory of the documents directory
    # I think that this makes sense, but we should say in the readme that
    # this works with a project folder and probably should have some kind of
    # environment variable or something to keep the root of the directory available. 
    db_path = path.parent.absolute() / db_name 

    #if there is no database we have to build one from scratch here. 
    if not db_path.exists():
        con = ddb.connect(db_path)
        con.sql("CREATE TABLE docs AS SELECT * FROM data")
        con.sql("ALTER TABLE docs ADD PRIMARY KEY (name_key);")
    else:
        con = ddb.connect(db_path)
        ow = "OR REPLACE" if overwrite else "OR IGNORE"
        con.sql(f"INSERT {ow} INTO docs SELECT * FROM data")

    # From duckdb docs
    #Warning
    #The FTS index will not update automatically when input table changes. A workaround of this limitation can be recreating the index to refresh
    # we need to run this pragma add index thing either way, when we add or create for the first time

    con.sql("PRAGMA create_fts_index('docs', 'name_key', 'text', overwrite=1)")
    con.close()

