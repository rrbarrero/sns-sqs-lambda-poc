from infra.s3_repository import S3Repository
from infra.utils import get_s3_client


def get_s3_repository():
    return S3Repository(get_s3_client())
