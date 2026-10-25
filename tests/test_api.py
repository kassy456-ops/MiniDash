import pytest
from fastapi.testclient import TestClient
from src.main import app

import src.database as database
import src.main as main

@pytest.fixture(autouse=True)
def use_test_database(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test_minidash.db"

    monkeypatch.setattr(database, "DATABASE_PATH", test_db_path)
    monkeypatch.setattr(main, "get_connection", database.get_connection)

    database.initialize_database()

client = TestClient(app)


def test_get_restaurants():
    response = client.get("/restaurants")

    assert response.status_code == 200

    restaurants = response.json()

    assert len(restaurants) == 5
    assert restaurants[0]["name"] == "Pizza Palace"
    assert restaurants[1]["name"] == "Sushi House"

def test_get_restaurant_menu():
    response = client.get("/restaurants/1/menu")

    assert response.status_code == 200

    menu = response.json()

    assert len(menu) > 0
    assert "name" in menu[0]
    assert "price_cents" in menu[0]

def test_create_order():
    menu_response = client.get("/restaurants/1/menu")
    assert menu_response.status_code == 200

    menu_item = menu_response.json()[0]

    order_data = {
        "restaurant_id": 1,
        "address": "123 Test Street, New York, NY",
        "items": [
            {
                "menu_item_id": menu_item["id"],
                "quantity": 2
            }
        ]
    }

    response = client.post("/orders", json=order_data)

    assert response.status_code == 201

    order = response.json()

    assert "id" in order
    assert order["restaurant_id"] == 1
    assert order["status"] == "PLACED"
    assert order["total_cents"] == menu_item["price_cents"] * 2
    assert order["address"] == "123 Test Street, New York, NY"

def test_get_order():
    menu_response = client.get("/restaurants/1/menu")
    menu_item = menu_response.json()[0]

    order_data = {
        "restaurant_id": 1,
        "address": "123 Test Street, New York, NY",
        "items": [
            {
                "menu_item_id": menu_item["id"],
                "quantity": 2
            }
        ]
    }

    create_response = client.post("/orders", json=order_data)
    assert create_response.status_code == 201

    order_id = create_response.json()["id"]

    response = client.get(f"/orders/{order_id}")

    assert response.status_code == 200

    order = response.json()

    assert order["id"] == order_id
    assert order["restaurant_id"] == 1
    assert order["total_cents"] == menu_item["price_cents"] * 2

def test_update_order_status():
    menu_response = client.get("/restaurants/1/menu")
    menu_item = menu_response.json()[0]

    order_data = {
        "restaurant_id": 1,
        "address": "123 Test Street, New York, NY",
        "items": [
            {
                "menu_item_id": menu_item["id"],
                "quantity": 1
            }
        ]
    }

    create_response = client.post("/orders", json=order_data)
    assert create_response.status_code == 201

    order_id = create_response.json()["id"]

    response = client.patch(
        f"/orders/{order_id}/status",
        json={"status": "PREPARING"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PREPARING"

def test_invalid_restaurant_id():
    response = client.get("/restaurants/99999/menu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found"

def test_invalid_order_id():
    response = client.get("/orders/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

def test_invalid_menu_item():
    order_data = {
        "restaurant_id": 1,
        "address": "123 Test Street, New York, NY",
        "items": [
            {
                "menu_item_id": 999999,
                "quantity": 1
            }
        ]
    }

    response = client.post("/orders", json=order_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid menu item for this restaurant"

