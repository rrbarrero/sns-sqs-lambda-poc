from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    sns_topic_arn: str = Field(
        default="arn:aws:sns:us-east-1:000000000000:OrderPlaced-dev",
        alias="SNS_TOPIC_ARN",
    )
    sns_endpoint_url: str = Field(
        default="http://192.168.1.164:4566", alias="SNS_ENDPOINT_URL"
    )
    sns_access_key_id: str = Field(default="test", alias="SNS_ACCESS_KEY_ID")
    sns_secret_access_key: str = Field(default="test", alias="SNS_SECRET_ACCESS_KEY")
    sqs_endpoint_url: str = Field(
        default="http://192.168.1.164:4566", alias="SQS_ENDPOINT_URL"
    )
    sqs_orders_queue_url: str = Field(
        default="http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/orders-dev",
        alias="SQS_ORDERS_QUEUE_URL",
    )
    sqs_billing_queue_url: str = Field(
        default="http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/billing-dev",
        alias="SQS_BILLING_QUEUE_URL",
    )


settings = Settings()  # type: ignore


def get_settings() -> Settings:
    return settings
