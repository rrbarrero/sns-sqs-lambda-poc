from config import Settings
from infra.sqs_repository import SQSRepository
from fastapi.testclient import TestClient

from tests.builders import create_order_body


def test_post_order(
    client: TestClient,
    billings_repository: SQSRepository,
    orders_repository: SQSRepository,
    settings: Settings,
):
    request = client.post("place-order", json=create_order_body())

    assert request.status_code == 200
    assert request.json() == {"message": "Order placed successfully"}

    billings_messages = billings_repository.receive_message(
        settings.sqs_billing_queue_url
    )
    orders_messages = orders_repository.receive_message(settings.sqs_orders_queue_url)

    assert len(billings_messages) == 1
    assert len(orders_messages) == 1

    assert billings_repository.delete_message(
        queue_url=settings.sqs_billing_queue_url,
        receipt_handle=billings_messages[0]["ReceiptHandle"],
    )
    assert orders_repository.delete_message(
        queue_url=settings.sqs_orders_queue_url,
        receipt_handle=orders_messages[0]["ReceiptHandle"],
    )
