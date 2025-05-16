import boto3

from config import get_settings


def get_sns_client():
    settings = get_settings()
    return boto3.client(
        "sns",
        region_name=settings.aws_region,
        endpoint_url=settings.sns_endpoint_url,
        aws_access_key_id=settings.sns_access_key_id,
        aws_secret_access_key=settings.sns_secret_access_key,
    )


def get_sqs_client():
    settings = get_settings()
    return boto3.client(
        "sqs",
        region_name=settings.aws_region,
        endpoint_url=settings.sqs_endpoint_url,
        aws_access_key_id=settings.sns_access_key_id,
        aws_secret_access_key=settings.sns_secret_access_key,
    )
