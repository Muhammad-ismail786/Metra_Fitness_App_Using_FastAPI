
from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_goal(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # Get current user's user_id
    user_response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
    )

    assert user_response.status_code == 200

    user = user_response.json()
    user_id = user["id"]

    # Create goal
    data = {
        "goal_type": "weight_loss",
        "target_value": 70,
        "current_value": 75,
        "target_date": "2026-12-31",
        "description": "Lose 5kg",
    }

    response = client.post(
        f"{settings.API_V1_STR}/users/{user_id}/goals",
        headers=normal_user_token_headers,
        json=data,
    )

    assert response.status_code == 200

    content = response.json()

    assert content["user_id"] == user_id
    assert content["goal_type"] == data["goal_type"]
    assert content["target_value"] == data["target_value"]
    assert content["current_value"] == data["current_value"]
    assert content["target_date"] == data["target_date"]
    assert content["description"] == data["description"]
    assert "id" in content


def test_get_all_goals(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/users/goals",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    content = response.json()

    assert isinstance(content, list)

def test_get_goals_by_user_id(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # Get current user's user_id
    user_response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
    )

    assert user_response.status_code == 200

    user = user_response.json()
    user_id = user["id"]

    # Get goals for the current user
    response = client.get(
        f"{settings.API_V1_STR}/users/{user_id}/goals",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    content = response.json()

    assert isinstance(content, list)

    # Verify that returned goals belong to the requested user
    for goal in content:
        assert goal["user_id"] == user_id

