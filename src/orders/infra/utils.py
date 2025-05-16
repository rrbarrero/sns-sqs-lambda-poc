import boto3

from config import get_settings


def get_s3_client():
    settings = get_settings()
    return boto3.client(
        "s3",
        region_name=settings.s3_aws_region,
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
    )
