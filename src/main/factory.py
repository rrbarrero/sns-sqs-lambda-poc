from config import get_settings
from infra.logger import get_logger
from infra.sns_repository import SNSRepository
from infra.sqs_repository import SQSRepository
from infra.utils import get_sns_client, get_sqs_client


def create_sns_repository() -> SNSRepository:
    return SNSRepository(get_sns_client())


def create_sqs_orders_repository() -> SQSRepository:
    return SQSRepository(get_sqs_client())


def create_sqs_billing_repository() -> SQSRepository:
    return SQSRepository(get_sqs_client())


def create_logger(name: str):
    return get_logger(name)
