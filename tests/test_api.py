from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.api import app
from src.database import get_db
from src.models import Base
from src.enums import ProductType

import pytest
from datetime import date as Date

import os
from dotenv import load_dotenv

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
test_engine = create_engine(TEST_DATABASE_URL)

Base.metadata.create_all(test_engine)

# # # # # # # # # # # # # # # # # # # # # # # # HELPERS/FIXTURES # # # # # # # # # # # # # # # # # # # # # # # #

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

def create_test_product(name, protein, fat, carbs, headers, product_type=ProductType.product
    ):
    response = client.post(
        "/products",
        headers=headers,
        json={
            "name": name,
            "type": product_type,
            "protein": protein,
            "fat": fat,
            "carbs": carbs 
        }
    )
    return response

def create_test_log(product_id, weight, headers):
    response = client.post(
        "/logs",
        headers=headers,
        json={
            "product_id": product_id,
            "weight":  weight
        }
    )
    return response

def create_test_user(email, password):
    response = client.post(
        "/users/register",
        json={
            "email": email,
            "password": password
        }
    )
    return response

def login_test_user(email, password):
    response = client.post(
        "/users/login",
        json={
            "email": email,
            "password": password
        }
    )
    return response

def create_test_authorization(
    email="test@example.com",
    password="TestPassword123"
):
    create_test_user(email, password)
    login_response = login_test_user(email, password)
    access_token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}"
    }


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
        headers=create_test_authorization(),
        json={
            "name": "Ryż",
            "protein": 7,
            "fat": 1,
            "carbs": 78,
            "type": "product"
        }
    )

    assert response.status_code == 200


def test_create_product_multiple(clean_db):
    headers=create_test_authorization()
    create_test_product("Ryż", 7, 1, 78, headers)
    create_test_product("Makaron", 10, 3, 50, headers)

    response1 = client.get("/products", headers=headers)

    assert response1.status_code == 200
    assert len(response1.json()) == 2

def test_product_search(clean_db):
    headers=create_test_authorization()
    create_test_product("Ryż", 7, 1, 78, headers)
    create_test_product("Kurczak", 20, 6, 25, headers)

    response1 = client.get(
        "/products/search",
        headers=headers,
        params={
            "phrase": "Ry"
            }
        )

    data = response1.json()

    assert response1.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Ryż"

def test_delete_product(clean_db):
    headers=create_test_authorization()
    create_response1 = create_test_product("Ryż", 7, 1, 78, headers)
    product_id = create_response1.json()["id"]
    
    response1 = client.delete(
        f"/products/{product_id}",
        headers=headers
    )

    assert response1.status_code == 200
    assert response1.json() == {
        "status": "ok", "message": "Product is deleted"
    }

def test_delete_product_not_found(clean_db):
    headers=create_test_authorization()
    response = client.delete(
        "/products/100",
        headers=headers
    )

    assert response.status_code == 404
    assert response.json() == {
    "detail": "Product not found"
    }

def test_soft_delete_product(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers)
    product_id = create_response_product1.json()["id"]
    response_delete1 = client.delete(f"/products/{product_id}", headers=headers)
    create_response_log1 = create_test_log(product_id, 200, headers)

    assert response_delete1.status_code == 200
    assert create_response_log1.status_code == 404

def test_soft_delete_product_same_name(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers)
    product_id1 = create_response_product1.json()["id"]
    create_response_product2 = create_test_product("Ryż", 7, 1, 78, headers)

    assert create_response_product2.status_code == 409

    client.delete(f"/products/{product_id1}", headers=headers)
    create_response_product3 = create_test_product("Ryż", 7, 1, 78, headers)

    assert create_response_product3.status_code == 200

def test_update(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers)
    product_id = create_response_product1.json()["id"]
    response_update1 = client.patch(
        f"/products/{product_id}",
        headers=headers,
        json={
            "protein": 12
        }
    )

    data = response_update1.json()

    assert response_update1.status_code == 200
    assert data["protein"] == 12

def test_update_nonnegative(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers)
    product_id = create_response_product1.json()["id"]
    response_update1 = client.patch(
        f"/products/{product_id}",
        headers=headers,
        json={
            "protein": -12
        }
    )

    assert response_update1.status_code == 422

