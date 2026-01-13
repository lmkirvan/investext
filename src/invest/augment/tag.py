import typer
import duckdb as ddb 
import os

from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
from string import Template


sql_template =  Template(
    """
        SELECT id, score
        FROM (
            SELECT *, fts_main_docs.match_bm25(
                id,
                ${query_string},
                fields := ${fields},
                conjunctinve = ${must}
            ) AS score
            FROM docs
        ) sq
        WHERE score IS NOT NULL
        ORDER BY score DESC;
    """
)

app  = typer.Typer()
# this there only reason to limit the search to just certain things? 
# I kind of think it's way simpler just to run the search on everything 
# but maybe allowing for some filter conditions makes sense?    
@app.command()
def tag( 
    query_string: str,
    must: bool = False,
    fields: Optional[List[str]] = None,
    add_to_spec: bool = False, 
        all: bool = False,
    verbose: int = 0 
):
    """
    tag an indexed field in the database. the tag will then be available for use 
    in outputing to markdown and will be stored in a table of saved searches.

    query_string    :   str 
                        a keyword search string using bm25. 
    must            :   bool
                        require all words to appear
    fields          :   list of str
                        if multiple fields are indexed this will be for supplying them (eventually) 
    add_to_spec     :   bool
                        this will append the search to your spec file for describing your corpus
    verbose         :   int
                        if 0- don't print any examples. otherwise print up to n examples. max 10. 
    """

    # this should be a callback I think need to consult the docs on that
    load_dotenv(".env")
    assert os.getenv("INVEST_INIT") == 'yes', "Looks like you have not initialized a project, or you're in the wrong directory"

    dbparent = Path(os.environ["INVEST_ROOT"])
    db_path = dbparent / ".data.db"

    con = ddb.connect(".data.db")

    if fields is None:
        fields = ["text"]

    filled_template = sql_template.substitute(fields=fields, query_string=query_string)





