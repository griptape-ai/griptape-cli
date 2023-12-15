import os
import click
from click import echo
from griptape.artifacts import TextArtifact
from griptape.cli.core.app import App
from griptape.cli.core.structure_runner import StructureRunner


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
    "--package_manager",
    "-p",
    type=click.Choice(["pip"]),
    help="Package manager to use for Griptape app.",
    default="pip",
    show_default=True,
)
@click.option(
    "--directory",
    "-d",
    type=str,
    help="Directory to create a new app in.",
    default=".",
    show_default=True,
)
@click.option(
    "--griptape-version",
    "-g",
    type=str,
    help="Version of griptape to use for the app.",
    required=False,
)
def new(name: str, package_manager: str, directory: str, griptape_version: str) -> None:
    """
    Create a new Griptape app.
    """

    echo(f"Initializing app {name}")

    App(
        name=name, package_manager=package_manager, griptape_version=griptape_version
    ).generate(directory)


@app.command(name="run")
@click.option("--arg", "-a", multiple=True, type=str, required=True)
@click.option(
    "--init-param",
    "-i",
    "init_params",
    type=(str, str),
    multiple=True,
    help="Initialization parameters for the app in the format 'key value'.",
    required=False,
)
@click.option(
    "--directory",
    "-d",
    type=str,
    help="Directory where app resides. Defaults to current directory.",
    default=os.getcwd(),
    show_default=True,
)
def run(
    arg: list[str], init_params: list[tuple[str, str]], directory: str
) -> TextArtifact:
    """
    Run a Griptape app.
    """

    echo(f"Running app")
    params = {k: v for k, v in init_params}

    structure_runner = StructureRunner(
        args=arg, init_params=params, app_directory=directory
    )
    structure_runner.run()
