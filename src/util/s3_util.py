from io import BytesIO
from typing import BinaryIO

from aioboto3 import Session

from config import settings


async def upload_file_obj(file: BytesIO | BinaryIO, key: str, mimetype: str):
    session = Session()

    async with session.client(
        "s3",
        endpoint_url=settings.s3.endpoint,
        aws_access_key_id=settings.s3.key_id,
        aws_secret_access_key=settings.s3.key_secret,
    ) as s3:

        await s3.upload_fileobj(
            file,
            settings.s3.bucket,
            key,
            ExtraArgs={
                "ContentType": mimetype,
            },
        )


async def delete_obj(key: str):
    session = Session()
    async with session.client(
        "s3",
        endpoint_url=settings.s3.endpoint,
        aws_access_key_id=settings.s3.key_id,
        aws_secret_access_key=settings.s3.key_secret,
    ) as s3:
        await s3.delete_object(
            Bucket=settings.s3.bucket,
            Key=key,
        )
