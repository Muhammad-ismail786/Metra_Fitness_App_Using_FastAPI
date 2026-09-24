import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Exercise, ExercisePublic, ExerciseUpdate

router = APIRouter(tags=["exercises"])


UPLOAD_DIR = Path("uploads/exercises")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post(
    "/users/exercises/upload",
    response_model=ExercisePublic,
)
def create_exercise(
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    exercise_name: str = Form(...),
    description: str = Form(...),
    muscle_groups: str = Form(...),
    instructions: str = Form(...),
) -> Exercise:

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

    exercise = Exercise(
        user_id=current_user.id,
        exercise_name=exercise_name,
        description=description,
        muscle_groups=muscle_groups,
        instructions=instructions,
        image_url=str(file_path).replace("\\", "/"),
    )

    session.add(exercise)
    session.commit()
    session.refresh(exercise)

    return exercise


@router.get(
    "/users/exercises",
    response_model=list[ExercisePublic],
)
def get_all_exercises(
    session: SessionDep,
    current_user: CurrentUser,
) -> list[Exercise]:
    exercises = session.exec(
        select(Exercise)
    ).all()

    return list(exercises)

@router.patch(
    "/users/exercises/{exercise_id}",
    response_model=ExercisePublic,
)
def update_exercise(
    exercise_id: uuid.UUID,
    exercise_in: ExerciseUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Exercise:
    exercise = session.get(Exercise, exercise_id)

    if not exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercise not found",
        )

    if exercise.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )

    exercise_data = exercise_in.model_dump(exclude_unset=True)

    for key, value in exercise_data.items():
        setattr(exercise, key, value)

    session.add(exercise)
    session.commit()
    session.refresh(exercise)

    return exercise

@router.delete(
    "/users/exercises/{exercise_id}",
)
def delete_exercise(
    exercise_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    exercise = session.get(Exercise, exercise_id)

    if not exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercise not found",
        )

    if exercise.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )

    session.delete(exercise)
    session.commit()

    return {
        "message": "Exercise deleted successfully",
    }