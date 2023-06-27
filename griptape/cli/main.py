import click

from griptape.cli.commands.app import app


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {}


cli.add_command(app)
