from fastapi import Depends, FastAPI
from pydantic import BaseModel

from config import Settings, get_settings
from domain.order import Order
from factory import create_logger, create_sns_repository
from infra.sns_repository import SNSRepository


app = FastAPI()


async def create_sns_repositiory_with():
    return create_sns_repository()


async def get_settings_with():
    return get_settings()


async def create_logger_with():
    return create_logger("PlaceOrderAPI")


class OrderBody(BaseModel):
    item_id: int
    quantity: int
    customer_id: int

    def to_entity(self) -> Order:
        return Order.new(
            item_id=self.item_id,
            quantity=self.quantity,
            customer_id=self.customer_id,
        )


@app.post("/place-order")
def place_order(
    order: OrderBody,
    repository: SNSRepository = Depends(create_sns_repositiory_with),
    settings: Settings = Depends(get_settings_with),
    logger=Depends(create_logger_with),
):
    logger.info(
        repository.publish_message(
            topic_arn=settings.sns_topic_arn,
            order=order.to_entity(),
        )
    )
    return {"message": "Order placed successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
