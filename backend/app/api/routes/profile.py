from fastapi import APIRouter, HTTPException
from sqlmodel import select
import uuid
from app.api.deps import CurrentUser, SessionDep
from app.models import Profile, ProfileCreate, ProfilePublic, ProfileUpdate

router = APIRouter(tags=["profile"])


@router.post("/users/profile", response_model=ProfilePublic)
def create_profile(
    profile_in: ProfileCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Profile:
    profile = Profile(
        user_id=current_user.id,
        date_of_birth=profile_in.date_of_birth,
        gender=profile_in.gender,
        height=profile_in.height,
        weight=profile_in.weight,
        activity_level=profile_in.activity_level,
    )

    session.add(profile)
    session.commit()
    session.refresh(profile)

    return profile

@router.get("/users/profile", response_model=ProfilePublic)
def get_profile(
    session: SessionDep,
    current_user: CurrentUser,
) -> Profile:
    profile = session.exec(
        select(Profile).where(Profile.user_id == current_user.id)
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile

@router.patch("/users/{user_id}/profile", response_model=ProfilePublic)
def update_profile(
    user_id: uuid.UUID,
    profile_in: ProfileUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Profile:
    profile = session.exec(
        select(Profile).where(Profile.user_id == user_id)
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile_data = profile_in.model_dump(exclude_unset=True)

    for field, value in profile_data.items():
        setattr(profile, field, value)

    session.add(profile)
    session.commit()
    session.refresh(profile)

    return profile    