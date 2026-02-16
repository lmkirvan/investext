from invest.main import app
from typer.testing import CliRunner
from typer import echo
from pathlib import Path

import subprocess
import os


runner = CliRunner()

def test_tag(docs_directory):
    dd = docs_directory
    os.chdir(docs_directory)
    db = Path('.data.db')
    assert db.exists()

    result = runner.invoke(app, ["augment", "tag", "'trump'"])

    assert result.exit_code == 0 
    database = dd / ".data.db"
    assert database.is_file()

    rows = subprocess.check_output(
        ["duckdb", "-ascii", str(dd / ".data.db"), "SELECT count(id) FROM tags"]
    )

    rows_str = rows.decode('utf-8')

    assert rows_str == 'count(id)\n34\n'

    
#def test_add(docs_directory):
#
#    dd = docs_directory
#    os.chdir(dd)
#    runner.invoke(app, ["init"])
#    # this tests the make a new database path
#    result = runner.invoke(app, ['add', str(dd / "001")])
#    assert result.exit_code == 0
#    database = dd / ".data.db"
#    assert database.is_file() == True
#    rows = subprocess.check_output(
#        ["duckdb", "-ascii", str(dd / ".data.db"), "SELECT count(id) FROM docs"])
#    rows_str = rows.decode('utf-8')
#    assert rows_str == 'count(id)\n3778\n' 
#    result = runner.invoke(app, ['add', str(dd/ "002") ])
#    assert result.exit_code == 0 
#    rows = subprocess.check_output(
#        ["duckdb", "-ascii", str(dd / ".data.db"), "SELECT count(id) FROM docs"])
#    rows_str = rows.decode('utf-8')
#    assert rows_str == 'count(id)\n4025\n'
#    # check the search module is working
#    rows_str = subprocess.check_output(
#        ["duckdb", "-ascii", str(dd / ".data.db"), search_str])
#    assert rows_str ==  b'count(score)\n34\n'


    


