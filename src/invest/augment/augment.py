import typer
import duckdb as ddb 
import os

from .. dbops  import dbops
from typing import List, Annotated, Optional
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
    add_to_spec: bool = False
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
                        this will append the search to your spec file for describing your corpus, if false query prints to st.out
    verbose         :   int
                        if 0- don't print any examples. otherwise print up to n examples. max 10. 
    """

    #todo https://typer.tiangolo.com/tutorial/arguments/envvar/
    # all this enironvment variable stuff should probably be done as cli arguments 
    # that are filled as in the docs linked  above
    load_dotenv(".env")
    assert os.getenv("INVEST_INIT") == 'yes', "Looks like you have not initialized a project, or you're in the wrong directory"

    dbparent = Path(os.environ["INVEST_ROOT"])
    assert os.getcwd() == str(dbparent), "Are you in the root of your project?" 
    con = ddb.connect(".data.db")

    if fields is None:
        fields = ["NULL"]
    if must:
        must_sql = 1
    else: 
        must_sql = 0 
   
    query = query_string
    query_col_name = query_string.replace(' ', '_')

    tables = con.sql('SHOW TABLES').fetchall() 
    first_run = ("tags", ) not in tables

    def query_template() -> str:
        query_template =  (
        f"SELECT id, score, '{query_col_name}' as query \n"
        f'FROM (\n'
        f'  SELECT *, fts_main_docs.match_bm25(\n'
        f'      id,\n'
        f"      '{query}',\n"
        f"      fields := {", ".join(fields)},\n"
        f'      conjunctive := {must_sql}\n'
        f'  ) AS  score \n'
        f'  FROM docs\n'
        f'  WHERE score IS NOT NULL\n'
        f')\n'
        )
        return query_template

    if first_run and add_to_spec:
        final_query = dbops.query_create_table(query_template(), table_name="tags")
    else: 
        if add_to_spec:
            final_query = dbops.insert_query_into(query_template(), table_name="tags")
        else:
            final_query = query_template()
    
    if add_to_spec:
        con.sql(final_query)
        result = 0 
    else: 
        result = con.sql(final_query)
        typer.echo(result)
    return result


@tag_app.command()
def starts_with(
    starts_with : Annotated[ List[str], typer.Argument(
        help="match the first token of a line a keyword"
    )],
    fields: Annotated[List[str] | None, typer.Option ] = None,
    add_to_spec: bool = False
):
    """
    Used to pull information out the text and make it part of the 
    metadata for the document. You can do this in two ways. starts_with matches the first
    token in a line and then caputures the remainder of the line as a key value pair. 
    Or you can provide a keyvalue pair with a name and a regex. This will result in a 
    new column in the main docs database with the captured content. 
    """
    pass


@tag_app.command()
def recapture(
    capture: Annotated[ List[str], typer.Argument(
        help="a string pair of KEY=REGEX"
    )],
    fields: Annotated[List[str] | None, typer.Option ] = None,
    add_to_spec: bool = False
):
    """
    Used to pull information out the text and make it part of the 
    metadata for the document. You can do this in two ways. starts_with matches the first
    token in a line and then caputures the remainder of the line as a key value pair. 
    Or you can provide a keyvalue pair with a name and a regex. This will result in a 
    new column in the main docs database with the captured content. 
    """
    pass


