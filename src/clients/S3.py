from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from aiobotocore.client import AioBaseClient

from common.settings import settings


class S3Client:
    def __init__(self, access_key: str, secret_key: str, endpoint_url: str, bucket_name: str):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self) -> AioBaseClient:
        async with self.session.create_client("s3", **self.config, verify=False) as client:
            yield client

    async def upload_file(self, file: bytes, filename: str) -> None:
        async with self.get_client() as client:
            await client.put_object(Bucket=self.bucket_name, Key=filename, Body=file)


s3_client = S3Client(
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    endpoint_url=settings.S3_URL,
    bucket_name=settings.S3_BUCKET_NAME,
)
