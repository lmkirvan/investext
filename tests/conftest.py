import pytest
from pathlib import Path
import shutil
import pytest
import sys

@pytest.fixture(scope="session")
def docs_directory(tmp_path_factory):
    source_data = Path(__file__).parent / "data"
    dest_data = tmp_path_factory.mktemp("data", numbered = False ) 
    if source_data.exists():
        shutil.copytree(source_data, dest_data, dirs_exist_ok=True)
    else :
        print("did you forget to add data for your tests?")
        sys.exit(1)
    return dest_data
