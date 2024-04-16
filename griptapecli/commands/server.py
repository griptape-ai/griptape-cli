import click
import functools
import uvicorn
import requests


def server_options(func):
    @click.option(
        "--host",
        "-h",
        type=str,
        help="Host to run the server on",
        default="127.0.0.1",
        required=False,
    )
    @click.option(
        "--port",
        "-p",
        type=int,
        help="Port to run the server on",
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
        "--main-file",
        type=str,
        help="Main file for the Structure",
        default="structure.py",
        required=False,
    )
    @click.option(
        "environment",
        "--environment",
        "-e",
        type=(str, str),
        help="Environment key-pairs for the Structure",
        multiple=True,
        default=[],
        required=False,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@click.group()
@click.pass_context
def server(ctx):
    pass


@server.command(name="start")
@server_options
def start(
    host: str,
    port: int,
) -> None:
    """Starts the Griptape server."""
    uvicorn.run(
        "griptapecli.core.server:app",
        host=host,
        port=port,
        reload=False,
    )


@server.command(name="register")
@server_options
@structure_options
def register(
    host: str,
    port: int,
    directory: str,
    main_file: str,
    environment: list[tuple[str, str]],
) -> None:
    url = f"http://{host}:{port}/api/structures"
    directory = directory.rstrip("/")
    click.echo(f"Registering structure: {directory}/{main_file}")
    response = requests.post(
        url,
        json={
            "directory": directory,
            "main_file": main_file,
            "environment": dict(environment),
        },
    )
    response.raise_for_status()

    structure_id = response.json()["structure_id"]

    click.echo(f"Structure registered with id: {structure_id}")


@server.command(name="build")
@server_options
@click.option(
    "--structure-id",
    "-s",
    type=str,
    help="Id of the Structure to build",
    default="active",
    required=False,
)
def build(
    host: str,
    port: int,
    structure_id: str,
) -> None:
    url = f"http://{host}:{port}/api/structures/{structure_id}/build"
    response = requests.post(
        url,
        json={},
    )
    response.raise_for_status()

    click.echo(f"Structure built: {structure_id}")


@server.command(name="list")
@server_options
def list_structures(
    host: str,
    port: int,
) -> None:
    url = f"http://{host}:{port}/api/structures"
    response = requests.get(url)
    response.raise_for_status()

    structures = response.json()
    if structures:
        for structure in structures:
            structure_id = structure["structure_id"]
            directory = structure["directory"].rstrip("/")
            main_file = structure["main_file"]
            click.echo(f"{structure_id} -> {directory}/{main_file}")
    else:
        click.echo("No structures registered")


@server.command(name="remove")
@server_options
@click.option(
    "--structure-id",
    "-s",
    type=str,
    help="Id of the Structure to remove",
    required=True,
)
def remove_structure(
    host: str,
    port: int,
    structure_id: str,
) -> None:
    url = f"http://{host}:{port}/api/structures/{structure_id}"
    response = requests.delete(url)
    response.raise_for_status()

    click.echo(f"Structure removed: {structure_id}")
