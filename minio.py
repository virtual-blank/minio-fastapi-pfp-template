from typing import Optional

import aioboto3
from botocore.exceptions import ClientError
from uuid6 import uuid7

from backend.src.config import get_minio_settings # import settings


MINIO_ENDPOINT = "http://127.0.0.1:9000"
BUCKET_NAME = get_minio_settings().bucket_name
ACCESS_KEY = get_minio_settings().root_user
SECRET_KEY = get_minio_settings().root_password


class MinioService:
    def __init__(self):
        self.session = aioboto3.Session(
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name="us-east-1",
        )
        self.endpoint_url = MINIO_ENDPOINT
        self.bucket_name = BUCKET_NAME

    def _get_client(self):
        return self.session.client("s3", endpoint_url=self.endpoint_url)

    async def upload_pfp(
        self, file_bytes: bytes, extension: str = "webp"
    ) -> Optional[str]:
        unique_filename = f"{uuid7().hex}.{extension}"
        file_key = f"pfp/{unique_filename}"

        try:
            async with self._get_client() as s3_client:
                await s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=file_key,
                    Body=file_bytes,
                    ContentType=f"image/{extension}",
                )
                public_url = f"{self.endpoint_url}/{self.bucket_name}/{file_key}"
                return public_url
        except ClientError as e:
            print(f"S3 Upload Error: {str(e)}")
            return None
        except Exception as e:
            print(f"S3 Unexpected Error While Upload {file_key}: {str(e)}")

    async def delete_avatar(self, file_url: str) -> bool:
        try:
            file_key = file_url.split(f"/{self.bucket_name}/")[-1]

            async with self._get_client() as s3_client:
                await s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
                print(f"[+] S3 successfully deleted {file_key}")
                return True
        except ClientError as e:
            print(f"S3 Delete Error: {str(e)}")
            return False
        except Exception as e:
            print(f"S3 Unexpected Error While Delete {file_url}: {str(e)}")


minio_service = MinioService()
