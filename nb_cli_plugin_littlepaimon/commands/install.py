from pathlib import Path
from typing import List, Optional

from ..handlers.cmd import install_dependencies

import click
from nb_cli.cli import ClickAliasedCommand, run_async
from nb_cli.handlers import call_pip_install, detect_virtualenv


@click.command(
    cls=ClickAliasedCommand,
    aliases=["add"],
    context_settings={"ignore_unknown_options": True},
    help="安装依赖库到小派蒙中.",
)
@click.argument("name", nargs=-1, required=False, default=None)
@click.option(
    "-f",
    "--file",
    default="requirements.txt",
    type=click.Path(exists=True),
    help="指定依赖文件的路径",
)
@click.option(
    "-i",
    "--index-url",
    "index_url",
    default=None,
    help="pip下载所使用的镜像源",
)
@click.pass_context
@run_async
async def install(
    ctx: click.Context,
    name: Optional[List[str]],
    file: Path,
    index_url: Optional[str],
):
    file_path = Path(file).absolute()
    if not (
        (file_path.parent / "LittlePaimon").is_dir()
        and (file_path.parent / "bot.py").is_file()
    ):
        click.secho("未检测到当前目录下有小派蒙项目，请确保目录无误", fg="red")
        ctx.exit()
    if python_path := detect_virtualenv(file_path.parent):
        click.secho(f"使用虚拟环境: {python_path}", fg="green")
    proc = (
        await call_pip_install(
            name,
            python_path=python_path,
            pip_args=["-i", index_url] if index_url else None,
        )
        if name
        else await install_dependencies(
            file_path=file_path,
            python_path=python_path,
            pip_args=["-i", index_url] if index_url else None,
        )
    )
    await proc.wait()
