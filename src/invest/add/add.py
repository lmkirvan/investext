import typer
import duckdb as ddb 
import polars as pl 
import os

from typing import List, Annotated, Any, Dict
from rich import print
from pathlib import Path
from datetime import datetime

def bin_mask(l: List[Any], p: List[bool]) -> List[Any]:
    assert len(l) == len(p)
    return [item for item, keep in zip(l, p) if keep] 

def read_whole_folder(root: str, items: List[str]) -> Dict:
    text = []
    p = Path(root)
    for i in items:
        text.append((p / i).read_text().split(sep="\n"))
    return {"root": root, 'file': items, "text": text}

app  = typer.Typer()

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
    data = data.with_columns(
        pl.lit(datetime.now()).alias("date_added")
    )

    data = data.explode('text')
    data = data.with_columns(
        pl.int_range(0, pl.len()).over(["root", "file"]).alias("line_id")
    )

    data = data.with_columns(
        pl.concat_str(["root", "file", "line_id"], separator="-").alias("id")
    )

    # this is a quick and dirty thing to make sure that you are working in the parent folder
    # probably this should be some kind of environment variable setup thing eventually
    # but I think that I can defer that for now TODO?
    dbparent = path.parent.absolute() 
    db_path = dbparent / db_name
    #if there is no database we have to build one from scratch here. 
    if not db_path.exists():
        os.environ["INVEST_ROOT"] = str(dbparent)
        con = ddb.connect(db_path)
        con.sql("CREATE TABLE docs AS SELECT * FROM data")
        con.sql("ALTER TABLE docs ADD PRIMARY KEY (id);")
    else:

        con = ddb.connect(db_path)
        ow = "OR REPLACE" if overwrite else "OR IGNORE"
        con.sql(f"INSERT {ow} INTO docs SELECT * FROM data")

    # From duckdb docs
    #Warning
    #The FTS index will not update automatically when input table changes. A workaround of this limitation can be recreating the index to refresh
    # we need to run this pragma add index thing either way, when we add or create for the first time

    con.sql("PRAGMA create_fts_index('docs', 'id', 'text', overwrite=1)")
    con.close()

