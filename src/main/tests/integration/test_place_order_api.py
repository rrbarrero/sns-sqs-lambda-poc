import json
from fastapi.testclient import TestClient
import pytest

from infra.sns_repository import InMemorySNSRepository
from main import app, create_sns_repositiory_with
from config import Settings
from infra.sqs_repository import SQSRepository
from tests.builders import create_order_body


@pytest.fixture
def spy():
    spy = InMemorySNSRepository()
    app.dependency_overrides[create_sns_repositiory_with] = lambda: spy
    yield spy
    app.dependency_overrides.clear()


def test_post_order(client: TestClient, spy: InMemorySNSRepository):
    request = client.post("place-order", json=create_order_body())

    assert request.status_code == 200
    assert request.json() == {"message": "Order placed successfully"}

    assert len(spy.published_messages) == 1

    message = json.loads(spy.published_messages[0])
    assert message["item_id"] == 1
    assert message["quantity"] == 2
    assert message["customer_id"] == 3
