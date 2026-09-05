from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.api import app
from src.database import get_db
from src.models import Base

import pytest
from datetime import date

test_engine = create_engine("sqlite:///test.db")

@pytest.fixture
def clean_db():
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)

    yield
    Base.metadata.drop_all(test_engine)

def override_get_db():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_db] = override_get_db



# # # # # # # # # # # # # # # # # # # # # # # # API TESTS # # # # # # # # # # # # # # # # # # # # # # # #

client = TestClient(app)

def test_healthcheck(): 
    response = client.get("/healthcheck")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Server is running smoothly"
    }

# # # # # # # # # # # # # # # # # # # # # # # # PRODUCTS TESTS # # # # # # # # # # # # # # # # # # # # # # # #


def test_create_product(clean_db):
    response = client.post(
        "/products",
        json={
            "name": "Ryż",
            "protein": 7,
            "fat": 1,
            "carbs": 78
        }
    )

    assert response.status_code == 200

def test_delete_product(clean_db):
    create_response = client.post(
            "/products",
            json={
                "name": "Ryż",
                "protein": 7,
                "fat": 1,
                "carbs": 78
            }
        )

    product_id = create_response.json()["id"]
    
    response = client.delete(
        f"/products/{product_id}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok", "message": "Product is deleted"
    }

def test_delete_product_not_found(clean_db):
    response = client.delete(
        "/products/100"
    )

    assert response.status_code == 404
    assert response.json() == {
    "detail": "Product not found"
    }

def test_soft_delete_product(clean_db):
    response = client.post(
        "/products",
        json={
            "name": "Ryż",
            "protein": 7,
            "fat": 1,
            "carbs": 78
        }
    )
    product_id = response.json()["id"]

    response_delete = client.delete(f"/products/{product_id}")

    create_response_log = client.post(
        "/logs",
        json={
            "product_id": product_id,
            "weight": 100
        }
    )

    assert response_delete.status_code == 200
    assert create_response_log.status_code == 404

# # # # # # # # # # # # # # # # # # # # # # # # LOGS TESTS # # # # # # # # # # # # # # # # # # # # # # # #

def test_create_log(clean_db):
    create_response_product = client.post(
        "/products",
        json={
            "name": "Ryż",
            "protein": 7,
            "fat": 1,
            "carbs": 78
        }
    )
    product_id = create_response_product.json()["id"]

    create_response_log = client.post(
        "/logs",
        json={
            "product_id": product_id,
            "weight": 100
        }
    )

    assert create_response_log.status_code == 200

# # # # # # # # # # # # # # # # # # # # # # # # REPORTS # # # # # # # # # # # # # # # # # # # # # # # #

def test_sum_day(clean_db):
    create_response_product = client.post(
        "/products",
        json={
            "name": "Ryż",
            "protein": 7,
            "fat": 1,
            "carbs": 78
        }
    )
    product_id = create_response_product.json()["id"]

    create_response_log1 = client.post(
        "/logs",
        json={
            "product_id": product_id,
            "weight": 100
        }
    )
    create_response_log2 = client.post(
            "/logs",
            json={
                "product_id": product_id,
                "weight": 150
            }
        )

    create_response_daily = client.get(
        "/reports/daily-summary",
        params={"target_date": date.today()}   
        )
    daily_data = create_response_daily.json()

    assert create_response_daily.status_code == 200
    assert daily_data["log_count"] == 2
    assert daily_data["protein"] == 17.5