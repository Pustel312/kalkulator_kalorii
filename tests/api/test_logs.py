from tests.common import client
from tests.helpers import create_test_product, create_test_log, create_test_authorization

# # # # # # # # # # # # # # # # # # # # # # # # LOGS TESTS # # # # # # # # # # # # # # # # # # # # # # # #

def test_create_log(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers)
    product_id = create_response_product1.json()["id"]
    create_response_log1 = create_test_log(product_id, 200, headers)

    assert create_response_log1.status_code == 200

def test_get_log(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers)
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
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers)
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
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers)
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

def test_create_log_macros_normalization(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 50, 25, 100, 250, headers)
    product_id = create_response_product1.json()["id"]
    create_response_log1 = create_test_log(product_id, 250, headers)

    log_data = create_response_log1.json()

    assert create_response_log1.status_code == 200


    assert log_data["protein"] == 50
    assert log_data["fat"] == 25
    assert log_data["carbs"] == 100
    assert log_data["calories"] == 825