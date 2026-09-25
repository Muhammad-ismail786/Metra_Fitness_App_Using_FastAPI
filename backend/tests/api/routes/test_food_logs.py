from fastapi.testclient import TestClient
from unittest.mock import patch

from app.core.config import settings


def test_create_food_log(
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

    # Food log data
    data = {
        "log_date": "2026-09-25",
        "quantity": "1",
        "entry_method": "ai",
    }

    # Fake image file
    files = {
        "file": (
            "test-food.jpg",
            b"fake image content",
            "image/jpeg",
        )
    }

    # Gemini ko mock karte hain
    with patch(
        "app.api.routes.food_logs.analyze_food_image"
    ) as mock_analyze_food_image:

        mock_analyze_food_image.return_value = {
            "food_name": "Automated Test Chicken",
            "quantity": 1,
            "calories": 300,
            "protein_g": 20,
            "carbs_g": 15,
            "fat_g": 18,
        }

        # Create food log
        response = client.post(
            f"{settings.API_V1_STR}/users/food-logs/upload",
            headers=normal_user_token_headers,
            data=data,
            files=files,
        )

    assert response.status_code == 200

    content = response.json()

    # Verify basic response
    assert "id" in content
    assert content["user_id"] == user_id

    # Verify food data
    assert content["food_name"] == "Automated Test Chicken"
    assert content["log_date"] == "2026-09-25"
    assert content["quantity"] == 1
    assert content["entry_method"] == "ai"

    # Verify nutrition
    assert content["total_calories"] == 300
    assert content["total_protein_g"] == 20
    assert content["total_carbs_g"] == 15
    assert content["total_fat_g"] == 18

    # Verify AI detected items
    assert content["ai_detected_items"] == [
        "Automated Test Chicken"
    ]

    # Image URL should exist
    assert "image_url" in content

def test_get_food_logs(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # Pehle ek food log create karte hain
    data = {
        "log_date": "2026-09-25",
        "quantity": "1",
        "entry_method": "ai",
    }

    files = {
        "file": (
            "test-get-food.jpg",
            b"fake image content",
            "image/jpeg",
        )
    }

    # Gemini ko mock karte hain
    with patch(
        "app.api.routes.food_logs.analyze_food_image"
    ) as mock_analyze_food_image:

        mock_analyze_food_image.return_value = {
            "food_name": "Automated GET Test Food",
            "quantity": 1,
            "calories": 400,
            "protein_g": 25,
            "carbs_g": 30,
            "fat_g": 15,
        }

        create_response = client.post(
            f"{settings.API_V1_STR}/users/food-logs/upload",
            headers=normal_user_token_headers,
            data=data,
            files=files,
        )

    assert create_response.status_code == 200

    created_food_log = create_response.json()
    food_log_id = created_food_log["id"]

    # Ab GET Food Logs call karte hain
    response = client.get(
        f"{settings.API_V1_STR}/users/food-logs",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    food_logs = response.json()

    # Response list honi chahiye
    assert isinstance(food_logs, list)

    # Jo food log create kiya tha,
    # wo GET response mein hona chahiye
    food_log = next(
        (
            item
            for item in food_logs
            if item["id"] == food_log_id
        ),
        None,
    )

    assert food_log is not None

    # Food log values verify karte hain
    assert food_log["food_name"] == "Automated GET Test Food"
    assert food_log["log_date"] == "2026-09-25"
    assert food_log["quantity"] == 1
    assert food_log["entry_method"] == "ai"

    # Nutrition verify karte hain
    assert food_log["total_calories"] == 400
    assert food_log["total_protein_g"] == 25
    assert food_log["total_carbs_g"] == 30
    assert food_log["total_fat_g"] == 15

    # AI detected items verify karte hain
    assert food_log["ai_detected_items"] == [
        "Automated GET Test Food"
    ]