from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.api import app
from src.database import get_db
from src.models import Base

import pytest
from datetime import date as Date

import os
from dotenv import load_dotenv

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
test_engine = create_engine(TEST_DATABASE_URL)

Base.metadata.create_all(test_engine)

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


def test_create_product_multiple(clean_db):
    create_response1 = client.post(
        "/products",
        json={
            "name": "Ryż",
            "protein": 7,
            "fat": 1,
            "carbs": 78
        }
    )
    create_response2 = client.post(
        "/products",
        json={
            "name": "Makaron",
            "protein": 10,
            "fat": 2,
            "carbs": 50
        }
    )

    response3 = client.get("/products")
    assert response3.status_code == 200
    assert len(response3.json()) == 2

def test_product_search(clean_db):
    client.post(
        "/products",
        json={
            "name": "Ryż",
            "protein": 7,
            "fat": 1,
            "carbs": 78
        }
    )
    client.post(
        "/products",
        json={
            "name": "Kurczak",
            "protein": 20,
            "fat": 6,
            "carbs": 25
        }
    )

    response3 = client.get(
        "/products/search",
        params={
            "phrase": "Ry"
            }
        )

    data = response3.json()

    assert response3.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Ryż"

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

def test_soft_delete_product_same_name(clean_db):
    response1 = client.post(
        "/products",
        json={
            "name": "Ryż",
            "protein": 7,
            "fat": 1,
            "carbs": 78
        }
    )
    product_id1 = response1.json()["id"]
    response2 = client.post(
        "/products",
        json={
            "name": "Ryż",
            "protein": 7,
            "fat": 1,
            "carbs": 78
        }
    )

    assert response2.status_code == 409

    response1_delete = client.delete(f"/products/{product_id1}")

    response3 = client.post(
        "/products",
        json={
            "name": "Ryż",
            "protein": 7,
            "fat": 1,
            "carbs": 78
        }
    )

    assert response3.status_code == 200

def test_update(clean_db):
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
    response_update = client.patch(
        f"/products/{product_id}",
        json={
            "protein": 12
        }
    )

    data = response_update.json()

    assert response_update.status_code == 200
    assert data["protein"] == 12

def test_update_nonnegative(clean_db):
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
    response_update = client.patch(
        f"/products/{product_id}",
        json={
            "protein": -12
        }
    )

    assert response_update.status_code == 422

def test_update_nonexisting(clean_db):
    response_update = client.patch(
        f"/products/1",
        json={
            "protein": 12
        }
    )

    assert response_update.status_code == 404
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

def test_get_log(clean_db):
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
    log_id = create_response_log.json()["id"]

    get_response_log = client.get(
        f"/logs/{log_id}"
    )


    data = get_response_log.json()

    assert get_response_log.status_code == 200
    assert data["id"] == log_id
    assert data["calories"] == 349

def test_get_log_target_date(clean_db):
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
    target_date = create_response_log.json()["date"]

    get_response_log = client.get(
        "/logs",
        params={
            "target_date": target_date
        }
    )


    data = get_response_log.json()

    assert get_response_log.status_code == 200
    assert data[0]["date"] == target_date

def test_delete_log(clean_db):
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
    log_id = create_response_log.json()["id"]

    delete_response_log = client.delete(
        f"/logs/{log_id}"
    )

    assert delete_response_log.status_code == 200
    assert delete_response_log.json() == {"status": "ok", "message": "Log is deleted"}

def test_delete_log_nonexisting(clean_db):
    delete_response_log = client.delete(
        f"/logs/{1}"
    )

    assert delete_response_log.status_code == 404
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
        params={"target_date": Date.today()}   
        )
    daily_data = create_response_daily.json()

    assert create_response_daily.status_code == 200
    assert daily_data["log_count"] == 2
    assert daily_data["protein"] == 17.5

def test_top_and_average_products(clean_db):
    create_response_product1 = client.post(
        "/products",
        json={
            "name": "Ryż",
            "protein": 7,
            "fat": 1,
            "carbs": 78
        }
    )
    create_response_product2 = client.post(
        "/products",
        json={
            "name": "Makaron",
            "protein": 10,
            "fat": 3,
            "carbs": 50
        }
    )
    create_response_product3 = client.post(
        "/products",
        json={
            "name": "Ziemniaki",
            "protein": 4,
            "fat": 0,
            "carbs": 40
        }
    )
    create_response_product4 = client.post(
        "/products",
        json={
            "name": "Kasza",
            "protein": 6,
            "fat": 5,
            "carbs": 60
        }
    )
    product_id1 = create_response_product1.json()["id"]
    product_id2 = create_response_product2.json()["id"]
    product_id3 = create_response_product3.json()["id"]
    product_id4 = create_response_product4.json()["id"]


    client.post(
        "/logs",
        json={
            "product_id": product_id1,
            "weight": 300
        }
    )
    client.post(
        "/logs",
        json={
            "product_id": product_id1,
            "weight": 200
        }
    )
    client.post(
        "/logs",
        json={
            "product_id": product_id1,
            "weight": 150
        }
    )
    client.post(
        "/logs",
        json={
            "product_id": product_id1,
            "weight": 165
        }
    )
    client.post(
        "/logs",
        json={
            "product_id": product_id2,
            "weight": 254
        }
    )
    client.post(
        "/logs",
        json={
            "product_id": product_id2,
            "weight": 354
        }
    )
    client.post(
        "/logs",
        json={
            "product_id": product_id2,
            "weight": 123
        }
    )
    client.post(
        "/logs",
        json={
            "product_id": product_id3,
            "weight": 535
        }
    )
    client.post(
        "/logs",
        json={
            "product_id": product_id3,
            "weight": 254
        }
    )
    client.post(
        "/logs",
        json={
            "product_id": product_id4,
            "weight": 1000
        }
    )

    top_response = client.get("/report/top")
    avg_response = client.get("report/avg")
    data_top = top_response.json()
    data_avg = avg_response.json()

    assert top_response.status_code == 200
    assert len(data_top) == 3

    assert data_top[0]["name"] == "Ryż"
    assert data_top[0]["number_of_logs"] == 4
    assert data_top[0]["weight_sum"] == 815

    assert data_top[2]["name"] == "Ziemniaki"
    assert data_top[2]["number_of_logs"] == 2
    assert data_top[2]["weight_sum"] == 789



    assert avg_response.status_code == 200
    assert len(data_avg) == 3

    assert data_avg[0]["name"] == "Ziemniaki"
    assert data_avg[0]["number_of_logs"] == 2
    assert data_avg[0]["weight_avg"] == 394.5

    assert data_avg[1]["name"] == "Makaron"
    assert data_avg[1]["number_of_logs"] == 3
    assert data_avg[1]["weight_avg"] == 243.67

    assert data_avg[2]["name"] == "Ryż"
    assert data_avg[2]["number_of_logs"] == 4
    assert data_avg[2]["weight_avg"] == 203.75