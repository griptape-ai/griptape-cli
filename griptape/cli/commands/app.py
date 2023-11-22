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
    type=click.Choice(["pip", "poetry"]),
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
def new(name: str, package_manager: str, directory: str) -> None:
    """
    Create a new Griptape app.
    """

    echo(f"Initializing app {name}")

    App(name=name, package_manager=package_manager).generate(directory)


@app.command(name="run")
@click.option("--arg", "-a", multiple=True, type=str, required=True)
@click.option(
    "--directory",
    "-d",
    type=str,
    help="Directory where app resides. Defaults to current directory.",
    default=os.getcwd(),
    show_default=True,
)
def run(arg: list[str], directory: str) -> TextArtifact:
    """
    Run a Griptape app.
    """

    echo(f"Running app")

    structure_runner = StructureRunner(args=arg, app_directory=directory)
    structure_runner.run()
