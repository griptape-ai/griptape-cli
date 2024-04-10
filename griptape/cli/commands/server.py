import click
import uvicorn


@click.group()
@click.pass_context
def server(ctx):
    pass


@server.command(name="start")
def start() -> None:
    """Starts the Griptape server."""
    uvicorn.run(
        "griptape.cli.core.server:app",
        host="127.0.0.1",
        port=5000,
        log_level="info",
        reload=True,
    )
