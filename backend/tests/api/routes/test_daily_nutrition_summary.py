from fastapi.testclient import TestClient

from app.core.config import settings


def test_daily_nutrition_summary(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:

    response = client.get(
        f"{settings.API_V1_STR}/daily-nutrition-summary",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200

    content = response.json()

    assert "user_id" in content
    assert "date" in content
    assert "total_calories" in content
    assert "total_protein_g" in content
    assert "total_carbs_g" in content
    assert "total_fat_g" in content
    assert "meals_logged" in content