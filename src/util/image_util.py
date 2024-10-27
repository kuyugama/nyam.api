import secrets
from io import BytesIO
from typing import BinaryIO

from PIL import Image

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
