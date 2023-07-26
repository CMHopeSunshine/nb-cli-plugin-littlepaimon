from pathlib import Path
import signal
from threading import Event
from typing import Optional

import httpx
from noneprompt import CancelledError
import rich.progress


def download_json(url: str):
    """下载json文件

    :param url: url
    """
    return httpx.get(url=url, verify=False).json()


def download_with_bar(url: str, save_path: Path, show_name: Optional[str] = None):
    """
    下载文件(带进度条)

    :param url: url
    :param save_path: 保存路径
    :param show_name: 下载时展示的昵称
    """
    done_event = Event()

    def handle_sigint(signum, frame):
        done_event.set()

    signal.signal(signal.SIGINT, handle_sigint)

    save_path.parent.mkdir(parents=True, exist_ok=True)
    with save_path.open("wb") as f:  # noqa: SIM117
        with httpx.stream(
            method="GET",
            url=url,
            follow_redirects=True,
            verify=False,
        ) as datas:
            size = int(datas.headers["Content-Length"])
            with rich.progress.Progress(
                rich.progress.TextColumn("[bold yellow]{task.description}"),
                rich.progress.BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                "•",
                rich.progress.DownloadColumn(),
                "•",
                rich.progress.TransferSpeedColumn(),
                "•",
                rich.progress.TimeRemainingColumn(),
            ) as progress:
                download_task = progress.add_task(
                    show_name or save_path.name,
                    total=size,
                )
                for data in datas.iter_bytes():
                    f.write(data)
                    progress.update(download_task, completed=datas.num_bytes_downloaded)
                    if done_event.is_set():
                        raise CancelledError
