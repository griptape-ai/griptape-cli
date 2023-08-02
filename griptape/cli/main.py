import click

from griptape.cli.commands.app import app
from griptape.cli.commands.cloud import cloud


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {}


cli.add_command(app)
cli.add_command(cloud)
