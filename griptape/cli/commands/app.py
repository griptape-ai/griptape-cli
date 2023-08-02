import os
import click
from click import echo
from griptape.artifacts import TextArtifact
from griptape.cli.core.app import App
from griptape.cli.core.app_deployer import AppDeployer
from griptape.cli.core.structure_runner import StructureRunner

from griptape.cli.core.utils.constants import DEFAULT_ENDPOINT_URL

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
    show_default=True
)
@click.option(
    "--directory", "-d",
    type=str,
    help="Directory to create a new app in.",
    default=".",
    show_default=True
)
def new(name: str, package_manager: str, directory: str) -> None:
    """
    Create a new Griptape app.
    """

    echo(f"Initializing app {name}")

    App(
        name=name,
        package_manager=package_manager
    ).generate(directory)


@app.command(name="run")
@click.option(
    "--arg", "-a",
    multiple=True,
    type=str,
    required=True
)
@click.option(
    "--directory", "-d",
    type=str,
    help="Directory where app resides. Defaults to current directory.",
    default=os.getcwd(),
    show_default=True
)
def run(arg: list[str], directory: str) -> TextArtifact:
    """
    Run a Griptape app.
    """

    structure_runner = StructureRunner(arg=arg, app_directory=directory)
    structure_runner.run()


@app.command(name="deploy")
@click.option(
    "--directory", "-d",
    type=str,
    help="Directory where app resides. Defaults to current directory.",
    default=os.getcwd(),
    show_default=True
)
@click.option(
    "--endpoint-url", "-e",
    type=str,
    required=False,
    help="Override default endpoint url",
    default=DEFAULT_ENDPOINT_URL,
)
@click.option(
    "--name", "-n",
    type=str,
    help="Griptape Cloud app name",
    default=None,
    required=False
)
def deploy(directory: str, endpoint_url: str, name: str) -> None:
    """
    Deploy a Griptape app to Griptape Cloud.
    """

    app_deployer = AppDeployer(app_directory=directory, endpoint_url=endpoint_url, name=name)
    app_deployer.deploy()
