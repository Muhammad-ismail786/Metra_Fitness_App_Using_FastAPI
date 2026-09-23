from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_user_preference(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # Create user preference
    data = {
        "preferred_workout_duration": 65,
        "workouts_per_week": 5,
        "available_equipment": [
            "dumbbells",
            "resistance bands",
            "treadmill",
        ],
        "workout_location": "home",
    }

    response = client.post(
        f"{settings.API_V1_STR}/users/preferences",
        headers=normal_user_token_headers,
        json=data,
    )

    assert response.status_code == 200

    content = response.json()

    assert content["preferred_workout_duration"] == data["preferred_workout_duration"]
    assert content["workouts_per_week"] == data["workouts_per_week"]
    assert content["available_equipment"] == data["available_equipment"]
    assert content["workout_location"] == data["workout_location"]
    assert "id" in content
    assert "user_id" in content


def test_get_all_user_preferences(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/users/preferences",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    content = response.json()

    assert isinstance(content, list)


def test_get_user_preferences_by_user_id(
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

    # Get preferences for the current user
    response = client.get(
        f"{settings.API_V1_STR}/users/{user_id}/preferences",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    content = response.json()

    assert isinstance(content, list)

    # Verify that returned preferences belong to the requested user
    for preference in content:
        assert preference["user_id"] == user_id


def test_delete_user_preference(
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

    # Delete user preference
    response = client.delete(
        f"{settings.API_V1_STR}/users/{user_id}/preferences",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    content = response.json()

    assert content["message"] == "User preference deleted successfully"