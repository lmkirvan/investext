from typer.testing import CliRunner
from invest.main import app
from pathlib import Path
import subprocess
import shutil
import pytest
import sys


search_str = """    
    select count( score)  
    from  (select *, fts_main_docs.match_bm25(name_key, 'trump', fields :='text') 
    as score from docs);
"""


@pytest.fixture
def docs_directory(tmp_path_factory):
    source_data = Path(__file__).parent / "data"
    dest_data = tmp_path_factory.mktemp("data")
    if source_data.exists():
        shutil.copytree(source_data, dest_data, dirs_exist_ok=True)
    else :
        print("did you forget to add data for your tests?")
        sys.exit(1)
    return dest_data

runner = CliRunner()

def test_add(docs_directory):
    # this tests the make a new database path
    result = runner.invoke(app, ['add', str(docs_directory / "001")])
    assert result.exit_code == 0
    assert Path(".data.db").exists()
    rows = subprocess.check_output(
        ["duckdb", "-ascii", str(docs_directory / ".data.db"), "SELECT count(id) FROM docs"])
    rows_str = rows.decode('utf-8')
    assert rows_str == 'count(id)\n3\n' 
    result = runner.invoke(app, ['add', str(docs_directory/ "002") ])
    assert result.exit_code == 0 
    rows = subprocess.check_output(
        ["duckdb", "-ascii", str(docs_directory / ".data.db"), "SELECT count(id) FROM docs"])
    rows_str = rows.decode('utf-8')
    assert rows_str == 'count(id)\n9\n'
    rows_str = subprocess.check_output(
        ["duckdb", "-ascii", str(docs_directory / ".data.db"), search_str])
    assert rows_str ==  b'count(score)\n8\n'


