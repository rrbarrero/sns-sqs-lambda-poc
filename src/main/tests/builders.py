from domain.order import Order


def uuid_a():
    return "123e4567-e89b-12d3-a456-426614174000"


def create_order(override: dict = {}):
    return Order(
        order_id=override.get("order_id", uuid_a()),
        item_id=override.get("item_id", 1),
        quantity=override.get("quantity", 2),
        customer_id=override.get("customer_id", 3),
        date=override.get("date", "2023-10-01 12:00:00"),
    )


def create_order_body(override: dict = {}):
    return {
        "item_id": override.get("item_id", 1),
        "quantity": override.get("quantity", 2),
        "customer_id": override.get("customer_id", 3),
    }
