from uuid import UUID
from domain.order import Order
from main import OrderBody
from tests.builders import create_order_body, uuid_a


def test_order_to_json():
    current = Order(
        order_id=UUID(uuid_a()),
        customer_id=1,
        item_id=2,
        quantity=3,
        date="2023-10-01 12:00:00",
    )

    assert (
        current.to_json_string()
        == '{"order_id": "123e4567-e89b-12d3-a456-426614174000", "item_id": 2, "quantity": 3, "customer_id": 1, "date": "2023-10-01 12:00:00"}'
    )


def test_order_body_to_order():
    current = OrderBody(**create_order_body()).to_entity().to_json_string()

    assert '"item_id": 1, "quantity": 2, "customer_id": 3,' in current
