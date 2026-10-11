from tests.common import client
from tests.helpers import create_test_authorization, create_userprofile, create_test_user, login_test_user

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

# # # # # # # # # # # # # # # # # # # # # # # # USERPROFILE # # # # # # # # # # # # # # # # # # # # # # # #

def test_create_userprofile(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )

    create_userprofile = client.post("/users/me/profile", 
        headers=headers1,
        json={
            "sex": "male",
            "height": 180,
            "weight": 90,
            "birth_date": "2003-06-25",
            "activity_level": "high",
            "goal": "maintenance"
        })

    data = create_userprofile.json()

    assert create_userprofile.status_code == 200
    assert data["sex"] == "male"
    assert data["height"] == 180
    assert data["weight"] == "90.0"
    assert data["birth_date"] == "2003-06-25"
    assert data["activity_level"] == "high"
    assert data["goal"] == "maintenance"

def test_create_userprofile_multiple_userprofiles(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    create_userprofile1 = create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    create_userprofile2 = create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")

    assert create_userprofile1.status_code == 200
    assert create_userprofile2.status_code == 409

def test_get_userprofile(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    get_userprofile1 = client.get("/users/me/profile", headers=headers1)

    data = get_userprofile1.json()

    assert get_userprofile1.status_code == 200 
    assert data["sex"] == "male"
    assert data["goal"] == "maintenance"

def test_get_userprofile_wrong_user(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    get_userprofile1 = client.get("/users/me/profile", headers=headers2)    

    assert get_userprofile1.status_code == 404

def test_update_userprofile(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    update_userprofile1 = client.patch("/users/me/profile", headers=headers1,
    json={
        "height": 185
    })

    data = update_userprofile1.json()

    assert update_userprofile1.status_code == 200
    assert data["height"] == 185
    assert data["weight"] == "90.0"

def test_update_userprofile_multiple_fields(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    update_userprofile1 = client.patch("/users/me/profile", headers=headers1,
    json={
        "height": 185,
        "weight": "95.3"
    })

    data = update_userprofile1.json()

    assert update_userprofile1.status_code == 200
    assert data["height"] == 185
    assert data["weight"] == "95.3"
    assert data["sex"] == "male"

def test_update_userprofile_wrong_data_type(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    update_userprofile1 = client.patch("/users/me/profile", headers=headers1,
    json={
        "height": "str"
    })

    assert update_userprofile1.status_code == 422

def test_update_userprofile_wrong_user(clean_db):
    headers1 = create_test_authorization(
            "test1@example.com",
            "TestPassword123"
        )
    headers2 = create_test_authorization(
        "test2@example.com",
        "TestPassword321"
    )
    create_userprofile(headers1, "male", 180, "90.0", "2003-06-25", "high", "maintenance")
    update_userprofile1 = client.patch("/users/me/profile", headers=headers2,
    json={
        "height": 185
    })

    assert update_userprofile1.status_code == 404