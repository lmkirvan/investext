import typer
import os
from pathlib import Path 
from dotenv import load_dotenv

from .augment import app as augment_app

def check_env():
    load_dotenv(".env")
    assert os.getenv("INVEST_INIT") == 'yes', \
    "Looks like you have not initialized a project, or you're in the wrong directory"
    dbparent = Path(os.environ["INVEST_ROOT"])
    assert os.getcwd() == str(dbparent), "Are you in the root of your project?"

app = typer.Typer(callback=check_env, name = "augment")
app.add_typer(augment_app)