def test_update_nonexisting(clean_db):
    headers=create_test_authorization()
    response_update = client.patch(
        f"/products/1",
        headers=headers,
        json={
            "protein": 12
        }
    )

    assert response_update.status_code == 404
# # # # # # # # # # # # # # # # # # # # # # # # LOGS TESTS # # # # # # # # # # # # # # # # # # # # # # # #

def test_create_log(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers)
    product_id = create_response_product1.json()["id"]
    create_response_log1 = create_test_log(product_id, 200, headers)

    assert create_response_log1.status_code == 200

def test_get_log(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers)
    product_id = create_response_product1.json()["id"]
    create_response_log1 = create_test_log(product_id, 200, headers)
    log_id = create_response_log1.json()["id"]

    get_response_log1 = client.get(
        f"/logs/{log_id}",
        headers=headers
    )


    data = get_response_log1.json()

    assert get_response_log1.status_code == 200
    assert data["id"] == log_id
    assert data["calories"] == 698

def test_get_log_target_date(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers)
    product_id = create_response_product1.json()["id"]
    create_response_log1 = create_test_log(product_id, 200, headers)
    target_date = create_response_log1.json()["date"]

    get_response_log = client.get(
        "/logs",
        headers=headers,
        params={
            "target_date": target_date
        }
    )

    data = get_response_log.json()

    assert get_response_log.status_code == 200
    assert data[0]["date"] == target_date

def test_delete_log(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers)
    product_id = create_response_product1.json()["id"]
    create_response_log1 = create_test_log(product_id, 200, headers)
    log_id = create_response_log1.json()["id"]
    delete_response_log = client.delete(
        f"/logs/{log_id}",
        headers=headers
    )

    assert delete_response_log.status_code == 200
    assert delete_response_log.json() == {"status": "ok", "message": "Log is deleted"}

def test_delete_log_nonexisting(clean_db):
    headers = create_test_authorization()
    delete_response_log = client.delete(
        f"/logs/{1}",
        headers=headers
    )

    assert delete_response_log.status_code == 404
# # # # # # # # # # # # # # # # # # # # # # # # REPORTS # # # # # # # # # # # # # # # # # # # # # # # #

def test_sum_day(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers)
    product_id = create_response_product1.json()["id"]
    create_test_log(product_id, 100, headers)
    create_test_log(product_id, 150, headers)



    create_response_daily = client.get(
        "/reports/daily-summary",
        headers=headers,
        params={"target_date": Date.today()}   
        )
    daily_data = create_response_daily.json()

    assert create_response_daily.status_code == 200
    assert daily_data["log_count"] == 2
    assert daily_data["protein"] == 17.5

def test_top_and_average_products(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers)
    create_response_product2 = create_test_product("Makaron", 10, 3, 50, headers)
    create_response_product3 = create_test_product("Ziemniaki", 4, 0, 40, headers)
    create_response_product4 = create_test_product("Kasza", 6, 5, 60, headers)
    product_id1 = create_response_product1.json()["id"]
    product_id2 = create_response_product2.json()["id"]
    product_id3 = create_response_product3.json()["id"]
    product_id4 = create_response_product4.json()["id"]

    create_test_log(product_id1, 154, headers)
    create_test_log(product_id1, 254, headers)
    create_test_log(product_id1, 436, headers)
    create_test_log(product_id1, 436, headers)
    create_test_log(product_id2, 653, headers)
    create_test_log(product_id2, 254, headers)
    create_test_log(product_id2, 753, headers)
    create_test_log(product_id3, 835, headers)
    create_test_log(product_id3, 1004, headers)
    create_test_log(product_id4, 1535, headers)

    top_response = client.get("/report/top", headers=headers)
    avg_response = client.get("report/avg", headers=headers)
    data_top = top_response.json()
    data_avg = avg_response.json()

    assert top_response.status_code == 200
    assert len(data_top) == 3

    assert data_top[0]["name"] == "Ryż"
    assert data_top[0]["number_of_logs"] == 4
    assert data_top[0]["weight_sum"] == 1280

    assert data_top[2]["name"] == "Ziemniaki"
    assert data_top[2]["number_of_logs"] == 2
    assert data_top[2]["weight_sum"] == 1839


    assert avg_response.status_code == 200
    assert len(data_avg) == 3

    assert data_avg[0]["name"] == "Ziemniaki"
    assert data_avg[0]["number_of_logs"] == 2
    assert data_avg[0]["weight_avg"] == 919.5

    assert data_avg[1]["name"] == "Makaron"
    assert data_avg[1]["number_of_logs"] == 3
    assert data_avg[1]["weight_avg"] == 553.33

    assert data_avg[2]["name"] == "Ryż"
    assert data_avg[2]["number_of_logs"] == 4
    assert data_avg[2]["weight_avg"] == 320.0

