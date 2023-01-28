import asyncio
from pathlib import Path

import click
from nb_cli.cli import ClickAliasedCommand, run_async
from nb_cli.handlers import (
    detect_virtualenv,
    register_signal_handler,
    terminate_process,
    run_project,
    remove_signal_handler
)


@click.command(
    cls=ClickAliasedCommand, aliases=['start'], help='在当前目录下启动小派蒙Bot.'
)
@click.option("-d", "--cwd", default=".", help='指定工作目录.')
@click.pass_context
@run_async
async def run(ctx: click.Context, cwd: str):
    if not ((Path(cwd) / 'LittlePaimon').is_dir() and (Path(cwd) / 'bot.py').is_file()):
        click.secho('未检测到当前目录下有小派蒙项目，请确保目录无误', fg='red')
        ctx.exit()
    python_path = detect_virtualenv(Path(cwd))
    should_exit = asyncio.Event()

    def shutdown(signum, frame):
        should_exit.set()

    register_signal_handler(shutdown)

    async def wait_for_exit():
        await should_exit.wait()
        await terminate_process(proc)

    proc = await run_project(python_path=python_path, cwd=Path(cwd))
    task = asyncio.create_task(wait_for_exit())
    await proc.wait()
    should_exit.set()
    await task
    remove_signal_handler(shutdown)
