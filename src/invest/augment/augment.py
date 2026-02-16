import typer
import duckdb as ddb 

from .. dbops  import dbops
from typing import List, Annotated, Optional

app = typer.Typer()
tag_app = typer.Typer()
app.add_typer(tag_app)
start_app = typer.Typer()
app.add_typer(start_app)

def use_template(template:str, table_name:str, conn: ddb.DuckDBPyConnection, first_run:bool, add_to_spec:bool):
    if first_run and add_to_spec:
        final_query = dbops.query_create_table(template, table_name=table_name)
    else: 
        if add_to_spec:
            final_query = dbops.insert_query_into(template, table_name=table_name)
        else:
            final_query = template
    if add_to_spec:
        conn.sql(final_query)
        result = 0 
    else:
        result = conn.sql(final_query)
        typer.echo(result)
    return result

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

    filled = query_template()
    res = use_template(filled, 'tags', con, first_run, add_to_spec)
    return res



@start_app.command()
def starts(
    starts: Annotated[ str,
        typer.Argument(help="match the first token of a line a keyword")],
    add_to_spec: Annotated[bool, typer.Option(help="Save your search to a log and the database")] = False
):
    """
    Grab lines that start with a string. These are stored in a the lines table as pattern and match.  
    """     
    
    con = ddb.connect(".data.db")
    starts_re = (f"(^{starts.lower()})(.*)")
    tables = con.sql("SHOW TABLES").fetchall() 
    first_run = ("lines") not in tables
 
    def query_template(starts) -> str:
        query_template =  (
        f"SELECT \n"
        f"  ID,\n"
        f"  regexp_extract(text.lower(), '{starts}', ['pattern', 'match']) as starts_with\n"
        f"FROM docs\n"
        f"WHERE struct_extract(starts_with, 'pattern') != ''"
        )
        return query_template

    filled = query_template(starts_re)
    res = use_template(filled, 'lines', con, first_run, add_to_spec)
    return res


@tag_app.command()
def recapture(
    pattern: Annotated[ str, typer.Argument(
        help="a string pair of KEY=REGEX")],
    fields: Annotated[ Optional[List[str]], typer.Argument(help="Which text fields? Defaults to all") ] = None,
    add_to_spec: bool = False
):
    """
    Capture the line numbers for the occurrences of a regex and add them to a table called keys. Will capture all (default) unless all is set to False. If all is set to false, captures only the first one. TODO change the interface so you can also specify a capture group integer maybe, or a separate function recapture_group() 
    """
    
    con = ddb.connect(".data.db")
    tables = con.sql('SHOW TABLES').fetchall() 
    first_run = ("keys",) not in tables 
    if fields == None:
        _fields = ["text"]
    else:
        _fields = fields
    try:
        key, value = pattern.split("=")
    except: 
        typer.echo("You didn't pass in a KEY=VALUE pair, try again")
        return 1
      
    def query_template(key: str, value:str, regex:str, field:str) -> str:
        query_template =  (
        f"SELECT \n"
        f"  ID,\n"
        f"  '{key}' as key,\n"
        f"  '{value}' as regex,\n" 
        f"  regexp_matches({field}.lower(), '{regex}') as match\n"
        f"FROM docs\n"
        f"WHERE  match;"
        )
        return query_template

    res = [] 

    for field in _fields:
        filled = query_template(
            key=key,
            value=value,
            regex=value,
            field=field
        )
        
        res.append( use_template(filled, 'keys', con, first_run, add_to_spec)) 
        first_run = False

    return res

