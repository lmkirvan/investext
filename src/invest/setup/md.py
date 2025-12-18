import tomllib 
import typer
import os

# I think this is kidn of stupid, but maybe I'll just let it ride for now. 
# the basic idea is make sure that commands run from the root directoy
# this will be handled differently in an actual application I suppose 
def check_setup():
    assert os.path.isfile('.invest'), ".invest is missing are you in the project root directory"

    file = open(".venv", "r")
    lines = file.readlines()

    set = False 
    for line in lines: 
        if line.startswith('SETUP'):
            if line.endswith("yes"):
                set = True

    assert set, "Looks like you haven't setup the database yet" 


app = typer.Typer(callback=check_setup)

@app.command(name = "markdown")
def markdown():
    pass



