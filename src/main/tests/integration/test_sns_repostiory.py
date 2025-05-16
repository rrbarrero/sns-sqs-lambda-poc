from config import get_settings
from infra.sns_repository import SNSRepository
from infra.sqs_repository import SQSRepository
from infra.utils import get_sns_client, get_sqs_client
from tests.builders import create_order


def test_sns_repository():
    repository = SNSRepository(get_sns_client())

    repository.publish_message(
        topic_arn=get_settings().sns_topic_arn, order=create_order()
    )

    sqs_repository = SQSRepository(get_sqs_client())

    orders = sqs_repository.receive_message(
        queue_url=get_settings().sqs_orders_queue_url
    )

    billings = sqs_repository.receive_message(
        queue_url=get_settings().sqs_billing_queue_url
    )

    assert orders[0]["Body"] == create_order().to_json_string()
    assert billings[0]["Body"] == create_order().to_json_string()

    assert sqs_repository.delete_message(
        queue_url=get_settings().sqs_orders_queue_url,
        receipt_handle=orders[0]["ReceiptHandle"],
    )

    assert sqs_repository.delete_message(
        queue_url=get_settings().sqs_billing_queue_url,
        receipt_handle=billings[0]["ReceiptHandle"],
    )
