import click
from click import echo
from griptape.structures import Structure

from griptape.cli.core.app import App


@click.group()
@click.pass_context
def app(ctx):
    pass


@app.command(name="new")
@click.argument(
    "name",
    type=str,
    required=True,
)
@click.option(
    "--package_manager", "-p",
    type=click.Choice(["pip", "poetry"]),
    help="Package manager to use for Griptape app.",
    default="pip",
    show_default=True,
)
def new(name: str, package_manager: str) -> None:
    """
    Create a new Griptape app.
    """

    echo(f"Initializing app {name}")

    App(
        name=name,
        package_manager=package_manager
    ).generate()


@app.command(name="run")
@click.option(
    "--arg", "-a",
    multiple=True,
    type=str,
    required=True
)
def run(arg: list[str]) -> None:
    try:
        from app import init_structure

        try:
            init_structure().run(*arg)
        except Exception as e:
            echo(f"Error running app: {e}", err=True)
    except Exception as e:
        echo("App doesn't exist", err=True)

