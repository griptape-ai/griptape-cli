import click

from griptapecli.commands.server import server


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {}


cli.add_command(server)
