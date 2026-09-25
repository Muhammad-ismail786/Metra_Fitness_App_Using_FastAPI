import json

from google import genai
from google.genai import types

from app.core.config import settings


client = genai.Client(api_key=settings.GEMINI_API_KEY)


def analyze_recipe(ingredients: list[str]) -> dict:
    prompt = f"""
    Analyze the following recipe ingredients and estimate the total nutrition.

    Ingredients:
    {ingredients}

    Estimate nutrition for the complete recipe.

    Return:
    - calories
    - protein_g
    - carbs_g
    - fat_g

    All values must be numbers.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "calories": {
                            "type": "NUMBER"
                        },
                        "protein_g": {
                            "type": "NUMBER"
                        },
                        "carbs_g": {
                            "type": "NUMBER"
                        },
                        "fat_g": {
                            "type": "NUMBER"
                        },
                    },
                    "required": [
                        "calories",
                        "protein_g",
                        "carbs_g",
                        "fat_g",
                    ],
                },
            ),
        )

        response_text = response.text

        if not response_text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return json.loads(response_text)

    except Exception as error:
        raise RuntimeError(
            f"Gemini recipe analysis failed: {error}"
        ) from error