import uuid

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import WorkoutPlan, WorkoutPlanCreate, WorkoutPlanPublic,  WorkoutPlanUpdate

router = APIRouter(tags=["workout plans"])


@router.post("/users/workout-plans", response_model=WorkoutPlanPublic)
def create_workout_plan(
    workout_plan_in: WorkoutPlanCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> WorkoutPlan:
    workout_plan = WorkoutPlan(
        user_id=current_user.id,
        plan_name=workout_plan_in.plan_name,
        duration=workout_plan_in.duration,
        weekly_schedule=workout_plan_in.weekly_schedule,
        exercises=workout_plan_in.exercises,
        status=workout_plan_in.status,
    )

    session.add(workout_plan)
    session.commit()
    session.refresh(workout_plan)

    return workout_plan

@router.get("/users/workout-plans", response_model=list[WorkoutPlanPublic])
def get_all_workout_plans(
    session: SessionDep,
    current_user: CurrentUser,
) -> list[WorkoutPlan]:
    workout_plans = session.exec(
        select(WorkoutPlan)
    ).all()

    return list(workout_plans)

@router.get("/users/workout-plans/{workout_plan_id}", response_model=WorkoutPlanPublic)
def get_workout_plan_by_id(
    workout_plan_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> WorkoutPlan:
    workout_plan = session.get(WorkoutPlan, workout_plan_id)

    if not workout_plan:
        raise HTTPException(
            status_code=404,
            detail="Workout plan not found",
        )

    return workout_plan


@router.patch(
    "/users/workout-plans/{workout_plan_id}",
    response_model=WorkoutPlanPublic,
)
def update_workout_plan(
    workout_plan_id: uuid.UUID,
    workout_plan_in: WorkoutPlanUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> WorkoutPlan:
    workout_plan = session.get(WorkoutPlan, workout_plan_id)

    if not workout_plan:
        raise HTTPException(
            status_code=404,
            detail="Workout plan not found",
        )

    update_data = workout_plan_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(workout_plan, field, value)

    session.add(workout_plan)
    session.commit()
    session.refresh(workout_plan)

    return workout_plan

@router.delete("/users/workout-plans/{workout_plan_id}")
def delete_workout_plan(
    workout_plan_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    workout_plan = session.get(WorkoutPlan, workout_plan_id)

    if not workout_plan:
        raise HTTPException(
            status_code=404,
            detail="Workout plan not found",
        )

    session.delete(workout_plan)
    session.commit()

    return {"message": "Workout plan deleted successfully"}