import typer
from . import launch_rpc, launch_http

app = typer.Typer()


@app.command()
def rpc():
    launch_rpc()


@app.command()
def http():
    launch_http()


if __name__ == "__main__":
    app()
