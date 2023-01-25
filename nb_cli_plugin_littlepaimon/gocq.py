import asyncio
import platform
import zipfile
from pathlib import Path

import httpx
from cpuinfo import get_cpu_info
from nb_cli.consts import WINDOWS

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


async def download_gocq(download_domain: str = 'github.com'):
    """
    下载gocq

    :param download_domain: 下载源
    """
    GOCQ_DIR.mkdir(parents=True, exist_ok=True)
    download_path = Path() / f'go-cqhttp_{GOOS}_{GOARCH}{ARCHIVE_EXT}'
    url = f'https://{download_domain}/Mrs4s/go-cqhttp/releases/latest/download/go-cqhttp_{GOOS}_{GOARCH}{ARCHIVE_EXT}'
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()

        with open(download_path, 'wb') as f:
            f.write(resp.content)

        zipf = zipfile.ZipFile(download_path)
        zipf.extractall(GOCQ_DIR)
        zipf.close()
        await asyncio.sleep(1)
        download_path.unlink()
        return GOCQ_DIR / f'go-cqhttp{EXECUTABLE_EXT}'
