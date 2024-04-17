import click

from griptapecli.commands.skatepark import skatepark


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {}


cli.add_command(skatepark)
