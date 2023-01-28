import math
from pathlib import Path
from typing import Optional

import httpx
from tqdm import tqdm


def download_json(url: str):
    """下载json文件

    :param url: url
    """
    return httpx.get(url=url, verify=False).json()


def download_with_bar(url: str,
                      save_path: Path,
                      show_name: Optional[str] = None):
    """
    下载文件(带进度条)

    :param url: url
    :param save_path: 保存路径
    :param show_name: 下载时展示的昵称
    """
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream(method='GET', url=url, follow_redirects=True, verify=False) as datas:
        size = math.ceil(int(datas.headers['Content-Length']) / 1024)
        with save_path.open('wb') as f:
            for data in tqdm(iterable=datas.iter_bytes(1024),
                             desc=show_name or save_path.name,
                             unit='KB',
                             total=size,
                             colour='green'):
                f.write(data)
