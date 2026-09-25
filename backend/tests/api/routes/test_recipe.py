from fastapi.testclient import TestClient
from unittest.mock import patch

from app.core.config import settings


def test_create_recipe(
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

    # Recipe data
    data = {
        "recipe_name": "Automated Test Chicken Pasta",
        "ingredients": (
            "200g chicken,"
            "100g pasta,"
            "1 table spoon olive oil"
        ),
        "instructions": (
            "Cook chicken, boil pasta, "
            "then mix with olive oil."
        ),
    }

    # Fake image file for upload
    files = {
        "file": (
            "test-recipe.jpg",
            b"fake image content",
            "image/jpeg",
        )
    }

    # Mock Gemini
    with patch(
        "app.api.routes.recipe.analyze_recipe"
    ) as mock_analyze_recipe:

        mock_analyze_recipe.return_value = {
            "calories": 822.5,
            "protein_g": 75,
            "carbs_g": 74,
            "fat_g": 22.2,
        }

        # Create recipe
        response = client.post(
            f"{settings.API_V1_STR}/users/recipe/upload",
            headers=normal_user_token_headers,
            data=data,
            files=files,
        )

    assert response.status_code == 200

    content = response.json()

    # Verify response
    assert "id" in content
    assert content["user_id"] == user_id
    assert content["recipe_name"] == data["recipe_name"]

    assert content["ingredients"] == [
        "200g chicken",
        "100g pasta",
        "1 table spoon olive oil",
    ]

    assert content["instructions"] == data["instructions"]

    # Verify nutrition
    assert content["total_calories"] == 822.5
    assert content["total_protein_g"] == 75
    assert content["total_carbs_g"] == 74
    assert content["total_fat_g"] == 22.2

    # Image URL should exist
    assert "image_url" in content

def test_get_recipes(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # Pehle ek recipe create karte hain
    data = {
        "recipe_name": "Automated GET Test Recipe",
        "ingredients": (
            "200g chicken,"
            "100g rice,"
            "1 tablespoon olive oil"
        ),
        "instructions": (
            "Cook chicken, cook rice, "
            "then mix with olive oil."
        ),
    }

    files = {
        "file": (
            "test-get-recipe.jpg",
            b"fake image content",
            "image/jpeg",
        )
    }

    # Gemini ko mock karte hain
    with patch(
        "app.api.routes.recipe.analyze_recipe"
    ) as mock_analyze_recipe:

        mock_analyze_recipe.return_value = {
            "calories": 750,
            "protein_g": 60,
            "carbs_g": 70,
            "fat_g": 20,
        }

        create_response = client.post(
            f"{settings.API_V1_STR}/users/recipe/upload",
            headers=normal_user_token_headers,
            data=data,
            files=files,
        )

    assert create_response.status_code == 200

    created_recipe = create_response.json()
    recipe_id = created_recipe["id"]

    # Ab GET recipes call karte hain
    response = client.get(
        f"{settings.API_V1_STR}/users/recipe",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    recipes = response.json()

    # Response list honi chahiye
    assert isinstance(recipes, list)

    # Jo recipe humne create ki thi,
    # wo GET response mein honi chahiye
    recipe = next(
        (
            item
            for item in recipes
            if item["id"] == recipe_id
        ),
        None,
    )

    assert recipe is not None

    # Recipe ki values verify karte hain
    assert recipe["recipe_name"] == data["recipe_name"]

    assert recipe["ingredients"] == [
        "200g chicken",
        "100g rice",
        "1 tablespoon olive oil",
    ]

    assert recipe["instructions"] == data["instructions"]

    # Nutrition verify karte hain
    assert recipe["total_calories"] == 750
    assert recipe["total_protein_g"] == 60
    assert recipe["total_carbs_g"] == 70
    assert recipe["total_fat_g"] == 20