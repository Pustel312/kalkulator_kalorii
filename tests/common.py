from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)