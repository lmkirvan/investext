from typer.testing import CliRunner
from src.invest.main import app
from pathlib import Path
import os
import subprocess

runner = CliRunner()

os.system("rm .data.db")

def test_add():
  result = runner.invoke(app, ['invest', 'add', "./sample/emails/001"])
  assert result.exit_code == 0
  assert Path(".data.db").exists()
  rows = subprocess.run(["duckdb", "-list", ".data.db",  "'SELECT count(id) from docs'"], capture_output=True)
  print(rows)
  result = runner.invoke(app, ['invest', 'add', 'sample/emails/002'])
  assert result.exit_code == 0 
  # rows = os.system("duckdb -list .data.db 'SELECT count(id) from docs'")
  #assert rows == 2895 


