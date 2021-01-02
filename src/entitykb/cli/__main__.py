from .cli import cli
from . import commands
from . import users

if __name__ == "__main__":
    assert commands
    assert users
    cli()
