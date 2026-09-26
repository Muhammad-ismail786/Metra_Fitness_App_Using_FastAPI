from datetime import date

from fastapi import APIRouter, Query
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import DailyNutritionSummary, FoodLog


router = APIRouter(tags=["daily-nutrition-summary"])


@router.get("/daily-nutrition-summary")
def get_daily_nutrition_summary(
    session: SessionDep,
    current_user: CurrentUser,
    log_date: date | None = Query(default=None),
) -> DailyNutritionSummary:

    if log_date is None:
        log_date = date.today()

    food_logs = session.exec(
        select(FoodLog).where(
            FoodLog.user_id == current_user.id,
            FoodLog.log_date == log_date,
        )
    ).all()

    total_calories = sum(
        food.total_calories for food in food_logs
    )

    total_protein_g = sum(
        food.total_protein_g for food in food_logs
    )

    total_carbs_g = sum(
        food.total_carbs_g for food in food_logs
    )

    total_fat_g = sum(
        food.total_fat_g for food in food_logs
    )

    meals_logged = len(food_logs)

    return DailyNutritionSummary(
        user_id=current_user.id,
        date=log_date,
        total_calories=total_calories,
        total_protein_g=total_protein_g,
        total_carbs_g=total_carbs_g,
        total_fat_g=total_fat_g,
        meals_logged=meals_logged,
    )