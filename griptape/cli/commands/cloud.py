import click
from click import echo
from griptape.cli.core.utils.auth import get_auth_token


@click.group()
@click.pass_context
def cloud(ctx):
    pass


@cloud.command(name="login")
@click.option(
    "--relogin",
    "-r",
    is_flag=True,
    help="Set flag to force relogin",
)
@click.option(
    "--endpoint-url",
    "-e",
    type=str,
    required=False,
    help="Override default endpoint url",
    default="http://localhost:8000",
)
def login(relogin: bool, endpoint_url: str) -> None:
    try:
        get_auth_token(relogin, endpoint_url)
        echo("Login succeeded")
    except Exception as e:
        echo(f"{e}")
