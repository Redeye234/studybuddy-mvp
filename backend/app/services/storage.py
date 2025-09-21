import boto3
from botocore.client import Config
from ..config import settings
from typing import BinaryIO, Union
import os



def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
        region_name=settings.S3_REGION,
        config=Config(signature_version="s3v4"),
    )


def upload_file(fileobj: Union[BinaryIO, bytes], key: str, content_type: str = "application/octet-stream") -> str:
    client = s3_client()
    body = fileobj if isinstance(fileobj, (bytes, bytearray)) else fileobj.read()
    client.put_object(Bucket=settings.S3_BUCKET, Key=key, Body=body, ContentType=content_type)
    return f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{key}"


def key_from_url(url: str) -> str:
    # Expecting format like http://endpoint/bucket/key or s3://bucket/key
    if url.startswith("s3://"):
        parts = url.split("/", 3)
        return parts[3] if len(parts) > 3 else ""
    # strip protocol and host
    try:
        # http://host:port/bucket/key
        path = url.split("//", 1)[1]
        path_after_host = path.split("/", 1)[1]
        # remove bucket name prefix
        bucket_prefix = f"{settings.S3_BUCKET}/"
        if path_after_host.startswith(bucket_prefix):
            return path_after_host[len(bucket_prefix):]
        return path_after_host
    except Exception:
        return url


def download_object_to_path(key: str, dest_path: str) -> None:
    client = s3_client()
    obj = client.get_object(Bucket=settings.S3_BUCKET, Key=key)
    body = obj["Body"].read()
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(body)


def storage_health() -> dict:
    """Return storage readiness and bucket availability."""
    client = s3_client()
    try:
        client.head_bucket(Bucket=settings.S3_BUCKET)
        return {"ok": True, "bucket": settings.S3_BUCKET}
    except Exception as e:
        return {"ok": False, "bucket": settings.S3_BUCKET, "error": str(e)}
