import tomllib
import typer
import duckdb as ddb
from typing import Annotated, Optional, List, Any
from pathlib import Path
from enum import Enum


class Line:
    def __init__(self, tag: Enum, content:str):
        self.tag = tag
        self.content = content

    def __str__(self): 
        return f"line type {self.tag.name} with contents: {self.content}"

    def __repr__(self):
        return(str(self.tag))

#there has to be a way to make the types work here, but not for me to figure out at the moment
def get_raw_docs() -> Optional[List[Any]]:
    con = ddb.connect(".data.db")
    docs = con.sql("SELECT text FROM main;").fetchall() 
    con.close()

    return docs

app = typer.Typer()

@app.command()
def markdown(
    config: Annotated[
        Optional[Path],
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ]
):
    if config is None:
        print("No config provided") 
        raise typer.Abort()
    if config.is_file() and config.suffix == ".toml":
        print('reading file')
        with config.open( "rb") as f:
            con_par = tomllib.load(f)
    else: 
        print("Couldn't find the file. Where's the toml at?")
        raise typer.Abort()

    Tags = Enum("starts_with", con_par["starts_with"])

    def tag_line(line: str):
        line = line.strip()
        for t in Tags:
            if line.startswith(t.value):
                if t.value == "":
                    start_pos = 0
                else: 
                    start_pos = len(t.value)
                return(Line(t, line[start_pos : ] ))
            else: 
                pass
    
    def tag_lines(lines: List[str]):
        res = []
        for line in lines:
            res.append(tag_line(line))
        return res

    get_raw_docs()


