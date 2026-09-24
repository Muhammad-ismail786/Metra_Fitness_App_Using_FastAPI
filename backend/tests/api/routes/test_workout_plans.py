from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_workout_plan(
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

    # Create workout plan
    data = {
        "plan_name": "Automated Test Workout Plan",
        "duration": 4,
        "weekly_schedule": {
            "monday": "Chest and Triceps",
            "wednesday": "Back and Biceps",
            "friday": "Legs",
        },
        "exercises": [
            {
                "name": "Push Ups",
                "sets": 3,
                "reps": 12,
            },
            {
                "name": "Squats",
                "sets": 3,
                "reps": 15,
            },
        ],
        "status": "active",
    }

    response = client.post(
        f"{settings.API_V1_STR}/users/workout-plans",
        headers=normal_user_token_headers,
        json=data,
    )

    assert response.status_code == 200

    content = response.json()

    assert "id" in content
    assert content["user_id"] == user_id
    assert content["plan_name"] == data["plan_name"]
    assert content["duration"] == data["duration"]
    assert content["weekly_schedule"] == data["weekly_schedule"]
    assert content["exercises"] == data["exercises"]
    assert content["status"] == data["status"]


def test_get_all_workout_plans(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/users/workout-plans",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    content = response.json()

    assert isinstance(content, list)

def test_get_workout_plan_by_id(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # Create a workout plan first
    data = {
        "plan_name": "Test Plan For Get By ID",
        "duration": 4,
        "weekly_schedule": {
            "monday": "Chest",
            "wednesday": "Back",
            "friday": "Legs",
        },
        "exercises": [
            {
                "name": "Push Ups",
                "sets": 3,
                "reps": 12,
            }
        ],
        "status": "active",
    }

    create_response = client.post(
        f"{settings.API_V1_STR}/users/workout-plans",
        headers=normal_user_token_headers,
        json=data,
    )

    assert create_response.status_code == 200

    created_plan = create_response.json()
    workout_plan_id = created_plan["id"]

    # Get workout plan by ID
    response = client.get(
        f"{settings.API_V1_STR}/users/workout-plans/{workout_plan_id}",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    content = response.json()

    assert content["id"] == workout_plan_id
    assert content["plan_name"] == data["plan_name"]
    assert content["duration"] == data["duration"]
    assert content["weekly_schedule"] == data["weekly_schedule"]
    assert content["exercises"] == data["exercises"]
    assert content["status"] == data["status"]


def test_update_workout_plan(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # Create a workout plan first
    data = {
        "plan_name": "Workout Plan Before Update",
        "duration": 4,
        "weekly_schedule": {
            "monday": "Chest",
            "wednesday": "Back",
            "friday": "Legs",
        },
        "exercises": [
            {
                "name": "Push Ups",
                "sets": 3,
                "reps": 12,
            }
        ],
        "status": "active",
    }

    create_response = client.post(
        f"{settings.API_V1_STR}/users/workout-plans",
        headers=normal_user_token_headers,
        json=data,
    )

    assert create_response.status_code == 200

    created_plan = create_response.json()
    workout_plan_id = created_plan["id"]

    # Update the workout plan
    update_data = {
        "plan_name": "Updated Workout Plan",
        "duration": 8,
        "status": "inactive",
    }

    response = client.patch(
        f"{settings.API_V1_STR}/users/workout-plans/{workout_plan_id}",
        headers=normal_user_token_headers,
        json=update_data,
    )

    assert response.status_code == 200

    content = response.json()

    # Verify updated values
    assert content["id"] == workout_plan_id
    assert content["plan_name"] == update_data["plan_name"]
    assert content["duration"] == update_data["duration"]
    assert content["status"] == update_data["status"]

    # Verify values that were not updated remain unchanged
    assert content["weekly_schedule"] == data["weekly_schedule"]
    assert content["exercises"] == data["exercises"]

def test_delete_workout_plan(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # Create a workout plan first
    data = {
        "plan_name": "Workout Plan To Delete",
        "duration": 4,
        "weekly_schedule": {
            "monday": "Chest",
            "wednesday": "Back",
            "friday": "Legs",
        },
        "exercises": [
            {
                "name": "Push Ups",
                "sets": 3,
                "reps": 12,
            }
        ],
        "status": "active",
    }

    create_response = client.post(
        f"{settings.API_V1_STR}/users/workout-plans",
        headers=normal_user_token_headers,
        json=data,
    )

    assert create_response.status_code == 200

    created_plan = create_response.json()
    workout_plan_id = created_plan["id"]

    # Delete the workout plan
    response = client.delete(
        f"{settings.API_V1_STR}/users/workout-plans/{workout_plan_id}",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    content = response.json()

    assert content["message"] == "Workout plan deleted successfully"

    # Verify that the workout plan no longer exists
    get_response = client.get(
        f"{settings.API_V1_STR}/users/workout-plans/{workout_plan_id}",
        headers=normal_user_token_headers,
    )

    assert get_response.status_code == 404