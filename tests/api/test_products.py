from tests.common import client
from tests.helpers import create_test_product, create_test_log, create_test_authorization

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