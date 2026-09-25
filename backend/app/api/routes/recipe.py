import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.api.routes.recipe_detection import analyze_recipe
from app.models import Recipe


router = APIRouter(tags=["recipe"])


UPLOAD_DIR = Path("uploads/recipes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/users/recipe/upload")
def upload_recipe(
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    recipe_name: str = Form(...),
    ingredients: str = Form(...),
    instructions: str = Form(...),
) -> Recipe:

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required",
        )

    file_extension = Path(file.filename).suffix

    new_file_name = f"{uuid.uuid4()}{file_extension}"

    file_path = UPLOAD_DIR / new_file_name

    with file_path.open("wb") as buffer:
        buffer.write(file.file.read())

    ingredients_list = [
        item.strip()
        for item in ingredients.split(",")
        if item.strip()
    ]

    nutrition = analyze_recipe(ingredients_list)

    recipe = Recipe(
        user_id=current_user.id,
        recipe_name=recipe_name,
        image_url=str(file_path).replace("\\", "/"),
        ingredients=ingredients_list,
        instructions=instructions,
        total_calories=nutrition["calories"],
        total_protein_g=nutrition["protein_g"],
        total_carbs_g=nutrition["carbs_g"],
        total_fat_g=nutrition["fat_g"],
    )

    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    return recipe


@router.get("/users/recipe")
def get_recipes(
    session: SessionDep,
    current_user: CurrentUser,
) -> list[Recipe]:

    recipes = session.exec(
        select(Recipe).where(
            Recipe.user_id == current_user.id
        )
    ).all()

    return list(recipes)