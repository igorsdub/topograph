import typer

app = typer.Typer()


@app.command()
def version():
    print("TopoGraph 0.1.0")