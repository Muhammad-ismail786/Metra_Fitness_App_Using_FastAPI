import uuid

from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Goal, GoalCreate, GoalPublic

router = APIRouter(tags=["goals"])


@router.post("/users/{user_id}/goals", response_model=GoalPublic)
def create_goal(
    user_id: uuid.UUID,
    goal_in: GoalCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Goal:
    goal = Goal(
        user_id=user_id,
        goal_type=goal_in.goal_type,
        target_value=goal_in.target_value,
        current_value=goal_in.current_value,
        target_date=goal_in.target_date,
        description=goal_in.description,
    )

    session.add(goal)
    session.commit()
    session.refresh(goal)

    return goal


@router.get("/users/goals", response_model=list[GoalPublic])
def get_all_goals(
    session: SessionDep,
    current_user: CurrentUser,
) -> list[Goal]:
    goals = session.exec(
        select(Goal)
    ).all()

    return list(goals)

@router.get("/users/{user_id}/goals", response_model=list[GoalPublic])
def get_goals_by_user_id(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> list[Goal]:
    goals = session.exec(
        select(Goal).where(Goal.user_id == user_id)
    ).all()

    return list(goals)    