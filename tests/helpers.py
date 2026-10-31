from src.enums import ProductType
from tests.common import client
from datetime import date as Date
from sqlalchemy.orm import Session
from tests.conftest import test_engine
from src.models import Log

# # # # # # # # # # # # # # # # # # # # # # # # HELPERS - CREATE # # # # # # # # # # # # # # # # # # # # # # # #

def create_test_product(name, protein, fat, carbs, weight, headers, product_type=ProductType.product
    ):
    response = client.post(
        "/products",
        headers=headers,
        json={
            "name": name,
            "type": product_type,
            "protein": protein,
            "fat": fat,
            "carbs": carbs,
            "weight": weight
        }
    )
    return response

def create_test_recipe(product_id, recipe, servings, preparation_time, headers):
    response = client.post(
        "/recipes",
        headers=headers,
        json={
            "product_id": product_id,
            "recipe": recipe,
            "servings": servings,
            "preparation_time": preparation_time
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

def create_userprofile(headers, sex, height, weight, birth_date, activity_level, goal):

    response = client.post("/users/me/profile", 
        headers=headers,
        json={
            "sex": sex,
            "height": height,
            "weight": weight,
            "birth_date": birth_date,
            "activity_level": activity_level,
            "goal": goal
        })

    return response

# # # # # # # # # # # # # # # # # # # # # # # # HELPERS - MODIFY # # # # # # # # # # # # # # # # # # # # # # # #

def modify_test_log_date(log_id: int, target_date: Date):
    with Session(test_engine) as session:
        log = session.get(Log, log_id)
        log.date = target_date
        session.commit()