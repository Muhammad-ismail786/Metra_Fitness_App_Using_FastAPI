
import json
import mimetypes

from google import genai

from app.core.config import settings


client = genai.Client(api_key=settings.GEMINI_API_KEY)


def analyze_food_image(image_path: str) -> dict:
    mime_type, _ = mimetypes.guess_type(image_path)

    if not mime_type:
        mime_type = "image/jpeg"

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_bytes,
                    }
                },
                """
                Analyze this food image and estimate its nutritional information.

                Return ONLY valid JSON.
                Do not add markdown or any explanation.

                Use exactly this structure:

                {
                    "food_name": "fried chicken",
                    "quantity": 1,
                    "calories": 300,
                    "protein_g": 20,
                    "carbs_g": 15,
                    "fat_g": 18
                }

                Rules:
                - Identify the main food visible in the image.
                - Estimate the quantity as a serving count.
                - Estimate calories, protein, carbohydrates, and fat.
                - All nutrition values must be numbers.
                - If the exact quantity cannot be determined, make a reasonable estimate.
                """,
            ],
        )

        return json.loads(response.text or "{}")

    except Exception as error:
        raise RuntimeError(
            f"Gemini food analysis failed: {error}"
        ) from error

