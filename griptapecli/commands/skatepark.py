import functools
import os

import click
import requests
import uvicorn

from griptapecli.core.models import Structure, StructureRun


def server_options(func):
    @click.option(
        "--host",
        "-h",
        type=str,
        help="Host to run the Skatepark emulator on",
        default="127.0.0.1",
        required=False,
    )
    @click.option(
        "--port",
        "-p",
        type=int,
        help="Port to run the Skatepark emulator on",
        default=5000,
        required=False,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def structure_options(func):
    @click.option(
        "--directory",
        "-d",
        type=str,
        help="Directory containing the Structure to register",
        default=".",
        required=False,
    )
    @click.option(
        "--structure-config-file",
        type=str,
        help="Config file for the Structure",
        default="structure_config.yaml",
        required=False,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@click.group()
@click.pass_context
def skatepark(ctx):
    pass


@skatepark.command(name="start")
@server_options
def start(
    host: str,
    port: int,
) -> None:
    """Starts the Griptape server."""
    uvicorn.run(
        "griptapecli.core.skatepark:app",
        host=host,
        port=port,
        reload=False,
        workers=1,  # Skatepark only supports 1 worker. We're explictly setting it here to avoid inheriting it from the environment.
    )


@skatepark.command(name="register")
@server_options
@structure_options
@click.option("--tldr", is_flag=True)
def register(
    host: str,
    port: int,
    directory: str,
    structure_config_file: str,
    tldr: bool,
) -> None:
    """Registers a Structure with Skatepark."""
    url = f"http://{host}:{port}/api/structures"
    directory = os.path.abspath(directory)
    if tldr is False:
        click.echo(f"Registering Structure from {directory}/{structure_config_file}")
    response = requests.post(
        url,
        json={
            "directory": directory,
            "structure_config_file": structure_config_file,
        },
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        click.echo(f"HTTP Error: {e}")
        return

    structure_id = response.json()["structure_id"]

    if tldr:
        click.echo(structure_id)
    else:
        click.echo(f"Structure registered with id: {structure_id}")


@skatepark.command(name="build")
@server_options
@click.option(
    "--structure-id",
    "-s",
    type=str,
    help="Id of the Structure to build",
    required=True,
    prompt=True,
    default=lambda: os.environ.get("GT_STRUCTURE_ID", None),
    show_default="GT_STRUCTURE_ID environment variable",
)
def build(
    host: str,
    port: int,
    structure_id: str,
) -> None:
    """Builds the Structure by creating a virtual environment and installing dependencies."""
    click.echo(f"Building Structure: {structure_id}")
    url = f"http://{host}:{port}/api/structures/{structure_id}/build"
    response = requests.post(
        url,
        json={},
    )
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        click.echo(f"HTTP Error: {e}")
        return

    click.echo(f"Structure built: {structure_id}")


@skatepark.command(name="run")
@server_options
@click.option(
    "--structure-id",
    "-s",
    type=str,
    help="Id of the Structure to run",
    required=True,
    prompt=True,
    default=lambda: os.environ.get("GT_STRUCTURE_ID", None),
    show_default="GT_STRUCTURE_ID environment variable",
)
@click.option(
    "--arg",
    "-a",
    type=str,
    help="Argument to pass to the Structure Run",
    required=False,
    prompt=True,
    multiple=True,
)
@click.option(
    "--env",
    "-e",
    type=dict,
    help="Environment Variables to pass to the Structure Run",
    required=False,
    prompt=False,
    default=lambda: {},
)
def run(host: str, port: int, structure_id: str, arg: list[str], env: dict) -> None:
    """Runs the Structure."""
    click.echo(f"Running Structure: {structure_id}")
    url = f"http://{host}:{port}/api/structures/{structure_id}/runs"

    response = requests.post(
        url,
        json={
            "args": list(arg),
            "env": env,
        },
    )
    try:
        response.raise_for_status()
        run_id = response.json()["structure_run_id"]
        run = _get_structure_run(host, port, run_id)
        while run.status not in [
            StructureRun.Status.SUCCEEDED,
            StructureRun.Status.FAILED,
            StructureRun.Status.CANCELLED,
        ]:
            run = _get_structure_run(host, port, run.structure_run_id)

        if run.status == StructureRun.Status.SUCCEEDED:
            click.echo(f"Structure run succeeded: {run_id}, output: {run.output}")
        elif run.status == StructureRun.Status.FAILED:
            click.echo(f"Structure run failed: {run_id}, logs: {run.logs}")
    except requests.exceptions.HTTPError as e:
        click.echo(f"HTTP Error: {e}")
        return


def _get_structure_run(
    host: str,
    port: int,
    structure_run_id: str,
) -> StructureRun:
    url = f"http://{host}:{port}/api/structure-runs/{structure_run_id}"
    response = requests.get(url)
    response.raise_for_status()

    structure_run = response.json()
    return StructureRun(**structure_run)


def _get_structure(
    host: str,
    port: int,
    structure_id: str,
) -> Structure:
    url = f"http://{host}:{port}/api/structures/{structure_id}"
    response = requests.get(url)
    response.raise_for_status()

    structure = response.json()
    return Structure(**structure)


@skatepark.command(name="list")
@server_options
def list_structures(
    host: str,
    port: int,
) -> None:
    """Lists all registered Structures."""
    url = f"http://{host}:{port}/api/structures"
    response = requests.get(url)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        click.echo(f"HTTP Error: {e}")
        return

    structures = response.json()["structures"]
    if structures:
        for structure in structures:
            structure_id = structure["structure_id"]
            directory = structure["directory"]
            structure_config_file = structure["structure_config_file"]
            env = structure["env"]
            click.echo(f"{structure_id} -> {directory}/{structure_config_file} ({env})")
    else:
        click.echo("No structures registered")


@skatepark.command(name="remove")
@server_options
@click.option(
    "--structure-id",
    "-s",
    type=str,
    help="Id of the Structure to remove",
    required=True,
    prompt=True,
    default=lambda: os.environ.get("GT_STRUCTURE_ID", None),
    show_default="GT_STRUCTURE_ID environment variable",
)
def remove_structure(
    host: str,
    port: int,
    structure_id: str,
) -> None:
    """Removes a Structure from Skatepark."""
    url = f"http://{host}:{port}/api/structures/{structure_id}"
    response = requests.delete(url)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        click.echo(f"HTTP Error: {e}")
        return

    click.echo(f"Structure removed: {structure_id}")
