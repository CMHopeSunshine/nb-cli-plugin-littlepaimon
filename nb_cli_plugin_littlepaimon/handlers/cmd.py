import asyncio
from pathlib import Path
from typing import Optional, List

from nb_cli.handlers import get_default_python


async def clone_paimon(git_url: str,
                       dir_name: Optional[str] = 'LittlePaimon'):
    """
    克隆派蒙项目

    :param git_url: git仓库地址
    :param dir_name: 要存放的文件夹名
    """
    process = await asyncio.create_subprocess_exec('git',
                                                   'clone',
                                                   '--depth=1',
                                                   '--single-branch',
                                                   git_url,
                                                   dir_name)
    stdout, _ = await process.communicate()
    return process


async def install_dependencies(file_path: Path,
                               python_path: Optional[str] = None,
                               pip_args: Optional[List[str]] = None):
    """
    安装requirements.txt中的依赖

    :param file_path: 依赖库文件路径
    :param python_path: python解释器路径
    :param pip_args: pip参数
    """
    if pip_args is None:
        pip_args = []
    if python_path is None:
        python_path = await get_default_python()
    if isinstance(python_path, Path):
        python_path = python_path.absolute()
    proc = await asyncio.create_subprocess_exec(python_path,
                                                '-m',
                                                'pip',
                                                'install',
                                                '-r',
                                                file_path.name,
                                                *pip_args,
                                                cwd=file_path.parent.absolute())
    stdout, _ = await proc.communicate()
    return proc


async def check_git() -> bool:
    """
    检查环境变量中是否存在 git

    :return: 布尔值
    """
    process = await asyncio.create_subprocess_shell('git --version',
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
    stdout, _ = await process.communicate()
    return bool(stdout)

