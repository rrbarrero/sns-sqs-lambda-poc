from datetime import datetime
from dataclasses import asdict, dataclass
import json
import uuid


@dataclass
class Order:
    order_id: uuid.UUID
    item_id: int
    quantity: int
    customer_id: int
    date: str

    @classmethod
    def new(cls, item_id: int, quantity: int, customer_id: int):
        order_id = uuid.uuid4()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return cls(
            order_id=order_id,
            item_id=item_id,
            quantity=quantity,
            customer_id=customer_id,
            date=date,
        )

    def to_json_string(self) -> str:
        return json.dumps(asdict(self), default=str)
