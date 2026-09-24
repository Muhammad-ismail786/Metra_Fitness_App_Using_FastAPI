from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_exercise(
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

    # Exercise data
    data = {
        "exercise_name": "Automated Test Bench Press",
        "description": "Exercise created by automated test",
        "muscle_groups": "Chest, Triceps, Shoulders",
        "instructions": "Lie on the bench and press the bar upward.",
    }

    # Fake image file for upload
    files = {
        "file": (
            "test-exercise.jpg",
            b"fake image content",
            "image/jpeg",
        )
    }

    # Create exercise
    response = client.post(
        f"{settings.API_V1_STR}/users/exercises/upload",
        headers=normal_user_token_headers,
        data=data,
        files=files,
    )

    assert response.status_code == 200

    content = response.json()

    # Verify response
    assert "id" in content
    assert content["user_id"] == user_id
    assert content["exercise_name"] == data["exercise_name"]
    assert content["description"] == data["description"]
    assert content["muscle_groups"] == data["muscle_groups"]
    assert content["instructions"] == data["instructions"]
    assert "image_url" in content

    # Delete the created exercise
    delete_response = client.delete(
        f"{settings.API_V1_STR}/users/exercises/{content['id']}",
        headers=normal_user_token_headers,
    )

    assert delete_response.status_code == 200

def test_get_all_exercises(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # Pehle ek exercise create karte hain
    data = {
        "exercise_name": "Automated GET Test Exercise",
        "description": "Exercise created for GET test",
        "muscle_groups": "Chest",
        "instructions": "Perform the exercise correctly.",
    }

    files = {
        "file": (
            "test-get-exercise.jpg",
            b"fake image content",
            "image/jpeg",
        )
    }

    create_response = client.post(
        f"{settings.API_V1_STR}/users/exercises/upload",
        headers=normal_user_token_headers,
        data=data,
        files=files,
    )

    assert create_response.status_code == 200

    created_exercise = create_response.json()
    exercise_id = created_exercise["id"]

    # Ab saare exercises GET karte hain
    response = client.get(
        f"{settings.API_V1_STR}/users/exercises",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    exercises = response.json()

    # Response list honi chahiye
    assert isinstance(exercises, list)

    # Jo exercise humne create ki thi, wo list mein honi chahiye
    exercise = next(
        (item for item in exercises if item["id"] == exercise_id),
        None,
    )

    assert exercise is not None

    # Exercise ki values verify karte hain
    assert exercise["exercise_name"] == data["exercise_name"]
    assert exercise["description"] == data["description"]
    assert exercise["muscle_groups"] == data["muscle_groups"]
    assert exercise["instructions"] == data["instructions"]

    # Test ke baad exercise delete kar dete hain
    delete_response = client.delete(
        f"{settings.API_V1_STR}/users/exercises/{exercise_id}",
        headers=normal_user_token_headers,
    )

    assert delete_response.status_code == 200

def test_update_exercise(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # Pehle ek exercise create karte hain
    data = {
        "exercise_name": "Automated Update Test Exercise",
        "description": "Original description",
        "muscle_groups": "Chest",
        "instructions": "Original instructions.",
    }

    files = {
        "file": (
            "test-update-exercise.jpg",
            b"fake image content",
            "image/jpeg",
        )
    }

    create_response = client.post(
        f"{settings.API_V1_STR}/users/exercises/upload",
        headers=normal_user_token_headers,
        data=data,
        files=files,
    )

    assert create_response.status_code == 200

    created_exercise = create_response.json()
    exercise_id = created_exercise["id"]

    # Exercise update data
    update_data = {
        "exercise_name": "Updated Exercise Name",
        "description": "Updated description",
        "muscle_groups": "Chest, Triceps",
        "instructions": "Updated instructions.",
    }

    # Exercise update karte hain
    response = client.patch(
        f"{settings.API_V1_STR}/users/exercises/{exercise_id}",
        headers=normal_user_token_headers,
        json=update_data,
    )

    assert response.status_code == 200

    updated_exercise = response.json()

    # Updated values verify karte hain
    assert updated_exercise["id"] == exercise_id
    assert updated_exercise["exercise_name"] == update_data["exercise_name"]
    assert updated_exercise["description"] == update_data["description"]
    assert updated_exercise["muscle_groups"] == update_data["muscle_groups"]
    assert updated_exercise["instructions"] == update_data["instructions"]

    # Test ke baad exercise delete kar dete hain
    delete_response = client.delete(
        f"{settings.API_V1_STR}/users/exercises/{exercise_id}",
        headers=normal_user_token_headers,
    )

    assert delete_response.status_code == 200

def test_delete_exercise(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # Pehle ek exercise create karte hain
    data = {
        "exercise_name": "Automated DELETE Test Exercise",
        "description": "Exercise created for DELETE test",
        "muscle_groups": "Legs",
        "instructions": "Perform the exercise correctly.",
    }

    files = {
        "file": (
            "test-delete-exercise.jpg",
            b"fake image content",
            "image/jpeg",
        )
    }

    create_response = client.post(
        f"{settings.API_V1_STR}/users/exercises/upload",
        headers=normal_user_token_headers,
        data=data,
        files=files,
    )

    assert create_response.status_code == 200

    created_exercise = create_response.json()
    exercise_id = created_exercise["id"]

    # Exercise delete karte hain
    response = client.delete(
        f"{settings.API_V1_STR}/users/exercises/{exercise_id}",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    content = response.json()

    # Delete response verify karte hain
    assert content["message"] == "Exercise deleted successfully"

    # Verify karte hain ke exercise ab exist nahi karti
    get_response = client.get(
        f"{settings.API_V1_STR}/users/exercises",
        headers=normal_user_token_headers,
    )

    assert get_response.status_code == 200

    exercises = get_response.json()

    assert not any(
        exercise["id"] == exercise_id
        for exercise in exercises
    )