import typer
import duckdb as ddb 
import polars as pl
import re

from .. dbops  import dbops
from typing import List, Annotated, Optional

app = typer.Typer()
tag_app = typer.Typer()
app.add_typer(tag_app)
start_app = typer.Typer()
app.add_typer(start_app)

@tag_app.command()
def tag( 
    query_string: str = typer.Argument(help="a keyword search string using bm25" ),
    fields: Annotated[ Optional[List[str]], typer.Argument(help="Which text fields? Defaults to all") ] = None,
    must: Annotated[bool, typer.Option(help="require all words to appear")] = False,
    add_to_spec: Annotated[bool, typer.Option(help="Save your search to a log and the database")] = True
):
    """
    tag an indexed field in the database. the tag will then be available for use
    in outputing to markdown and will be stored in a table of saved searches
    """

    #todo https://typer.tiangolo.com/tutorial/arguments/envvar/
    # all this enironvment variable stuff should probably be done as cli arguments
    # that are filled as in the docs linked  above
    # I think you just run load dotenv as a callback before any commands to make sure you have them? 
     
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
    first_run = ("tags") not in tables

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


@start_app.command()
def starts(
    starts: Annotated[ str,
        typer.Argument(help="match the first token of a line a keyword")],
    add_to_spec: Annotated[bool, typer.Option(help="Save your search to a log and the database")] = False
):
    """
    Used to pull information out the text and make it part of the 
    metadata for the document. You can do this in two ways. starts matches the first
    token in a line and then caputures the remainder of the line as a key value pair. 
    Or you can provide a keyvalue pair with a name and a regex. This will result in a 
    new column in the main docs database with the captured content. 
    """     
    
    con = ddb.connect(".data.db")

    starts_re = (f"(^{starts.lower()})(.*)")
    
    tables = con.sql('SHOW TABLES').fetchall() 
    first_run = ("keys") not in tables
 
    def query_template(starts) -> str:
        query_template =  (
        f"SELECT \n"
        f"  ID,\n" 
        f"  regexp_extract(text.lower(), '{starts}', ['key', 'value']) as starts_with\n"
        f"FROM docs\n"
        f"WHERE struct_extract(starts_with, 'key') != ''"
        )
        return query_template

    if first_run and add_to_spec:
        final_query = dbops.query_create_table(query_template(starts_re), table_name="tags")
    else: 
        if add_to_spec:
            final_query = dbops.insert_query_into(
                query_template(starts_re),
                table_name="tags"
            )
        else:
            final_query = query_template(starts_re)
    
    if add_to_spec:
        con.sql(final_query)
        # log to spec here. 
        result = 0 
    else: 
        result = con.sql(final_query)
        typer.echo(result)
    
    return result




@tag_app.command()
def recapture(
    regex: Annotated[ List[str], typer.Argument(
        help="a string pair of KEY=REGEX"
    )],
    fields: Annotated[List[str] | None, typer.Option ] = None,
    add_to_spec: bool = False
):
    """
    Used to pull information out the text and make it part of the 
    metadata for the document. You can do this in two ways. starts matches the first
    token in a line and then caputures the remainder of the line as a key value pair. 
    Or you can provide a keyvalue pair with a name and a regex. This will result in a 
    new column in the main docs database with the captured content. 
    """
    con = ddb.connect(".data.db")

    def valid_regex(regex:str) -> bool :
        try:
            re.compile(regex)
            return True
        except:
            return False

    assert valid_regex(regex), "Your regex didn't compile") 



    tables = con.sql('SHOW TABLES').fetchall() 
    first_run = ("keys") not in tables
 
    def query_template(starts) -> str:
        query_template =  (
        f"SELECT \n"
        f"  ID,\n" 
        f"  regexp_extract(text.lower(), '{starts}', ['key', 'value']) as starts_with\n"
        f"FROM docs\n"
        f"WHERE struct_extract(starts_with, 'key') != ''"
        )
        return query_template



  #  if first_run and add_to_spec:
  #      final_query = dbops.query_create_table(query_template(tarts_re), table_name="tags")
  #  else: 
  #      if add_to_spec:
  #          final_query = dbops.insert_query_into(
  #              query_template(regex),
  #              table_name="tags"
  #          )
  #      else:
  #          final_query = query_template(regex)
  #  
  #  if add_to_spec:
  #      con.sql(final_query)
  #      # log to spec here. 
  #      result = 0 
  #  else: 
  #      result = con.sql(final_query)
  #      typer.echo(result)
  #  
  #  return result


