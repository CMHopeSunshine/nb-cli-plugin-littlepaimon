import hashlib
from pathlib import Path
from typing import Optional
import zipfile

from ..handlers import download_json, download_with_bar

import click
from nb_cli.cli import CLI_DEFAULT_STYLE, ClickAliasedCommand, run_async
from noneprompt import (
    CancelledError,
    CheckboxPrompt,
    Choice,
    ConfirmPrompt,
    ListPrompt,
)
from rich.console import Console

console = Console()


@click.command(
    cls=ClickAliasedCommand,
    aliases=["res"],
    context_settings={"ignore_unknown_options": True},
    help="下载或更新小派蒙资源.",
)
@click.option(
    "-f",
    "--force",
    default=False,
    is_flag=True,
    help="是否强制下载资源，不管是否在小派蒙目录中.",
)
@click.option(
    "-u",
    "--url",
    "only_url",
    default=False,
    is_flag=True,
    help="是否只展示下载链接而不进行下载.",
)
@click.pass_context
@run_async
async def resources(
    ctx: click.Context,
    force: Optional[bool] = False,
    only_url: Optional[bool] = False,
):
    if only_url:
        click.secho(
            "小派蒙基础必需资源:"
            " https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimonRes/main/resources.zip",
            fg="yellow",
        )
        # click.secho(
        #     '原神数据信息: https://raw.githubusercontent.com/CMHopeSunshine/GenshinWikiMap/master/data/data.zip',
        #     fg='yellow')
        click.secho(
            "原神图标资源:"
            " https://raw.githubusercontent.com/CMHopeSunshine/GenshinWikiMap/master/resources/genshin_resources.zip",
            fg="yellow",
        )
        click.secho(
            "原神图标资源:"
            " https://raw.githubusercontent.com/CMHopeSunshine/GenshinWikiMap/master/resources/genshin_splash.zip",
            fg="yellow",
        )
        click.secho("如有需要请自行下载!", fg="yellow")
        ctx.exit()
    cwd_path = Path()
    if not force and not (
        (cwd_path / "LittlePaimon").is_dir() and (cwd_path / "pyproject.toml").is_file()
    ):
        click.secho("未检测到当前文件夹有小派蒙项目", fg="red")
        ctx.exit()
    try:
        confirm = False
        res_type = []
        while not confirm:
            res_type = await CheckboxPrompt(
                "你要下载(更新)哪些资源?",
                [
                    Choice("小派蒙基础必需资源", "base"),
                    # Choice('原神数据信息', 'data'),
                    Choice("原神图标资源", "icon"),
                    Choice("原神立绘资源", "splash"),
                ],
                default_select=[0, 1, 2],
            ).prompt_async(style=CLI_DEFAULT_STYLE)
            confirm = (
                True
                if res_type
                else await ConfirmPrompt(
                    "你还没选择任何资源",
                    default_choice=False,
                ).prompt_async(style=CLI_DEFAULT_STYLE)
            )
        if not (res_type := [res.data for res in res_type]):
            ctx.exit()
        download_url = await ListPrompt(
            "要使用的资源下载源?",
            [
                Choice("github官方源(国外推荐)", ""),
                Choice(
                    "cherishmoon镜像源(国内推荐)",
                    "https://github.cherishmoon.fun/",
                ),
                Choice("ghproxy镜像源(国内备选)", "https://ghproxy.com/"),
            ],
            default_select=1,
        ).prompt_async(style=CLI_DEFAULT_STYLE)
        download_url = download_url.data
        if "base" in res_type:
            resources_path = cwd_path / "resources"
            resources_path.mkdir(exist_ok=True, parents=True)
            base_zip_path = cwd_path / "base.zip"
            if not force and (
                (resources_path / "fonts").is_dir()
                and (resources_path / "LittlePaimon").is_dir()
                and len(list((resources_path / "LittlePaimon").rglob("*"))) >= 50
            ):
                click.secho("检测到已有部分基础资源，进行增量更新...", fg="yellow")
                base_resources_list = download_json(
                    f"{download_url}https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimonRes/main/resources_list.json",
                )
                for resource in base_resources_list:
                    file_path = resources_path / resource["path"]
                    if file_path.exists():
                        if (
                            not resource["lock"]
                            or hashlib.md5(file_path.read_bytes()).hexdigest()
                            == resource["hash"]
                        ):
                            continue
                        file_path.unlink()
                    try:
                        download_with_bar(
                            url=f'{download_url}https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimonRes/main/{resource["path"]}',
                            save_path=file_path,
                            show_name="基础资源" + resource["path"],
                        )
                    except CancelledError as e:
                        raise e
                    except Exception as e:
                        click.secho(
                            f'下载基础资源{resource["path"]}出错: {e}',
                            fg="red",
                        )
            else:
                try:
                    download_with_bar(
                        f"{download_url}https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimonRes/main/resources.zip",
                        base_zip_path,
                        "小派蒙基础资源",
                    )
                    with console.status("[bold yellow]解压小派蒙基础资源中..."):
                        zipfile.ZipFile(base_zip_path).extractall(
                            resources_path,
                        )
                except CancelledError as e:
                    raise e
                except Exception as e:
                    click.secho(f"下载小派蒙基础资源时出错: {e}", fg="red")
                if base_zip_path.is_file():
                    base_zip_path.unlink()

        if "data" in res_type:
            data_path = cwd_path / "data" / "LittlePaimon" / "genshin_data"
            data_path.mkdir(exist_ok=True, parents=True)
            data_zip_path = cwd_path / "data.zip"
            try:
                download_with_bar(
                    f"{download_url}https://github.com/CMHopeSunshine/GenshinWikiMap/raw/master/data/data.zip",
                    data_zip_path,
                    "原神数据信息",
                )
                with console.status("[bold yellow]解压原神数据资源中..."):
                    zipfile.ZipFile(data_zip_path).extractall(data_path)
            except CancelledError as e:
                raise e
            except Exception as e:
                click.secho(f"下载原神数据信息时出错: {e}", fg="red")
            if data_zip_path.is_file():
                data_zip_path.unlink()
        if "icon" in res_type:
            resources_path = cwd_path / "resources" / "LittlePaimon"
            resources_path.mkdir(exist_ok=True, parents=True)
            icon_zip_path = cwd_path / "icon.zip"
            try:
                download_with_bar(
                    f"{download_url}https://github.com/CMHopeSunshine/GenshinWikiMap/raw/master/resources/genshin_resources.zip",
                    icon_zip_path,
                    "原神图标资源",
                )
                with console.status("[bold yellow]解压原神图标资源中..."):
                    zipfile.ZipFile(icon_zip_path).extractall(resources_path)
            except CancelledError as e:
                raise e
            except Exception as e:
                click.secho(f"下载原神图标资源时出错: {e}", fg="red")
            if icon_zip_path.is_file():
                icon_zip_path.unlink()
        if "splash" in res_type:
            resources_path = cwd_path / "resources" / "LittlePaimon" / "splash"
            resources_path.mkdir(exist_ok=True, parents=True)
            splash_zip_path = cwd_path / "splash.zip"
            try:
                download_with_bar(
                    f"{download_url}https://github.com/CMHopeSunshine/GenshinWikiMap/raw/master/resources/genshin_splash.zip",
                    splash_zip_path,
                    "原神立绘资源",
                )
                with console.status("[bold yellow]解压原神立绘资源中..."):
                    zipfile.ZipFile(splash_zip_path).extractall(resources_path)
            except CancelledError as e:
                raise e
            except Exception as e:
                click.secho(f"下载原神立绘资源时出错: {e}", fg="red")
            if splash_zip_path.is_file():
                splash_zip_path.unlink()

        click.secho("资源更新完成", fg="green", bold=True)

    except CancelledError:
        ctx.exit()
