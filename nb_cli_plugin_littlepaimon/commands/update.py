import asyncio
from pathlib import Path

from ..handlers import git_pull

import click
from nb_cli.cli import ClickAliasedCommand, run_async
from nb_cli.handlers import (
    register_signal_handler,
    remove_signal_handler,
    terminate_process,
)


@click.command(
    cls=ClickAliasedCommand,
    aliases=["upgrade"],
    help="检测更新并更新小派蒙.",
)
@click.option("-d", "--cwd", default=".", help="指定工作目录.")
@click.pass_context
@run_async
async def update(ctx: click.Context, cwd: str):
    if not ((Path(cwd) / "LittlePaimon").is_dir() and (Path(cwd) / "bot.py").is_file()):
        click.secho("未检测到当前目录下有小派蒙项目，请确保目录无误", fg="red")
        ctx.exit()
    if not (Path(cwd) / ".git").is_dir():
        click.secho("未检测到当前目录下有git仓库，无法通过git更新", fg="red")
        ctx.exit()

    should_exit = asyncio.Event()

    def shutdown(signum, frame):
        should_exit.set()

    register_signal_handler(shutdown)

    async def wait_for_exit():
        await should_exit.wait()
        await terminate_process(proc)

    proc = await git_pull(cwd=Path(cwd))
    task = asyncio.create_task(wait_for_exit())
    await proc.wait()
    should_exit.set()
    await task
    remove_signal_handler(shutdown)