# # # # # # # # # # # # # # # # # # # # # # # # USERS # # # # # # # # # # # # # # # # # # # # # # # #

def test_create_user(clean_db):
    test_create_user1 = create_test_user("test@example.com", "TestPassword123")

    assert test_create_user1.status_code == 200

def test_login_user(clean_db):
    create_test_user("test@example.com", "TestPassword123")
    test_login_user1 = login_test_user("test@example.com", "TestPassword123")

    assert test_login_user1.status_code == 200

def test_create_user_same_email(clean_db):
    create_test_user("test@example.com", "TestPassword123")
    test_create_user2 = create_test_user("test@example.com", "TestPassword123")

    assert test_create_user2.status_code == 409

def test_login_user_wrong_password(clean_db):

    create_test_user("test@example.com", "TestPassword123")
    test_login_user1 = login_test_user("test@example.com", "TestPassword")

    assert test_login_user1.status_code == 401

def test_login_wrong_email(clean_db):

    test_login_user1 = login_test_user("test@example.com", "TestPassword123")

    assert test_login_user1.status_code == 401

def test_current_user(clean_db):
    headers = create_test_authorization()
    current_user = client.get(
        "/users/me",
        headers=headers
    )
    data1 = current_user.json()

    assert current_user.status_code == 200
    assert data1["email"] == "test@example.com"
    assert data1["active"] is True

def test_current_user_without_token(clean_db):
    response = client.get("/users/me")

    assert response.status_code == 401

# # # # # # # # # # # # # # # # # # # # # # # # OWNERSHIP # # # # # # # # # # # # # # # # # # # # # # # #
def test_login(
    clean_db,
    email="test@example.com",
    password="TestPassword123"
    ):
    create_test_user(email, password)
    login_response = login_test_user(email, password)
    bearer = login_response.json()["token_type"]
    access_token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    assert login_response.status_code == 200
    assert bearer == "bearer"
    assert access_token
    assert refresh_token

def test_refresh_token(clean_db,
    email="test@example.com",
    password="TestPassword123"
    ):
    create_test_user(email, password)
    login_response = login_test_user(email, password)
    refresh_token = login_response.json()["refresh_token"]
    refresh_headers = {
        "Authorization": f"Bearer {refresh_token}"
    }
    refresh_check = client.post("/users/token/refresh", headers=refresh_headers)

    access_token = refresh_check.json()["access_token"]
    token_type = refresh_check.json()["token_type"]

    assert refresh_check.status_code == 200
    assert access_token
    assert token_type == "bearer"

def test_access_token_as_refresh_token(clean_db,
    email="test@example.com",
    password="TestPassword123"
    ):
    create_test_user(email, password)
    login_response = login_test_user(email, password)
    refresh_token = login_response.json()["access_token"]
    access_headers = {
        "Authorization": f"Bearer {refresh_token}"
    }
    refresh_check = client.post("/users/token/refresh", headers=access_headers)

    assert refresh_check.status_code == 401
    assert refresh_check.json() == {
        "detail": "Invalid token type"
        }
def test_refresh_token_as_access_token(clean_db,
    email="test@example.com",
    password="TestPassword123"
    ):
    create_test_user(email, password)
    login_response = login_test_user(email, password)
    access_token = login_response.json()["refresh_token"]
    access_headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = client.post(
            "/products",
            headers=access_headers,
            json={
                "name": "Ryż",
                "protein": 7,
                "fat": 1,
                "carbs": 78,
                "type": "product"
            }
        )
    
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid token type"
        }

