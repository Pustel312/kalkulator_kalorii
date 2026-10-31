from tests.common import client
from tests.helpers import create_test_product, create_test_log, create_test_authorization, create_test_recipe

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
            "type": "product",
            "weight": 100
        }
    )

    assert response.status_code == 200


def test_create_product_multiple(clean_db):
    headers=create_test_authorization()
    create_test_product("Ryż", 7, 1, 78, 100, headers)
    create_test_product("Makaron", 10, 3, 50, 100, headers)

    response1 = client.get("/products", headers=headers)

    assert response1.status_code == 200
    assert len(response1.json()) == 2

def test_product_search(clean_db):
    headers=create_test_authorization()
    create_test_product("Ryż", 7, 1, 78, 100, headers)
    create_test_product("Kurczak", 20, 6, 25, 100, headers)

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
    create_response1 = create_test_product("Ryż", 7, 1, 78, 100, headers)
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
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id = create_response_product1.json()["id"]
    response_delete1 = client.delete(f"/products/{product_id}", headers=headers)
    create_response_log1 = create_test_log(product_id, 200, headers)

    assert response_delete1.status_code == 200
    assert create_response_log1.status_code == 404

def test_soft_delete_product_same_name(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id1 = create_response_product1.json()["id"]
    create_response_product2 = create_test_product("Ryż", 7, 1, 78, 100, headers)

    assert create_response_product2.status_code == 409

    client.delete(f"/products/{product_id1}", headers=headers)
    create_response_product3 = create_test_product("Ryż", 7, 1, 78, 100, headers)

    assert create_response_product3.status_code == 200

def test_update(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers)
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
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers)
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

def test_product_macros_calculations(clean_db):
    response = client.post(
        "/products",
        headers=create_test_authorization(),
        json={
            "name": "test_product",
            "protein": 50,
            "fat": 25,
            "carbs": 100,
            "type": "product",
            "weight": 250
        }
    )
    data = response.json()

    response.status_code == 200

    assert data["protein"] == 20
    assert data["fat"] == 10
    assert data["carbs"] == 40
    assert data["calories"] == 330

# # # # # # # # # # # # # # # # # # # # # # # # RECIPES TESTS # # # # # # # # # # # # # # # # # # # # # # # #

def test_create_recipe(clean_db):
    headers=create_test_authorization()
    product = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id = product.json()["id"]
    response = client.post(
        "/recipes",
        headers=headers,
        json={
            "product_id": product_id,
            "recipe": "test",
            "servings": 2,
            "preparation_time": 90
        }
    )

    assert response.status_code == 200

def test_create_recipe_without_prep_time(clean_db):
    headers=create_test_authorization()
    product = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id = product.json()["id"]
    response = client.post(
        "/recipes",
        headers=headers,
        json={
            "product_id": product_id,
            "recipe": "test",
            "servings": 2,
        }
    )

    assert response.status_code == 200
    assert response.json()["preparation_time"] is None

def test_create_recipe_nonexisting_product(clean_db):
    headers=create_test_authorization()
    response = create_test_recipe(1, "test", 2, 90, headers)

    assert response.status_code == 404

def test_create_second_recipe_for_same_product(clean_db):
    headers=create_test_authorization()
    product = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id = product.json()["id"]
    response1 = create_test_recipe(product_id, "test", 2, 90, headers)
    response2 = create_test_recipe(product_id, "test", 2, 90, headers)

    assert response1.status_code == 200
    assert response2.status_code == 409

def test_create_recipe_nonactive_product(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id = create_response_product1.json()["id"]
    response_delete = client.delete(f"/products/{product_id}", headers=headers)
    response_create_recipe = create_test_recipe(product_id, "test", 2, 90, headers)

    assert response_delete.status_code == 200
    assert response_create_recipe.status_code == 404

def test_get_recipe(clean_db):
    headers=create_test_authorization()
    product = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id = product.json()["id"]
    response1 = create_test_recipe(product_id, "test", 2, 90, headers)
    data = response1.json()

    response_get_recipe = client.get(
        "/recipes",
        headers=headers,
        params={
            "product_id": product_id
        })

    assert response_get_recipe.status_code == 200
    assert data["recipe"] == "test"
    assert data["servings"] == 2

def test_get_recipe_nonexisting_product(clean_db):
    headers=create_test_authorization()
    response_get_recipe = client.get(
        "/recipes",
        headers=headers,
        params={
            "product_id": 1
        })

    assert response_get_recipe.status_code == 404

def test_get_recipe_product_without_recipe(clean_db):
    headers=create_test_authorization()
    product = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id = product.json()["id"]

    response_get_recipe = client.get(
        "/recipes",
        headers=headers,
        params={
            "product_id": product_id
        })

    assert response_get_recipe.status_code == 404

def test_update_recipe(clean_db):
    headers=create_test_authorization()
    product = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id = product.json()["id"]
    create_test_recipe(product_id, "test", 2, 90, headers)

    response_update_recipe = client.patch(
        "/recipes",
        headers=headers,
        params={
            "product_id": product_id
        },
        json={
            "servings": 5
        }
    )

    data = response_update_recipe.json()

    assert response_update_recipe.status_code == 200
    assert data["servings"] == 5
    assert data["preparation_time"] == 90

def test_update_recipe_prep_time_null(clean_db):
    headers=create_test_authorization()
    product = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id = product.json()["id"]
    create_test_recipe(product_id, "test", 2, 90, headers)

    response_update_recipe = client.patch(
        "/recipes",
        headers=headers,
        params={
            "product_id": product_id
        },
        json={
            "preparation_time": None
        }
    )

    assert response_update_recipe.status_code == 200
    assert response_update_recipe.json()["preparation_time"] is None

def test_update_recipe_negative_value(clean_db):
    headers=create_test_authorization()
    product = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id = product.json()["id"]
    create_test_recipe(product_id, "test", 2, 90, headers)

    response_update_recipe = client.patch(
        "/recipes",
        headers=headers,
        params={
            "product_id": product_id
        },
        json={
            "servings": -5
        }
    )

    data = response_update_recipe.json()

    assert response_update_recipe.status_code == 422

def test_delete_recipe(clean_db):
    headers=create_test_authorization()
    product = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id = product.json()["id"]
    create_test_recipe(product_id, "test", 2, 90, headers)

    response_delete_recipe = client.delete(
        "/recipes",
        headers=headers,
        params={
            "product_id": product_id
        }
    )
    response_get_recipe = client.get(
        "/recipes",
        headers=headers,
        params={
            "product_id": product_id
        })

    response_get_product = client.get(
        "/products",
        headers=headers,
        )

    data = response_get_product.json()
    assert response_delete_recipe.status_code == 200
    assert response_delete_recipe.json() == {
        "status": "ok", "message": "Recipe is deleted"
    }
    assert response_get_recipe.status_code == 404
    assert data[0]["id"] == product_id


def test_delete_recipe_nonexisting(clean_db):
    headers=create_test_authorization()
    product = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id = product.json()["id"]

    response_delete_recipe = client.delete(
        "/recipes",
        headers=headers,
        params={
            "product_id": product_id
        }
    )

    assert response_delete_recipe.status_code == 404
