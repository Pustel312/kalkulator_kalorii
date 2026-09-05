from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.api import app
from src.database import get_db
from src.models import Base

test_engine = create_engine("sqlite:///test.db")
Base.metadata.create_all(test_engine)

def override_get_db():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_healthcheck(): 
    response = client.get("/healthcheck")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Server is running smoothly"
    }

def test_create_product():
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

def test_delete_product():
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

def test_delete_product_not_found():
    response = client.delete(
        "/products/100"
    )

    assert response.status_code == 404
    assert response.json() == {
    "detail": "Product not found"
    }