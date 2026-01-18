import typer
import duckdb as ddb 
import os

from .. dbops  import dbops
from typing import List, Annotated
from pathlib import Path
from dotenv import load_dotenv

app = typer.Typer()
tag_app = typer.Typer()
app.add_typer(tag_app)

@tag_app.command()
def tag( 
    query_string: str,
    must: bool = False,
    fields: Annotated[List[str] | None, typer.Option ] = None,
    add_to_spec: bool = False, 
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
        fields = ["NULL"]
    if must:
        must_sql = 1
    else: 
        must_sql = 0 
    
    sql_template =  (
        f' SELECT id, {query_string}\n'
        f' FROM (\n'
        f'     SELECT *, fts_main_docs.match_bm25(\n'
        f'         id,\n'
        f"         '{query_string}',\n"
        f"         fields := '{", ".join(fields)}',\n"
        f'         conjunctive := {must_sql}\n'
        f'     ) AS  {query_string} \n'
        f'     FROM docs\n'
        f' )\n'
    )

    typer.echo(sql_template)
    typer.echo(dbops.add_column_float(sql_template, "docs", query_string)) 
    #query_result = con.sql(sql_template)
    #typer.echo(query_result)
    return 0