def test_invalid_token(clean_db):
    response = client.post(
            "/products",
            headers={
                "Authorization": "Bearer 123"
            },
            json={
                "name": "Ryż",
                "protein": 7,
                "fat": 1,
                "carbs": 78,
                "type": "product"
            }
        )
    
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or expired token"
    }

def test_log_ownership(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )

    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers1)
    product_id1 = create_response_product1.json()["id"]
    change_to_global = client.patch(f"/products/{product_id1}/visibility",
        headers=headers1,
        params={
            "is_global": True
        })

    create_response_log1 = create_test_log(product_id1, 154, headers1)
    log_id = create_response_log1.json()["id"]

    get_response_log1 = client.get(
        f"/logs/{log_id}",
        headers=headers1
    )
    get_response_log2 = client.get(
        f"/logs/{log_id}",
        headers=headers2
    )

    assert change_to_global.status_code == 200
    assert get_response_log1.status_code == 200
    assert get_response_log2.status_code == 404

def test_log_ownership_delete_log(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )

    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers1)
    product_id1 = create_response_product1.json()["id"]
    change_to_global = client.patch(f"/products/{product_id1}/visibility",
        headers=headers1,
        params={
            "is_global": True
        })

    create_response_log1 = create_test_log(product_id1, 154, headers1)
    log_id = create_response_log1.json()["id"]

    delete_response_log1 = client.delete(
        f"/logs/{log_id}",
        headers=headers2
    )

    get_response_log1 = client.get(
            f"/logs/{log_id}",
            headers=headers1
        )
    
    assert change_to_global.status_code == 200
    assert delete_response_log1.status_code == 404
    assert get_response_log1.status_code == 200

def test_log_ownership_log_target_date(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )

    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers1)
    product_id1 = create_response_product1.json()["id"]
    change_to_global = client.patch(f"/products/{product_id1}/visibility",
        headers=headers1,
        params={
            "is_global": True
        })

    create_response_log1 = create_test_log(product_id1, 162, headers1)
    create_test_log(product_id1, 635, headers1)
    create_response_log3 = create_test_log(product_id1, 564, headers2)
    target_date1 = create_response_log1.json()["date"]
    target_date2 = create_response_log3.json()["date"]

    get_response_log1 = client.get(
        "/logs",
        headers=headers1,
        params={
            "target_date": target_date1
        }
    )
    get_response_log2 = client.get(
            "/logs",
            headers=headers2,
            params={
                "target_date": target_date2
            }
        )
    
    data1 = get_response_log1.json()
    data2 = get_response_log2.json()

    assert change_to_global.status_code == 200
    assert get_response_log1.status_code == 200
    assert get_response_log2.status_code == 200

    assert data1[0]["date"] == target_date1
    assert data2[0]["date"] == target_date2
    assert len(data1) == 2
    assert len(data2) == 1

def test_reports_ownership_daily_sum(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )

    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers1)
    product_id1 = create_response_product1.json()["id"]
    change_to_global = client.patch(f"/products/{product_id1}/visibility",
        headers=headers1,
        params={
            "is_global": True
        })

    create_test_log(product_id1, 162, headers1)
    create_test_log(product_id1, 635, headers1)
    create_test_log(product_id1, 635, headers1)
    create_test_log(product_id1, 564, headers2)
    create_test_log(product_id1, 564, headers2)

    create_response_daily1 = client.get(
        "/reports/daily-summary",
        headers=headers1,
        params={"target_date": Date.today()}   
        )
    create_response_daily2 = client.get(
        "/reports/daily-summary",
        headers=headers2,
        params={"target_date": Date.today()}   
        )
    daily_data1 = create_response_daily1.json()
    daily_data2 = create_response_daily2.json()

    assert change_to_global.status_code == 200
    assert create_response_daily1.status_code == 200
    assert create_response_daily2.status_code == 200

    assert daily_data1["log_count"] == 3
    assert daily_data2["log_count"] == 2
    assert daily_data1["calories"] == 4997.68
    assert daily_data2["calories"] == 3936.72

