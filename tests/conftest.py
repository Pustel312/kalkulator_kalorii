import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine import make_url

from src.api.app import app
from src.database.session import get_db
from src.models import Base

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is not configured")

database_name = make_url(TEST_DATABASE_URL).database

if database_name != "calorie_app_test":
    raise RuntimeError("Tests must user the test database!")

test_engine = create_engine(TEST_DATABASE_URL)
Base.metadata.create_all(test_engine)


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
