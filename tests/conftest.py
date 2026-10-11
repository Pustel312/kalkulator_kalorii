from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.api.app import app
from src.database.session import get_db
from src.models import Base

import pytest

import os
from dotenv import load_dotenv

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
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



