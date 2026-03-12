import typer

from .transforms import app as transforms_app
from .version import app as version_app

app = typer.Typer()

app.add_typer(transforms_app, name="transforms")
app.add_typer(version_app)

if __name__ == "__main__":
    app()
