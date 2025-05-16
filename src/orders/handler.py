import logging

from config import get_settings
from domain.order import Order
from factory import get_s3_repository

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    Lambda handler triggered by SQS messages for new orders.
    Parses order messages and uploads them to an S3 bucket.
    """
    settings = get_settings()
    logger.info(f"Using settings for bucket: {settings.s3_orders_bucket}")

    try:
        repository = get_s3_repository()
    except Exception as e:
        logger.error(f"Failed to initialize S3 repository: {e}")
        raise e

    for record in event.get("Records", []):
        try:
            message_body = record.get("body")
            if not message_body:
                logger.warning("Received record without a body. Skipping.")
                continue

            logger.info(f"Processing message body: {message_body[:200]}...")

            order = Order.from_json_string(message_body)

            file_name = f"order_{order.order_id}.json"
            logger.info(
                f"Uploading order {order.order_id} to s3://{settings.s3_orders_bucket}/{file_name}"
            )

            repository.upload_file(
                bucket_name=settings.s3_orders_bucket,
                file_name=file_name,
                order=order,
            )
            logger.info(f"Successfully uploaded order {order.order_id}")

        except Exception as e:
            logger.error(
                f"Error processing record: {record.get('messageId', 'N/A')}. Error: {e}",
                exc_info=True,
            )
            continue

    logger.info("Lambda execution finished successfully.")


if __name__ == "__main__":
    print("Running handler locally (simulation)...")

    simulated_event = {
        "Records": [
            {
                "messageId": "simulated-message-id-1",
                "receiptHandle": "simulated-receipt-handle",
                "body": '{"order_id": "123e4567-e89b-12d3-a456-426614174000", "item_id": 2, "quantity": 3, "customer_id": 1, "date": "2023-10-01 12:00:00"}',
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1523232000000",
                    "SenderId": "simulated-sender",
                    "ApproximateFirstReceiveTimestamp": "1523232000001",
                },
                "messageAttributes": {},
                "md5OfBody": "fcecf...",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:orders-dev",
                "awsRegion": "us-east-1",
            }
        ]
    }

    try:
        handler(simulated_event, None)
        print("Local simulation finished.")
    except Exception as e:
        print(f"Local simulation failed: {e}")
