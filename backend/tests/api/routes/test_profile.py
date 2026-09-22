from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_profile(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    data = {
        "date_of_birth": "1999-01-01",
        "gender": "male",
        "height": 175,
        "weight": 75,
        "activity_level": "moderate",
    }

    response = client.post(
        f"{settings.API_V1_STR}/users/profile",
        headers=normal_user_token_headers,
        json=data,
    )

    assert response.status_code == 200

    content = response.json()

    assert content["date_of_birth"] == data["date_of_birth"]
    assert content["gender"] == data["gender"]
    assert content["height"] == data["height"]
    assert content["weight"] == data["weight"]
    assert content["activity_level"] == data["activity_level"]
    assert "id" in content
    assert "user_id" in content


def test_get_profile(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/users/profile",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    content = response.json()

    assert "id" in content
    assert "user_id" in content
    assert content["date_of_birth"] == "1999-01-01"
    assert content["gender"] == "male"
    assert content["height"] == 175
    assert content["weight"] == 75
    assert content["activity_level"] == "moderate"

def test_update_profile(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # First, get the current profile to get the user_id
    get_response = client.get(
        f"{settings.API_V1_STR}/users/profile",
        headers=normal_user_token_headers,
    )

    assert get_response.status_code == 200

    profile = get_response.json()
    user_id = profile["user_id"]

    # Update the profile
    data = {
        "weight": 70,
        "activity_level": "active",
    }

    response = client.patch(
        f"{settings.API_V1_STR}/users/{user_id}/profile",
        headers=normal_user_token_headers,
        json=data,
    )

    assert response.status_code == 200

    content = response.json()

    assert content["user_id"] == user_id
    assert content["weight"] == data["weight"]
    assert content["activity_level"] == data["activity_level"]

