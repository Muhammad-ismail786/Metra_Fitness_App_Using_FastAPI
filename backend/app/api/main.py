from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils
from app.core.config import settings
from app.api.routes import profile, goals, preferences, workout_plans, exercises,  food_logs, recipe

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(profile.router)
api_router.include_router(goals.router)
api_router.include_router(preferences.router)
api_router.include_router(workout_plans.router)
api_router.include_router(exercises.router)
api_router.include_router(food_logs.router)
api_router.include_router(recipe.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)


if settings.FASTAPI_ENV == "development":
    api_router.include_router(private.router)
