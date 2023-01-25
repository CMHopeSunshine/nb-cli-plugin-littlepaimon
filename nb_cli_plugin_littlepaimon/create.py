import asyncio
import os
import shutil
import stat
from pathlib import Path
from typing import Optional

import click
from nb_cli import _
from nb_cli.cli import ClickAliasedCommand, run_async, CLI_DEFAULT_STYLE
from nb_cli.consts import WINDOWS
from nb_cli.handlers import create_virtualenv, call_pip_install
from nb_cli.cli.commands.project import project_name_validator
from noneprompt import Choice, ListPrompt, CancelledError, ConfirmPrompt, InputPrompt

from .handler import check_git, clone_paimon, install_dependencies
from .meta import LOGO
from .gocq import download_gocq, EXECUTABLE_EXT


@click.command(
    cls=ClickAliasedCommand,
    aliases=["new", "init"],
    context_settings={"ignore_unknown_options": True},
    help="安装派蒙",
)
@click.option(
    "-p",
    "--python-interpreter",
    default=None,
    help=_("The python interpreter virtualenv is installed into."),
)
@click.pass_context
@run_async
async def create(ctx: click.Context,
                 python_interpreter: Optional[str]):
    """安装小派蒙."""
    click.clear()
    click.secho(LOGO, fg="green", bold=True)

    click.secho('检查git...', fg='yellow')
    if not await check_git():
        click.secho('git未安装，请先自行安装git', fg='red')
        ctx.exit()
    else:
        click.secho('git已安装', fg='green')
        click.secho('开始安装小派蒙...', fg='yellow')
    try:
        is_clone = False
        while True:
            # 项目名称
            project_name = await InputPrompt(
                _("Project Name:"),
                default_text='LittlePaimon',
                validator=project_name_validator
            ).prompt_async(style=CLI_DEFAULT_STYLE)
            project_name = project_name.replace(' ', '-')

            # 检查项目是否存在
            if (Path() / project_name).is_dir():
                dir_choice = await ListPrompt(
                    '当前目录下已存在同名项目文件夹，如何操作?',
                    [
                        Choice('删除该文件夹并重新克隆', 'delete'),
                        Choice('使用该文件夹中的内容并继续', 'use'),
                        Choice('重新命名', 'rename'),
                        Choice('取消安装', 'exit'),
                    ],
                    default_select=0
                ).prompt_async(style=CLI_DEFAULT_STYLE)
                if dir_choice.data == 'rename':
                    pass
                elif dir_choice.data == 'delete':

                    def delete(func, path_, execinfo):
                        os.chmod(path_, stat.S_IWUSR)
                        func(path_)

                    shutil.rmtree(Path() / project_name, onerror=delete)
                    await asyncio.sleep(0.2)
                    break
                elif dir_choice.data == 'use':
                    is_clone = True
                    break
                else:
                    ctx.exit()
            else:
                break

        if not is_clone:
            git_url = await ListPrompt(
                '要使用的克隆源?',
                [Choice('github官方源(国外推荐)', 'https://github.com/CMHopeSunshine/LittlePaimon'),
                 Choice('ghproxy镜像源(国内推荐)',
                        'https://ghproxy.com/https://github.com/CMHopeSunshine/LittlePaimon'),
                 Choice('cherishmoon镜像源(国内备选)',
                        'https://github.cherishmoon.fun/https://github.com/CMHopeSunshine/LittlePaimon'),
                 Choice('gitee镜像源(国内备选)', 'https://gitee.com/cherishmoon/LittlePaimon')],
                default_select=1
            ).prompt_async(style=CLI_DEFAULT_STYLE)
            click.secho(f'在 {project_name} 文件夹克隆源码...', fg='yellow')
            clone_result = await clone_paimon(git_url.data, project_name)
            await clone_result.wait()

            env_file = (Path() / project_name / '.env.prod').read_text(encoding='utf-8')
            bot_name = await InputPrompt(
                _("填写机器人的昵称(多个用空格隔开):"),
                default_text='派蒙',
            ).prompt_async(style=CLI_DEFAULT_STYLE)
            if bot_name := bot_name.replace(' ', '", "'):
                env_file = env_file.replace('NICKNAME=["派蒙", "bot"]', f'NICKNAME=["{bot_name}"]')

            superusers = await InputPrompt(
                _("填写超级用户(即你自己的QQ号，多个用空格隔开):"),
                validator=lambda x: x.replace(' ', '').isdigit(),
            ).prompt_async(style=CLI_DEFAULT_STYLE)
            if superusers := superusers.replace(' ', '", "'):
                env_file = env_file.replace('SUPERUSERS=["123456"]', f'SUPERUSERS=["{superusers}"]')

            (Path() / project_name / '.env.prod').write_text(env_file, encoding='utf-8')

        is_install_dependencies = await ConfirmPrompt(
            _("Install dependencies now?"), default_choice=True
        ).prompt_async(style=CLI_DEFAULT_STYLE)
        venv_dir = Path() / project_name / '.venv'

        python_path = None
        if is_install_dependencies:
            is_use_venv = await ConfirmPrompt(
                _("Create virtual environment?"), default_choice=True
            ).prompt_async(style=CLI_DEFAULT_STYLE)

            python_path = None
            if is_use_venv:
                click.secho(
                    _("Creating virtual environment in {venv_dir} ...").format(
                        venv_dir=venv_dir
                    ),
                    fg="yellow",
                )
                await create_virtualenv(
                    venv_dir, prompt=project_name, python_path=python_interpreter
                )
                python_path = (
                        venv_dir
                        / ("Scripts" if WINDOWS else "bin")
                        / ("python.exe" if WINDOWS else "python")
                )

            click.secho('开始安装相关依赖...', fg='yellow')
            await install_dependencies(python_path, project_name)

        # go-cqhttp
        gocq_type = 0
        if (Path() / 'go-cqhttp' / f'go-cqhttp{EXECUTABLE_EXT}').exists():
            click.secho('检测到当前目录下已有go-cqhttp本体，跳过安装go-cqhttp', fg='yellow')
        else:
            install_gocq_type = await ListPrompt(
                'go-cqhttp安装和使用方式?',
                [Choice('nonebot-plugin-gocqhttp插件', 'plugin'),
                 Choice('go-cqhttp本体', 'gocq'),
                 Choice('我已安装或稍候自行安装', 'skip')],
                default_select=0).prompt_async(style=CLI_DEFAULT_STYLE)

            if install_gocq_type.data == 'plugin':
                gocq_type = 1
                proc = await call_pip_install('nonebot-plugin-gocqhttp', python_path=python_path)
                await proc.wait()
                toml_file = (Path() / project_name / 'pyproject.toml').read_text(encoding='utf-8')
                toml_file = toml_file.replace('plugins = []', 'plugins = ["nonebot_plugin_gocqhttp"]')
                (Path() / project_name / 'pyproject.toml').write_text(toml_file, encoding='utf-8')
            elif install_gocq_type.data == 'gocq':
                gocq_download_domain = await ListPrompt(
                    '要使用的go-cqhttp下载源?',
                    [Choice('Github官方源(国外推荐)', 'github.com'),
                     Choice('FastGit镜像源(国内推荐)', 'download.fgit.ml')],
                    default_select=1
                ).prompt_async(style=CLI_DEFAULT_STYLE)
                gocq_path = None
                try:
                    click.secho('下载go-cqhttp中...', fg='yellow')
                    gocq_path = await download_gocq(gocq_download_domain.data)
                except Exception as e:
                    click.secho(f'下载go-cqhttp失败: {e}', fg='red')
                if gocq_path and gocq_path.exists():
                    gocq_type = 2
                    config_raw_file = Path(__file__).parent / 'config.yml'
                    config_file = Path() / 'go-cqhttp' / 'config.yml'
                    bot_qq = await InputPrompt(
                        _("填写机器人的QQ号:"),
                        validator=lambda x: x.isdigit(),
                    ).prompt_async(style=CLI_DEFAULT_STYLE)
                    password = await InputPrompt(
                        _("填写机器人的密码(留空则为扫码登录):"),
                        is_password=True
                    ).prompt_async(style=CLI_DEFAULT_STYLE)
                    config_data = config_raw_file.read_text(encoding='utf-8')
                    config_data = config_data.replace('{{ qq }}', bot_qq).replace('{{ password }}', password)
                    config_file.write_text(config_data, encoding='utf-8')
                else:
                    click.secho('go-cqhttp安装失败, 请稍后手动安装', fg='red')
            else:
                pass
        click.secho('安装完成!', fg="green")
        click.secho('运行以下命令来启动你的小派蒙:', fg='green')
        if gocq_type == 2:
            if WINDOWS:
                click.secho(f'  cd {project_name}', fg='green')
                click.secho(f'  nb run', fg='green')
                click.secho('  双击运行go-cqhttp/go-cqhttp.exe', fg='green')
                click.secho('  两个窗口都不能关闭!!!', fg='green')
            else:
                click.secho('  cd go-cqhttp', fg='green')
                click.secho('  chmod 755 go-cqhttp (仅首次需要)', fg='green')
                click.secho('  nohup ./go-cqhttp &', fg='green')
                click.secho(f'  cd ../{project_name}', fg='green')
                click.secho(f'  nb run', fg='green')
        else:
            click.secho(f'  cd {project_name}', fg='green')
            if not is_install_dependencies:
                click.secho(f'  使用你自己的依赖管理器来安装依赖', fg='green')
            click.secho(f'  nb run', fg='green')
            if gocq_type == 1:
                click.secho('  访问http://127.0.0.1:13579/go-cqhttp登录账号')
        click.secho(f'开始享用小派蒙吧!', fg='green')


    except CancelledError:
        ctx.exit()
