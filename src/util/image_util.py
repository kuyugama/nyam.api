import secrets
from io import BytesIO
from typing import BinaryIO
from tempfile import TemporaryFile

import puremagic
from PIL import Image
from aiohttp import ClientSession

from config import settings

MB = 1024 * 1024


def file_size(file: BinaryIO) -> int:
    total_bytes = 0

    while read := len(file.read(1024)):
        total_bytes += read

    file.seek(0)

    return total_bytes


def filter_image_size(
    file: BinaryIO, max_width: int, max_height: int, image: bool = False
) -> BytesIO | BinaryIO | Image.Image:
    img = Image.open(file)
    image_format = img.format

    resize = False
    resize_to = img.size

    if img.width > max_width:
        resize = True
        resize_to = (max_width, resize_to[1])

    if img.height > max_height:
        resize = True
        resize_to = (resize_to[0], max_height)

    if resize:
        img = img.resize(resize_to)

    if image:
        return img

    if not resize:
        return file

    io = BytesIO()
    img.save(io, image_format, optimize=True)
    io.seek(0)

    return io


def compress_png(file: BinaryIO, max_width: int, max_height: int) -> BytesIO:
    img = filter_image_size(file, max_width, max_height, True)

    io = BytesIO()
    io.name = secrets.token_hex(8) + ".webp"

    if file_size(file) > 0.5 * MB:
        img.save(io, quality=85, optimize=True)
        io.seek(0)
        return io

    img.save(io, quality=95, optimize=True)
    io.seek(0)
    return io


async def web_image_metadata(url: str, client: ClientSession = None) -> dict[str, str | int] | None:
    if client is None:
        client = ClientSession()

    with TemporaryFile("w+b") as file:
        async with client:
            resp = await client.get(url, headers=settings.bot.headers)

            if resp.status != 200:
                return None

            while (data := await resp.content.read(4096)) != b"":
                file.write(data)

        file.seek(0)
        width, height = Image.open(file).size
        file.seek(0)
        mime = puremagic.from_stream(file, mime=True)

        return {"width": width, "height": height, "mimetype": mime, "url": url}