def test_reports_ownership_top_and_avg(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, headers1)
    create_response_product2 = create_test_product("Makaron", 10, 3, 50, headers1)
    create_response_product3 = create_test_product("Ziemniaki", 4, 0, 40, headers1)
    create_response_product4 = create_test_product("Kasza", 6, 5, 60, headers1)
    product_id1 = create_response_product1.json()["id"]
    product_id2 = create_response_product2.json()["id"]
    product_id3 = create_response_product3.json()["id"]
    product_id4 = create_response_product4.json()["id"]
    change_to_global1 = client.patch(f"/products/{product_id1}/visibility",
        headers=headers1,
        params={
            "is_global": True
        })
    change_to_global2 = client.patch(f"/products/{product_id2}/visibility",
        headers=headers1,
        params={
            "is_global": True
        })
    change_to_global3 = client.patch(f"/products/{product_id3}/visibility",
        headers=headers1,
        params={
            "is_global": True
        })
    change_to_global4 = client.patch(f"/products/{product_id4}/visibility",
        headers=headers1,
        params={
            "is_global": True
        })
    create_test_log(product_id1, 154, headers1)
    create_test_log(product_id1, 254, headers1)
    create_test_log(product_id1, 436, headers1)
    create_test_log(product_id1, 436, headers1)
    create_test_log(product_id2, 653, headers1)
    create_test_log(product_id2, 254, headers1)
    create_test_log(product_id2, 753, headers1)
    create_test_log(product_id3, 835, headers1)
    create_test_log(product_id3, 1004, headers1)
    create_test_log(product_id4, 1535, headers1)

    create_test_log(product_id1, 1544, headers2)
    create_test_log(product_id2, 2546, headers2)
    create_test_log(product_id2, 1735, headers2)
    create_test_log(product_id3, 4362, headers2)

    top_response1 = client.get("/report/top", headers=headers1)
    avg_response1 = client.get("report/avg", headers=headers1)
    top_response2 = client.get("/report/top", headers=headers2)
    avg_response2 = client.get("report/avg", headers=headers2)

    data_top1 = top_response1.json()
    data_avg1 = avg_response1.json()
    data_top2 = top_response2.json()
    data_avg2 = avg_response2.json()


    assert change_to_global1.status_code == 200
    assert change_to_global2.status_code == 200
    assert change_to_global3.status_code == 200
    assert change_to_global4.status_code == 200

# TEST USER 1
    assert top_response1.status_code == 200

    assert len(data_top1) == 3

    assert data_top1[0]["name"] == "Ryż"
    assert data_top1[0]["number_of_logs"] == 4
    assert data_top1[0]["weight_sum"] == 1280

    assert data_top1[2]["name"] == "Ziemniaki"
    assert data_top1[2]["number_of_logs"] == 2
    assert data_top1[2]["weight_sum"] == 1839


    assert avg_response1.status_code == 200
    assert len(data_avg1) == 3

    assert data_avg1[0]["name"] == "Ziemniaki"
    assert data_avg1[0]["number_of_logs"] == 2
    assert data_avg1[0]["weight_avg"] == 919.5

    assert data_avg1[1]["name"] == "Makaron"
    assert data_avg1[1]["number_of_logs"] == 3
    assert data_avg1[1]["weight_avg"] == 553.33

    assert data_avg1[2]["name"] == "Ryż"
    assert data_avg1[2]["number_of_logs"] == 4
    assert data_avg1[2]["weight_avg"] == 320.0
# TEST USER 2
    assert top_response2.status_code == 200
    assert len(data_top2) == 3

    assert data_top2[0]["name"] == "Makaron"
    assert data_top2[0]["number_of_logs"] == 2
    assert data_top2[0]["weight_sum"] == 4281

    assert data_top2[1]["name"] == "Ryż"
    assert data_top2[1]["number_of_logs"] == 1
    assert data_top2[1]["weight_sum"] == 1544

    assert avg_response2.status_code == 200
    assert len(data_avg2) == 1

    assert data_avg2[0]["name"] == "Makaron"
    assert data_avg2[0]["number_of_logs"] == 2
    assert data_avg2[0]["weight_avg"] == 2140.5