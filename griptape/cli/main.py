import click

from griptape.cli.commands.app import app
from griptape.cli.commands.cloud import cloud
from griptape.cli.commands.server import server


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {}


cli.add_command(app)
cli.add_command(cloud)
cli.add_command(server)
