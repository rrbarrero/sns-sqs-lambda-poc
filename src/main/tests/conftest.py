from fastapi.testclient import TestClient
import pytest
from config import get_settings
from factory import create_sqs_orders_repository
from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def billings_repository():
    return create_sqs_orders_repository()


@pytest.fixture
def orders_repository():
    return create_sqs_orders_repository()


@pytest.fixture
def settings():
    return get_settings()
