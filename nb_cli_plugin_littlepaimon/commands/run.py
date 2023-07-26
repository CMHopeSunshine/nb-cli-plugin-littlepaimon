import asyncio
from pathlib import Path
from typing import List, Optional

from ..handlers import run_python_command

import click
from nb_cli.cli import ClickAliasedCommand, run_async
from nb_cli.handlers import (
    detect_virtualenv,
    register_signal_handler,
    remove_signal_handler,
    run_project,
    terminate_process,
)


@click.command(
    cls=ClickAliasedCommand,
    aliases=["start"],
    context_settings={"ignore_unknown_options": True},
    help="运行命令或启动小派蒙Bot.",
)
@click.option("-d", "--cwd", default=".", help="指定工作目录.")
@click.argument("command", nargs=-1, required=False, default=None)
@click.pass_context
@run_async
async def run(ctx: click.Context, command: Optional[List[str]], cwd: str):
    if not ((Path(cwd) / "LittlePaimon").is_dir() and (Path(cwd) / "bot.py").is_file()):
        click.secho("未检测到该目录下有小派蒙项目，请确保目录无误", fg="red")
        ctx.exit()

    if python_path := detect_virtualenv(Path(cwd)):
        click.secho(f"使用虚拟环境: {python_path}", fg="green")
    should_exit = asyncio.Event()

    def shutdown(signum, frame):
        should_exit.set()

    register_signal_handler(shutdown)

    async def wait_for_exit():
        await should_exit.wait()
        await terminate_process(proc)

    if command:
        proc = await run_python_command(
            command=command,
            python_path=python_path,
            cwd=Path(cwd),
        )
    else:
        proc = await run_project(python_path=python_path, cwd=Path(cwd))
    task = asyncio.create_task(wait_for_exit())
    await proc.wait()
    should_exit.set()
    await task
    remove_signal_handler(shutdown)
