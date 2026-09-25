from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import (
    Exercise,
    FoodLog,
    Goal,
    Item,
    Profile,
    Recipe,
    User,
    WorkoutPlan,
)
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session]:
    with Session(engine) as session:
        init_db(session)
        yield session

        # Delete child records first
        session.execute(delete(Item))
        session.execute(delete(Profile))
        session.execute(delete(Goal))
        session.execute(delete(WorkoutPlan))
        session.execute(delete(Exercise))
        session.execute(delete(FoodLog))
        session.execute(delete(Recipe))

        # Delete users after all related records
        session.execute(delete(User))

        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(
    client: TestClient,
) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(
    client: TestClient,
    db: Session,
) -> dict[str, str]:
    return authentication_token_from_email(
        client=client,
        email=settings.EMAIL_TEST_USER,
        db=db,
    )