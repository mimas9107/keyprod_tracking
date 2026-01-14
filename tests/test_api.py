from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_ram_options():
    response = client.get("/ram-options")
    assert response.status_code == 200
    # Assuming DB is empty, should be empty list
    assert response.json() == []


def test_get_ram_prices_not_found():
    response = client.get("/ram/999/prices")
    assert response.status_code == 404


def test_get_chart_data_not_found():
    response = client.get("/ram/999/chart-data")
    assert response.status_code == 404
