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
        help="Directory containing the structure to register",
        default=".",
        required=False,
    )
    @click.option(
        "--entry-file",
        type=str,
        help="Entry file for the structure",
        default="structure.py",
        required=False,
    )
    @click.option(
        "environment",
        "--environment",
        "-e",
        type=(str, str),
        help="Environment key-pairs for the structure",
        multiple=True,
        default=(),
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
@structure_options
def start(
    host: str,
    port: int,
    directory: str,
    entry_file: str,
    environment: list[tuple[str, str]],
) -> None:
    """Starts the Griptape server."""
    uvicorn.run(
        "griptape.cli.core.server:app",
        host=host,
        port=port,
        log_level="info",
        reload=True,
    )
    register(directory, entry_file, environment)


@server.command(name="register")
@server_options
@structure_options
def register(
    host: str,
    port: int,
    directory: str,
    entry_file: str,
    environment: list[tuple[str, str]],
) -> None:
    url = f"http://{host}:{port}/api/structures"
    requests.post(
        url,
        json={
            "directory": directory,
            "entry_file": entry_file,
            "environment": dict(environment),
        },
    )


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
    requests.post(
        url,
        json={},
    )
