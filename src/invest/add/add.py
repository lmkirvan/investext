import typer
import duckdb as ddb 
import polars as pl 
import os

from typing import List, Annotated, Any, Dict
from rich import print
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv 

def bin_mask(l: List[Any], p: List[bool]) -> List[Any]:
    assert len(l) == len(p)
    return [item for item, keep in zip(l, p) if keep] 

def read_whole_folder(root: str, items: List[str]) -> Dict:
    text = []
    p = Path(root)
    for i in items:
        lines = (p / i).read_text().split(sep="\n")
        lines = list(map(str.strip, lines))
        text.append(lines)
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
    overwrite: int = 1,
    #todo should I put a field in here to label the doc type? like "emails" or something like that 
): 

    load_dotenv(".env")
    assert os.getenv("INVEST_INIT") == 'yes',\
    "Looks like you have not initialized a project, or you're in the wrong directory"

    assert overwrite >= 0 and overwrite <=1, "overwrite must be 0 or 1" 
    
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
    
    # todo maybe add some more metadata stuff here? 
    # ntokens, file size
    # todo update with only new stuff if the same folder is accessed twice
    data = pl.concat(dfs)
    data = data.with_columns(
        pl.lit(datetime.now()).alias("date_added"),
    )

    data = data.explode('text')
    data = data.with_columns(
        pl.int_range(0, pl.len()).over(["root", "file"]).alias("line_id"),
        pl.col('text').str.extract(r"(\S+)", 0).alias("first_token") 
    )

    data = data.with_columns(
        pl.concat_str(["root", "file", "line_id"], separator="-").alias("id")
    )

    
    dbparent = Path(os.environ["INVEST_ROOT"])
    db_path = dbparent / db_name
    #if there is no database we have to build one from scratch here. 
    if not db_path.exists():
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
    con.sql(f"PRAGMA create_fts_index('docs', 'id', 'text', 'first_token', overwrite={overwrite}, stopwords='none')")
    con.close()
