from typer.testing import CliRunner
from invest.main import app
import os

import subprocess
search_str = """    
    select count( score)  
    from  (select *, fts_main_docs.match_bm25(id, 'trump', fields :='text') 
    as score from docs);
"""

runner = CliRunner()

def test_add(docs_directory):

    dd = docs_directory
    os.chdir(dd)
    runner.invoke(app, ["init"])
    # this tests the make a new database path
    result = runner.invoke(app, ['add', str(dd / "001")])
    assert result.exit_code == 0
    database = dd / ".data.db"
    assert database.is_file() == True
    rows = subprocess.check_output(
        ["duckdb", "-ascii", str(dd / ".data.db"), "SELECT count(id) FROM docs"])
    rows_str = rows.decode('utf-8')
    assert rows_str == 'count(id)\n3778\n' 
    result = runner.invoke(app, ['add', str(dd/ "002") ])
    assert result.exit_code == 0 
    rows = subprocess.check_output(
        ["duckdb", "-ascii", str(dd / ".data.db"), "SELECT count(id) FROM docs"])
    rows_str = rows.decode('utf-8')
    assert rows_str == 'count(id)\n4025\n'
    # check the search module is working
    rows_str = subprocess.check_output(
        ["duckdb", "-ascii", str(dd / ".data.db"), search_str])
    assert rows_str ==  b'count(score)\n34\n'


