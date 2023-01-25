import asyncio
from pathlib import Path
from typing import Optional


async def clone_paimon(git_url: str, dir_name: Optional[str] = 'LittlePaimon'):
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


async def install_dependencies(python_path: Optional[str] = None,
                               dir_name: Optional[str] = 'LittlePaimon'):
    """
    安装requirements.txt中的依赖

    :param python_path: python解释器路径
    :param dir_name: 项目路径
    """
    proc = await asyncio.create_subprocess_exec(python_path,
                                                '-m',
                                                'pip',
                                                'install',
                                                '-r',
                                                'requirements.txt',
                                                cwd=Path() / dir_name)
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

