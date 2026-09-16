import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

os.environ["DB_CONNECTOR"] = "sqlite://"

import app
from person import Person


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

app.engine = test_engine


@pytest.fixture(autouse=True)
def database():
    Person.metadata.create_all(bind=test_engine)

    yield

    Person.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    with TestClient(app.app) as test_client:
        yield test_client