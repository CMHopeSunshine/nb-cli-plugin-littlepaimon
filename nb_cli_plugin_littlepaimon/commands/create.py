import asyncio
import os
import shutil
import stat
from pathlib import Path
from typing import Optional

import click
from nb_cli.cli import ClickAliasedCommand, run_async, CLI_DEFAULT_STYLE
from nb_cli.cli.commands.project import project_name_validator
from nb_cli.consts import WINDOWS
from nb_cli.handlers import create_virtualenv, call_pip_install
from noneprompt import Choice, ListPrompt, CancelledError, ConfirmPrompt, InputPrompt

from ..handlers.cmd import check_git, clone_paimon, install_dependencies
from ..handlers.gocq import download_gocq, EXECUTABLE_EXT
from ..meta import LOGO


@click.command(
    cls=ClickAliasedCommand,
    aliases=['new', 'init'],
    context_settings={'ignore_unknown_options': True},
    help='在当前目录下安装小派蒙以及go-cqhttp.',
)
@click.option(
    '-p',
    '--python-interpreter',
    default=None,
    help='指定Python解释器的路径',
)
@click.option('-i',
              '--index-url',
              'index_url',
              default=None,
              help='pip下载所使用的镜像源')
@click.pass_context
@run_async
async def create(ctx: click.Context,
                 python_interpreter: Optional[str],
                 index_url: Optional[str]):
    """在当前目录下安装小派蒙以及go-cqhttp."""
    click.clear()
    click.secho(LOGO, fg='green', bold=True)

    click.secho('检查前置环境...', fg='yellow')
    if not await check_git():
        click.secho('[Git]未安装，请先自行安装Git', fg='red')
        ctx.exit()
    else:
        click.secho('开始安装小派蒙...', fg='yellow')
    try:
        is_clone = False
        while True:
            # 项目名称
            project_name = await InputPrompt(
                '项目名称:',
                default_text='LittlePaimon',
                validator=project_name_validator
            ).prompt_async(style=CLI_DEFAULT_STYLE)
            project_name = project_name.replace(' ', '-')

            # 检查项目是否存在
            if (Path('.') / project_name).is_dir():
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

                    shutil.rmtree((Path('.') / project_name).absolute(), onerror=delete)
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
                 Choice('cherishmoon镜像源(国内备选1)',
                        'https://github.cherishmoon.fun/https://github.com/CMHopeSunshine/LittlePaimon'),
                 Choice('gitee镜像源(国内备选2)', 'https://gitee.com/cherishmoon/LittlePaimon')],
                default_select=1
            ).prompt_async(style=CLI_DEFAULT_STYLE)
            click.secho(f'在 {project_name} 文件夹克隆源码...', fg='yellow')
            clone_result = await clone_paimon(git_url.data, project_name)
            await clone_result.wait()

            env_file = (Path('.') / project_name / '.env.prod').read_text(encoding='utf-8')
            superusers = await InputPrompt(
                '超级用户QQ(即你自己的QQ号，多个用空格隔开):',
                validator=lambda x: x.replace(' ', '').isdigit(),
            ).prompt_async(style=CLI_DEFAULT_STYLE)
            if superusers := superusers.replace(' ', '", "'):
                env_file = env_file.replace('SUPERUSERS=["123456"]', f'SUPERUSERS=["{superusers}"]')
            (Path('.') / project_name / '.env.prod').write_text(env_file, encoding='utf-8')

        is_install_dependencies = await ConfirmPrompt(
            '立刻安装依赖?', default_choice=True
        ).prompt_async(style=CLI_DEFAULT_STYLE)
        venv_dir = Path('.') / project_name / '.venv'

        python_path = None
        if is_install_dependencies:
            is_use_venv = await ConfirmPrompt(
                '创建虚拟环境?', default_choice=True
            ).prompt_async(style=CLI_DEFAULT_STYLE)

            python_path = None
            if is_use_venv:
                click.secho(
                    f'在 {venv_dir} 中创建虚拟环境...',
                    fg='yellow',
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
            await install_dependencies(file_path=Path('.') / project_name / 'requirements.txt',
                                       python_path=python_path,
                                       pip_args=['-i', index_url] if index_url else None)

        # go-cqhttp
        gocq_type = 0
        if (Path('.') / 'go-cqhttp' / f'go-cqhttp{EXECUTABLE_EXT}').exists():
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
                toml_file = (Path('.') / project_name / 'pyproject.toml').read_text(encoding='utf-8')
                toml_file = toml_file.replace('plugins = []', 'plugins = ["nonebot_plugin_gocqhttp"]')
                (Path('.') / project_name / 'pyproject.toml').write_text(toml_file, encoding='utf-8')
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
                    gocq_path = download_gocq(gocq_download_domain.data)
                except Exception as e:
                    click.secho(f'下载go-cqhttp失败: {e}', fg='red')
                if gocq_path and gocq_path.exists():
                    gocq_type = 2
                    bot_qq = await InputPrompt(
                        '机器人的QQ号:',
                        validator=lambda x: x.isdigit(),
                    ).prompt_async(style=CLI_DEFAULT_STYLE)
                    password = await InputPrompt(
                        '机器人的密码(留空则为扫码登录):',
                        is_password=True
                    ).prompt_async(style=CLI_DEFAULT_STYLE)
                    config_data = (
                        (Path(__file__).parent.parent / 'config_template.yml').read_text(encoding='utf-8')
                        .replace('{{ qq }}', bot_qq)
                        .replace('{{ password }}', password)
                    )
                    (Path('.') / 'go-cqhttp' / 'config.yml').write_text(config_data, encoding='utf-8')
                else:
                    click.secho('go-cqhttp安装失败, 请稍后手动安装', fg='red')
        click.secho('安装完成!', fg='green')
        click.secho('运行以下命令来启动你的小派蒙:', fg='green')
        if gocq_type == 2:
            if WINDOWS:
                click.secho(f'  cd {project_name}', fg='green')
                click.secho('  nb run', fg='green')
                click.secho('  双击运行go-cqhttp文件夹下的go-cqhttp.exe', fg='green')
                click.secho('  两个窗口都不能关闭!!!', fg='green')
            else:
                click.secho('  cd go-cqhttp', fg='green')
                click.secho('  chmod 755 go-cqhttp (仅首次需要)', fg='green')
                click.secho('  nohup ./go-cqhttp &', fg='green')
                click.secho(f'  cd ../{project_name}', fg='green')
                click.secho('  nb run', fg='green')
        else:
            click.secho(f'  cd {project_name}', fg='green')
            if not is_install_dependencies:
                click.secho('  使用你自己的依赖管理器来安装依赖', fg='green')
            click.secho('  nb run', fg='green')
            if gocq_type == 1:
                click.secho('  访问http://127.0.0.1:13579/go-cqhttp登录账号')
        click.secho('开始享用小派蒙吧!', fg='green')

    except CancelledError:
        ctx.exit()
