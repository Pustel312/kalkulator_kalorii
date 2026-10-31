from tests.common import client
from tests.helpers import create_test_product, create_test_log, create_test_authorization, create_userprofile, modify_test_log_date

from datetime import date as Date

# # # # # # # # # # # # # # # # # # # # # # # # REPORTS # # # # # # # # # # # # # # # # # # # # # # # #

def test_sum_day(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    product_id = create_response_product1.json()["id"]
    create_test_log(product_id, 100, headers1)
    create_test_log(product_id, 150, headers1)



    create_response_daily = client.get(
        "/reports/period-summary",
        headers=headers1,
        params={
            "target_date": Date.today(),
            "period": "day"}   
        )
    daily_data = create_response_daily.json()

    assert create_response_daily.status_code == 200
    assert daily_data["log_count"] == 2
    assert daily_data["bmr"] == 1915
    assert daily_data["tdee"] == 3303
    assert daily_data["target_calories"] == 3303

    assert daily_data["protein_eaten"] == 17.5
    assert daily_data["fat_eaten"] == 2.5
    assert daily_data["carbs_eaten"] == 195.0
    assert daily_data["protein_min"] == 124
    assert daily_data["protein_max"] == 206
    assert daily_data["fat_min"] == 73
    assert daily_data["fat_max"] == 110
    assert daily_data["carbs_min"] == 372
    assert daily_data["carbs_max"] == 495

def test_sum_day_few_products(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    create_response_product2 = create_test_product("Makaron", 3, 5, 50, 100, headers1)
    product_id1 = create_response_product1.json()["id"]
    product_id2 = create_response_product2.json()["id"]
    create_test_log(product_id1, 100, headers1)
    create_test_log(product_id1, 150, headers1)
    create_test_log(product_id2, 100, headers1)
    create_test_log(product_id2, 300, headers1)
    create_test_log(product_id2, 200, headers1)

    create_response_daily = client.get(
        "/reports/period-summary",
        headers=headers1,
        params={
            "target_date": Date.today(),
            "period": "day"
            }   
        )
    daily_data = create_response_daily.json()

    assert create_response_daily.status_code == 200
    assert daily_data["log_count"] == 5
    assert daily_data["protein_eaten"] == 35.5
    assert daily_data["fat_eaten"] == 32.5
    assert daily_data["carbs_eaten"] == 495.0

def test_sum_day_exceeded_calories(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    product_id = create_response_product1.json()["id"]
    create_test_log(product_id, 1000, headers1)
    create_test_log(product_id, 1500, headers1)



    create_response_daily = client.get(
        "/reports/period-summary",
        headers=headers1,
        params={
            "target_date": Date.today(),
            "period": "day"
            }   
        )
    daily_data = create_response_daily.json()

    assert create_response_daily.status_code == 200
    assert daily_data["target_calories"] == 3303
    assert daily_data["remaining_calories"] == 0
    assert daily_data["exceeded_calories"] == 5422
def test_sum_day_zero_logs(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    create_response_daily = client.get(
        "/reports/period-summary",
        headers=headers1,
        params={
            "target_date": Date.today(),
            "period": "day"
            }   
        )
    daily_data = create_response_daily.json()

    assert create_response_daily.status_code == 200
    assert daily_data["log_count"] == 0
    assert daily_data["fat_eaten"] == 0
    assert daily_data["target_calories"] == 3303
    assert daily_data["remaining_calories"] == 3303
    assert daily_data["exceeded_calories"] == 0

def test_sum_day_ownership(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    create_userprofile(headers2, "male", 170, "83.2", "2005-07-22", "light", "gain_0_1")

    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    create_response_product2 = create_test_product("Makaron", 3, 5, 50, 100, headers1)
    create_response_product3 = create_test_product("Kurczak", 50, 1, 78, 100, headers2)
    product_id1 = create_response_product1.json()["id"]
    product_id2 = create_response_product2.json()["id"]
    product_id3 = create_response_product3.json()["id"]

    create_test_log(product_id1, 100, headers1)
    create_test_log(product_id1, 150, headers1)
    create_test_log(product_id2, 100, headers1)
    create_test_log(product_id2, 300, headers1)
    create_test_log(product_id2, 200, headers1)
    create_test_log(product_id3, 1000, headers2)


    create_response_daily1 = client.get(
        "/reports/period-summary",
        headers=headers1,
        params={
            "target_date": Date.today(),
            "period": "day"
            }   
        )
    create_response_daily2 = client.get(
        "/reports/period-summary",
        headers=headers2,
        params={
            "target_date": Date.today(),
            "period": "day"
            }   
        )
    daily_data1 = create_response_daily1.json()
    daily_data2 = create_response_daily2.json()

    assert create_response_daily1.status_code == 200
    assert create_response_daily2.status_code == 200

    assert daily_data1["target_calories"] == 3303
    assert daily_data2["target_calories"] == 2577

    assert daily_data1["log_count"] == 5
    assert daily_data1["protein_eaten"] == 35.5
    assert daily_data1["fat_eaten"] == 32.5
    assert daily_data1["carbs_eaten"] == 495.0

    assert daily_data2["log_count"] == 1
    assert daily_data2["protein_eaten"] == 500.0

def test_top_and_average_products(clean_db):
    headers=create_test_authorization()
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers)
    create_response_product2 = create_test_product("Makaron", 10, 3, 50, 100, headers)
    create_response_product3 = create_test_product("Ziemniaki", 4, 0, 40, 100, headers)
    create_response_product4 = create_test_product("Kasza", 6, 5, 60, 100, headers)
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


def test_period_summary_week(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    product_id = create_response_product1.json()["id"]
    log1 = create_test_log(product_id, 100, headers1)
    log2 = create_test_log(product_id, 150, headers1)
    log3 = create_test_log(product_id, 100, headers1)

    modify_test_log_date(log1.json()["id"], Date(2026, 10, 31))
    modify_test_log_date(log2.json()["id"], Date(2026, 10, 28))
    modify_test_log_date(log3.json()["id"], Date(2026, 10, 26))


    create_response_daily = client.get(
        "/reports/period-summary",
        headers=headers1,
        params={
            "target_date": Date(2026, 10, 31),
            "period": "week"}   
        )
    daily_data = create_response_daily.json()

    assert create_response_daily.status_code == 200
    assert daily_data["log_count"] == 3
    assert daily_data["days_with_logs"] == 3
    assert daily_data["days_without_logs"] == 4

    assert daily_data["bmr"] == 1915
    assert daily_data["tdee"] == 3303

    assert daily_data["target_calories"] == 23121

    assert daily_data["protein_eaten"] == 24.5
    assert daily_data["fat_eaten"] == 3.5
    assert daily_data["carbs_eaten"] == 273.0

    assert daily_data["protein_min"] == 868
    assert daily_data["protein_max"] == 1442
    assert daily_data["fat_min"] == 511
    assert daily_data["fat_max"] == 770
    assert daily_data["carbs_min"] == 2604
    assert daily_data["carbs_max"] == 3465

    assert daily_data["remaining_calories"] == 21900
    assert daily_data["exceeded_calories"] == 0
    assert daily_data["avg_calories_per_logged_day"] == 407

def test_period_summary_week_no_logs(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")

    create_response_daily = client.get(
        "/reports/period-summary",
        headers=headers1,
        params={
            "target_date": Date(2026, 10, 31),
            "period": "week"}   
        )
    daily_data = create_response_daily.json()

    assert create_response_daily.status_code == 200
    assert daily_data["log_count"] == 0
    assert daily_data["days_with_logs"] == 0
    assert daily_data["days_without_logs"] == 7

    assert daily_data["bmr"] == 1915
    assert daily_data["tdee"] == 3303

    assert daily_data["target_calories"] == 23121

    assert daily_data["protein_eaten"] == 0
    assert daily_data["fat_eaten"] == 0
    assert daily_data["carbs_eaten"] == 0

    assert daily_data["protein_min"] == 868
    assert daily_data["protein_max"] == 1442
    assert daily_data["fat_min"] == 511
    assert daily_data["fat_max"] == 770
    assert daily_data["carbs_min"] == 2604
    assert daily_data["carbs_max"] == 3465

    assert daily_data["remaining_calories"] == 23121
    assert daily_data["exceeded_calories"] == 0
    assert daily_data["avg_calories_per_logged_day"] == 0

def test_period_summary_month(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    create_response_product1 = create_test_product("Ryż", 7, 1, 78, 100, headers1)
    product_id = create_response_product1.json()["id"]
    log1 = create_test_log(product_id, 1636, headers1)
    log2 = create_test_log(product_id, 150, headers1)
    log3 = create_test_log(product_id, 500, headers1)
    log4 = create_test_log(product_id, 1200, headers1)
    log5 = create_test_log(product_id, 3000, headers1)
    log6 = create_test_log(product_id, 2536, headers1)
    log7 = create_test_log(product_id, 14646, headers1)


    modify_test_log_date(log1.json()["id"], Date(2026, 10, 5))
    modify_test_log_date(log2.json()["id"], Date(2026, 10, 12))
    modify_test_log_date(log3.json()["id"], Date(2026, 10, 1))
    modify_test_log_date(log4.json()["id"], Date(2026, 10, 31))
    modify_test_log_date(log5.json()["id"], Date(2026, 10, 27))
    modify_test_log_date(log6.json()["id"], Date(2026, 10, 26))
    modify_test_log_date(log7.json()["id"], Date(2026, 11, 1))

    create_response_daily = client.get(
        "/reports/period-summary",
        headers=headers1,
        params={
            "target_date": Date(2026, 10, 31),
            "period": "month"}   
        )
    daily_data = create_response_daily.json()

    assert create_response_daily.status_code == 200

    assert daily_data["log_count"] == 6
    assert daily_data["days_with_logs"] == 6
    assert daily_data["days_without_logs"] == 25

    assert daily_data["bmr"] == 1915
    assert daily_data["tdee"] == 3303

    assert daily_data["target_calories"] == 102393

    assert daily_data["protein_eaten"] == 631.54
    assert daily_data["fat_eaten"] == 90.22
    assert daily_data["carbs_eaten"] == 7037.16

    assert daily_data["protein_min"] == 3844
    assert daily_data["protein_max"] == 6386
    assert daily_data["fat_min"] == 2263
    assert daily_data["fat_max"] == 3410
    assert daily_data["carbs_min"] == 11532
    assert daily_data["carbs_max"] == 15345

    assert daily_data["remaining_calories"] == 70906
    assert daily_data["exceeded_calories"] == 0
    assert daily_data["avg_calories_per_logged_day"] == 5247

    assert daily_data["date_from"] == "2026-10-01"
    assert daily_data["date_to"] == "2026-10-31"