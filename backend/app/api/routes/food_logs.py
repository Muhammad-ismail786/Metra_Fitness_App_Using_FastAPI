
import uuid
from datetime import date
from pathlib import Path
from sqlmodel import select
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.deps import CurrentUser, SessionDep
from app.api.routes.food_detection import analyze_food_image
from app.models import FoodLog


router = APIRouter(tags=["food-logs"])


UPLOAD_DIR = Path("uploads/food_logs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/users/food-logs/upload")
def create_food_log(
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    log_date: date = Form(...),
    quantity: float = Form(...),
    entry_method: str = Form(...),
) -> FoodLog:

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

    detected_food = analyze_food_image(str(file_path))

    food_log = FoodLog(
        user_id=current_user.id,
        food_name=detected_food["food_name"],
        log_date=log_date,
        quantity=quantity,
        total_calories=detected_food["calories"],
        total_protein_g=detected_food["protein_g"],
        total_carbs_g=detected_food["carbs_g"],
        total_fat_g=detected_food["fat_g"],
        entry_method=entry_method,
        ai_detected_items=[detected_food["food_name"]],
        image_url=str(file_path).replace("\\", "/"),
    )

    session.add(food_log)
    session.commit()
    session.refresh(food_log)

    return food_log



@router.get("/users/food-logs")
def get_food_logs(
    session: SessionDep,
    current_user: CurrentUser,
) -> list[FoodLog]:

    food_logs = session.exec(
        select(FoodLog).where(
            FoodLog.user_id == current_user.id
        )
    ).all()

    return list(food_logs)

