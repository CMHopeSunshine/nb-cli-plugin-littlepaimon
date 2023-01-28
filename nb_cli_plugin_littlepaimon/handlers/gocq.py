import asyncio
import platform
import zipfile
from pathlib import Path

from cpuinfo import get_cpu_info
from nb_cli.consts import WINDOWS

from .download import download_with_bar

_SYSTEM_MAP = {
    "Windows": "windows",
    "Linux":   "linux",
    "Darwin":  "darwin",
}

_ARCHITECTURE_MAP = {
    "X86_32": "386",
    "X86_64": "amd64",
    "ARM_7":  "armv7",
    "ARM_8":  "arm64",
}


def _get_platform():
    """
    获取系统和架构

    :return: 系统和架构的元组。
    """
    try:
        system = _SYSTEM_MAP[platform.system()]
        architecture = _ARCHITECTURE_MAP[get_cpu_info()["arch"]]
    except KeyError:
        raise RuntimeError(f"Unsupported platform: {platform.uname()!r}") from None
    return system, architecture


GOOS, GOARCH = _get_platform()

ARCHIVE_EXT = ".zip" if WINDOWS else ".tar.gz"
EXECUTABLE_EXT = ".exe" if WINDOWS else ""

GOCQ_DIR = Path() / "go-cqhttp"


def download_gocq(download_domain: str = 'github.com'):
    """
    下载gocq

    :param download_domain: 下载源
    """
    GOCQ_DIR.mkdir(parents=True, exist_ok=True)
    download_path = Path() / f'go-cqhttp_{GOOS}_{GOARCH}{ARCHIVE_EXT}'
    url = f'https://{download_domain}/Mrs4s/go-cqhttp/releases/latest/download/go-cqhttp_{GOOS}_{GOARCH}{ARCHIVE_EXT}'
    download_with_bar(url=url, save_path=download_path, show_name=f'go-cqhttp_{GOOS}_{GOARCH}{ARCHIVE_EXT}')
    with zipfile.ZipFile(download_path, 'r') as z:
        z.extractall(GOCQ_DIR)
    download_path.unlink()
    return GOCQ_DIR / f'go-cqhttp{EXECUTABLE_EXT}'
