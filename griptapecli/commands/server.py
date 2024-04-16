import click
import functools
import uvicorn
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    logger.info(f"Server started at http://{host}:{port}")
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
    logger.debug("Structure registered")
    url = f"http://{host}:{port}/api/structures"
    logger.info(f"Registering structure: {directory}")
    response = requests.post(
        url,
        json={
            "directory": directory,
            "main_file": main_file,
            "environment": dict(environment),
        },
    )
    logger.info(response.text)


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
