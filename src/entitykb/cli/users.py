from pathlib import Path
from typing import Optional

import typer
from tabulate import tabulate

from entitykb import KB, Auth, UserStatus
from . import cli, services

users_cli = typer.Typer()
cli.add_typer(users_cli, name="user", help="User management sub-commands")


def get_auth(root) -> Auth:
    kb = KB(root=root)
    if not isinstance(kb.auth, Auth):
        raise RuntimeError("CLI tools only work with entitykb.Auth component")
    return kb.auth


@users_cli.command("add")
def user_add(
    username: str,
    status: UserStatus = typer.Argument(UserStatus.read_only),
    root: Optional[Path] = typer.Option(None),
):
    """ Create new user account. """

    try:
        pw = get_auth(root).add_user(username=username, status=status)
        typer.echo(f"{username} created ({status.value}) with password: {pw}")

    except RuntimeError as e:
        typer.echo(f"Failed: {str(e)}")
        typer.Exit(1)


@users_cli.command("status")
def change_status(
    username: str,
    status: UserStatus,
    root: Optional[Path] = typer.Option(None),
):
    """ Set status to inactive, read_only, or read_write """

    success = get_auth(root).set_status(username, status)
    if success:
        typer.echo(f"User ('{username}') changed to '{status}' status")
    else:
        typer.echo(f"User ('{username}') status not changed")
        typer.Exit(1)


@users_cli.command("password")
def reset_password(
    username: str,
    root: Optional[Path] = typer.Option(None),
    force: bool = typer.Option(False, "--force", "-f"),
):
    """ Reset user's password """

    if not force:
        typer.confirm(
            f"Reset {username}'s password. Are you sure?", abort=True
        )

    new_password = get_auth(root).reset_password(username)
    if new_password:
        typer.echo(f"User ('{username}') new password: {new_password}")
    else:
        typer.echo(f"User ('{username}') not found")
        typer.Exit(1)


@users_cli.command("info")
def user_info(
    username: str,
    root: Optional[Path] = typer.Option(None),
):
    """ Display user information """

    user = get_auth(root).get_user(username)
    data = user.dict()
    data["hashed_password"] = data["hashed_password"][:14] + "..."
    flat = sorted(services.flatten_dict(data).items())
    output = tabulate(flat, tablefmt="pretty", colalign=("left", "right"))
    typer.echo(output)


@users_cli.command("check")
def user_check(
    username: str,
    root: Optional[Path] = typer.Option(None),
):
    """ Check username and password combo """

    password = typer.prompt(f"Enter password for {username}", hide_input=True)
    is_auth = get_auth(root).authenticate(username, password)

    if is_auth:
        typer.echo("Success: Username and password combination was valid")
    else:
        typer.echo("FAIL: Username and password combination was NOT valid")
        typer.Exit(1)
