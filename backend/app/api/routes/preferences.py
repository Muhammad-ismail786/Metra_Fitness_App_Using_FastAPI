import uuid
from fastapi import APIRouter
from sqlmodel import select
from app.api.deps import CurrentUser, SessionDep
from app.models import UserPreference, UserPreferenceCreate, UserPreferencePublic

router = APIRouter(tags=["user preferences"])


@router.post("/users/preferences", response_model=UserPreferencePublic)
def create_user_preference(
    preference_in: UserPreferenceCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> UserPreference:
    preference = UserPreference(
        user_id=current_user.id,
        preferred_workout_duration=preference_in.preferred_workout_duration,
        workouts_per_week=preference_in.workouts_per_week,
        available_equipment=preference_in.available_equipment,
        workout_location=preference_in.workout_location,
    )

    session.add(preference)
    session.commit()
    session.refresh(preference)

    return preference

@router.get("/users/preferences", response_model=list[UserPreferencePublic])
def get_all_preferences(
    session: SessionDep,
    current_user: CurrentUser,
) -> list[UserPreference]:
    preferences = session.exec(
        select(UserPreference)
    ).all()

    return list(preferences)    

@router.get(
    "/users/{user_id}/preferences",
    response_model=list[UserPreferencePublic],
)
def get_preferences_by_user_id(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> list[UserPreference]:
    preferences = session.exec(
        select(UserPreference).where(UserPreference.user_id == user_id)
    ).all()

    return list(preferences)

@router.delete("/users/{user_id}/preferences")
def delete_user_preference(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    preference = session.exec(
        select(UserPreference).where(UserPreference.user_id == user_id)
    ).first()

    if not preference:
        return {"message": "User preference not found"}

    session.delete(preference)
    session.commit()

    return {"message": "User preference deleted successfully"}    