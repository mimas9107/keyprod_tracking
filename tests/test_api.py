import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", autouse=True)
def init_database(event_loop):
    event_loop.run_until_complete(init_db())


def test_get_ram_options():
    client = TestClient(app)
    response = client.get("/ram-options")
    assert response.status_code == 200
    assert response.json() == []


def test_get_ram_prices_not_found():
    client = TestClient(app)
    response = client.get("/ram/999/prices")
    assert response.status_code == 404


def test_get_chart_data_not_found():
    client = TestClient(app)
    response = client.get("/ram/999/chart-data")
    assert response.status_code == 404
