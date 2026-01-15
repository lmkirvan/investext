
from typer.testing import CliRunner
from pathlib import Path
import os

search_str = """    
    select count( score)  
    from  (select *, fts_main_docs.match_bm25(id, 'trump', fields :='text') 
    as score from docs);
"""

runner = CliRunner()

def test_tag(docs_directory):
    os.chdir(docs_directory)
    db = Path('.data.db')
    #making sure that there is a database when this test is run 
    assert db.exists()
