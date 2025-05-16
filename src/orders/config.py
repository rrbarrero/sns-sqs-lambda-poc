from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    s3_access_key_id: str = Field(default="test", alias="SNS_ACCESS_KEY_ID")
    s3_secret_access_key: str = Field(default="test", alias="SNS_SECRET_ACCESS_KEY")
    s3_aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    s3_endpoint_url: str = Field(
        default="http://192.168.1.164:4566", alias="S3_ENDPOINT_URL"
    )
    s3_orders_bucket: str = Field(default="orders-dev", alias="S3_ORDERS_BUCKET")


settings = Settings()  # type: ignore


def get_settings() -> Settings:
    return settings
