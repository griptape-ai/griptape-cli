import os
import click
import subprocess
import functools
import requests


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
        "--main-file",
        type=str,
        help="Main file for the Structure",
        default="structure.py",
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
    subprocess.run(
        [
            "gunicorn",
            "griptapecli.core.skatepark:app",
            "--preload",
            "--workers",
            "4",
            "--worker-class",
            "uvicorn.workers.UvicornWorker",
            "--bind",
            f"{host}:{port}",
        ]
    )
    """Starts the Griptape server."""
    # uvicorn.run(
    #     "griptapecli.core.skatepark:app", host=host, port=port, reload=False, workers=4
    # )


@skatepark.command(name="register")
@server_options
@structure_options
@click.option("--tldr", is_flag=True)
def register(
    host: str,
    port: int,
    directory: str,
    main_file: str,
    tldr: bool,
) -> None:
    url = f"http://{host}:{port}/api/structures"
    directory = os.path.abspath(directory)
    click.echo(f"Registering Structure from {directory}/{main_file}")
    response = requests.post(
        url,
        json={
            "directory": directory,
            "main_file": main_file,
        },
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        click.echo(f"HTTP Error: {e.response.text}")
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
    default=lambda: os.environ.get("GT_STRUCTURE_ID", ""),
    show_default="GT_STRUCTURE_ID environment variable",
)
def build(
    host: str,
    port: int,
    structure_id: str,
) -> None:
    click.echo(f"Building Structure: {structure_id}")
    url = f"http://{host}:{port}/api/structures/{structure_id}/build"
    response = requests.post(
        url,
        json={},
    )
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        click.echo(f"HTTP Error: {e.response.text}")
        return

    click.echo(f"Structure built: {structure_id}")


@skatepark.command(name="list")
@server_options
def list_structures(
    host: str,
    port: int,
) -> None:
    url = f"http://{host}:{port}/api/structures"
    response = requests.get(url)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        click.echo(f"HTTP Error: {e.response.text}")
        return

    structures = response.json()
    if structures:
        for structure in structures:
            structure_id = structure["structure_id"]
            directory = structure["directory"]
            main_file = structure["main_file"]
            env = structure["env"]
            click.echo(f"{structure_id} -> {directory}/{main_file} ({env})")
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
    default=lambda: os.environ.get("GT_STRUCTURE_ID", ""),
    show_default="GT_STRUCTURE_ID environment variable",
)
def remove_structure(
    host: str,
    port: int,
    structure_id: str,
) -> None:
    url = f"http://{host}:{port}/api/structures/{structure_id}"
    response = requests.delete(url)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        click.echo(f"HTTP Error: {e.response.text}")
        return

    click.echo(f"Structure removed: {structure_id}")
