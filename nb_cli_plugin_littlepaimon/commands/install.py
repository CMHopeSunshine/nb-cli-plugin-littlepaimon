from pathlib import Path
from typing import Optional, List

import click
from nb_cli.cli import run_async, ClickAliasedCommand
from nb_cli.handlers import detect_virtualenv, call_pip_install

from ..handlers.cmd import install_dependencies


@click.command(
    cls=ClickAliasedCommand,
    aliases=['add'],
    context_settings={"ignore_unknown_options": True},
    help='安装依赖库到小派蒙项目中.'
)
@click.argument('name',
                nargs=-1,
                required=False,
                default=None)
@click.option('-f',
              '--file',
              default='requirements.txt',
              type=click.Path(exists=True),
              help='指定依赖文件的路径')
@click.option('-i',
              '--index-url',
              'index_url',
              default=None,
              help='pip下载所使用的镜像源')
@click.pass_context
@run_async
async def install(
        ctx: click.Context, name: Optional[List[str]], file: Path, index_url: Optional[str]):
    file_path = Path(file).absolute()
    python_path = detect_virtualenv()
    proc = (
        await call_pip_install(
            name, pip_args=['-i', index_url], python_path=python_path
        )
        if name
        else await install_dependencies(file_path=file_path,
                                        python_path=python_path,
                                        pip_args=['-i', index_url] if index_url else None
                                        )
    )
    await proc.wait()
