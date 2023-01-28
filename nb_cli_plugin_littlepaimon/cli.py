from typing import List, cast

import click
from nb_cli import _
from nb_cli.cli import CLI_DEFAULT_STYLE, ClickAliasedGroup, run_sync, run_async
from noneprompt import Choice, ListPrompt, CancelledError

from . import __version__
from .meta import LOGO


@click.group(cls=ClickAliasedGroup,
             invoke_without_command=True,
             help='管理 LittlePaimon.')
@click.version_option(
    __version__,
    "-V",
    "--version",
    prog_name="paimon",
    message="%(prog)s: NB CLI plugin version %(version)s for LittlePaimon",
)
@click.pass_context
@run_async
async def paimon(ctx: click.Context):
    """为 LittlePaimon 定制的Nonebot CLI 插件."""
    if ctx.invoked_subcommand is not None:
        return

    command = cast(ClickAliasedGroup, ctx.command)

    # auto discover sub commands and scripts
    choices: List[Choice[click.Command]] = []
    for sub_cmd_name in await run_sync(command.list_commands)(ctx):
        if sub_cmd := await run_sync(command.get_command)(ctx, sub_cmd_name):
            choices.append(
                Choice(
                    sub_cmd.help
                    or _("Run subcommand {sub_cmd.name!r}").format(sub_cmd=sub_cmd),
                    sub_cmd,
                )
            )
    click.secho(LOGO, fg='green', bold=True)
    click.secho('欢迎来到小派蒙的Nonebot CLI 插件!', fg='green', bold=True)

    try:
        result = await ListPrompt(
            '你想要进行什么操作?', choices=choices
        ).prompt_async(style=CLI_DEFAULT_STYLE)
    except CancelledError:
        ctx.exit()

    sub_cmd = result.data
    await run_sync(ctx.invoke)(sub_cmd)


from .commands import create, install, resources

paimon.add_command(create)
paimon.add_command(install)
paimon.add_command(resources)


@paimon.command(
    aliases=['show'],
    help='展示小派蒙的LOGO.'
)
def logo():
    click.secho(LOGO, fg='green', bold=True)
    click.secho('欢迎来到小派蒙的Nonebot CLI插件!', fg='green', bold=True)
