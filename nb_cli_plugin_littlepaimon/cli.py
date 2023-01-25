from typing import List, cast

import click
from nb_cli import _
from nb_cli.cli import CLI_DEFAULT_STYLE, ClickAliasedGroup, run_sync, run_async
from noneprompt import Choice, ListPrompt, CancelledError

from .meta import LOGO
from .create import create
from . import __version__


@click.group(cls=ClickAliasedGroup, invoke_without_command=True, help=_('管理 LittlePaimon.'))
@click.version_option(
    __version__,
    "-V",
    "--version",
    prog_name="nb paimon",
    message="%(prog)s: Nonebot CLI plugin for LittlePaimon  version %(version)s",
)
@click.pass_context
@run_async
async def paimon(ctx: click.Context):
    """Command help."""
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
    click.secho(LOGO, fg="green", bold=True)
    click.secho(_("Welcome to Nonebot CLI plugin for LittlePaimon!"), fg="green", bold=True)

    try:
        result = await ListPrompt(
            _("What do you want to do?"), choices=choices
        ).prompt_async(style=CLI_DEFAULT_STYLE)
    except CancelledError:
        ctx.exit()

    sub_cmd = result.data
    await run_sync(ctx.invoke)(sub_cmd)


paimon.add_command(create)


@paimon.command()
def logo():
    """展示LOGO"""
    click.secho(LOGO, fg="green", bold=True)
    click.secho(_("Welcome to LittlePaimon CLI!"), fg="green", bold=True)


@paimon.command()
def more():
    """开发中"""
    click.secho('更多功能正在开发中...', fg='green')
