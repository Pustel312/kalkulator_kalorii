from tests.common import client
from tests.helpers import create_test_product, create_test_log, create_test_authorization, create_test_user, login_test_user, create_test_recipe

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
                "type": "product",
                "weight": 100
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
                "type": "product",
                "weight": 100
            }
        )
    
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or expired token"
    }

def test_private_product_visible_only_to_owner(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )
    create_test_product("Ryż", 7, 1, 78, 100, headers1)
    user1_list = client.get("/products",
        headers=headers1)
    user2_list = client.get("/products",
        headers=headers2)

    data1 = user1_list.json()
    data2 = user2_list.json()

    assert user1_list.status_code == 200
    assert user2_list.status_code == 200
    assert len(data1) == 1
    assert len(data2) == 0

def test_public_product_visible_to_all(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )
    create_product = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    product_id1 = create_product.json()["id"]
    visibility_response = client.patch(f"/products/{product_id1}/visibility",
        headers=headers1,
        params={
            "is_global": True
        })

    user1_list = client.get("/products",
        headers=headers1)
    user2_list = client.get("/products",
        headers=headers2)

    data1 = user1_list.json()
    data2 = user2_list.json()

    assert visibility_response.status_code == 200
    assert user1_list.status_code == 200
    assert user2_list.status_code == 200
    assert len(data1) == 1
    assert len(data2) == 1

def test_not_own_product_patch_blocked(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )
    create_product = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    product_id = create_product.json()["id"]
    change_product = client.patch(
        f"/products/{product_id}",
        headers=headers2,
        json={
            "protein": 12
        }
    )

    assert change_product.status_code == 404

def test_not_own_product_delete_blocked(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )
    create_product = create_test_product("Ryż", 7, 1, 78, 100,headers1)
    product_id = create_product.json()["id"]
    delete_product = client.delete(
        f"/products/{product_id}",
        headers=headers2)

    assert delete_product.status_code == 404

def test_not_own_product_change_visibility_blocked(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )
    create_product = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    product_id = create_product.json()["id"]
    visibility_response = client.patch(f"/products/{product_id}/visibility",
        headers=headers2,
        params={
            "is_global": True
        })

    assert visibility_response.status_code == 404
def test_log_ownership(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )

    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers1)
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

    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers1)
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

    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers1)
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

def test_reports_ownership_top_and_avg(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    create_response_product2 = create_test_product("Makaron", 10, 3, 50, 100, headers1)
    create_response_product3 = create_test_product("Ziemniaki", 4, 0, 40, 100, headers1)
    create_response_product4 = create_test_product("Kasza", 6, 5, 60, 100, headers1)
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

def test_create_not_owned_recipe(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )

    product = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    product_id = product.json()["id"]
    response_create_recipe = create_test_recipe(product_id, "test", 2, 90, headers2)

    assert response_create_recipe.status_code == 404

def test_get_not_owned_recipe(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )

    product = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    product_id = product.json()["id"]
    create_test_recipe(product_id, "test", 2, 90, headers1)

    response_get_recipe = client.get(
        "/recipes",
        headers=headers2,
        params={
            "product_id": product_id
        })

    assert response_get_recipe.status_code == 404

def test_update_not_owned_recipe(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )

    product = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    product_id = product.json()["id"]
    create_test_recipe(product_id, "test", 2, 90, headers1)

    response_update_recipe = client.patch(
        "/recipes",
        headers=headers2,
        params={
            "product_id": product_id
        },
        json={
            "servings": 5
        }
    )

    response_get_recipe = client.get(
        "/recipes",
        headers=headers1,
        params={
            "product_id": product_id
        })
    data = response_get_recipe.json()

    assert response_update_recipe.status_code == 404
    assert response_get_recipe.status_code == 200
    assert data["servings"] == 2

def test_delete_not_owned_recipe(clean_db):
    headers1 = create_test_authorization(
        "test1@example.com",
        "TestPassword123"
    )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )

    product = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    product_id = product.json()["id"]
    create_test_recipe(product_id, "test", 2, 90, headers1)

    response_delete_recipe = client.delete(
        "/recipes",
        headers=headers2,
        params={
            "product_id": product_id
        }
    )

    response_get_recipe = client.get(
        "/recipes",
        headers=headers1,
        params={
            "product_id": product_id
        })

    assert response_delete_recipe.status_code == 404
    assert response_get_recipe.status_code == 200