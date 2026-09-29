from datetime import date
from pathlib import Path
import uuid

from app.api.deps import CurrentUser, SessionDep
from app.models import PhysiquePhoto
from fastapi import APIRouter, File, Form, UploadFile
from sqlmodel import select


router = APIRouter(tags=["physique photos"])


UPLOAD_DIR = Path("uploads/physique_photos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post(
    "/users/physique/upload",
    response_model=PhysiquePhoto,
)
def create_physique_photo(
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    photo_type: str = Form(...),
    log_date: date = Form(...),
) -> PhysiquePhoto:

    file_extension = Path(file.filename or "").suffix

    new_file_name = f"{uuid.uuid4()}{file_extension}"

    file_path = UPLOAD_DIR / new_file_name

    with file_path.open("wb") as buffer:
        buffer.write(file.file.read())

    physique_photo = PhysiquePhoto(
        user_id=current_user.id,
        photo_type=photo_type,
        photo_url=str(file_path),
        log_date=log_date,
    )

    session.add(physique_photo)
    session.commit()
    session.refresh(physique_photo)

    return physique_photo


@router.get(
    "/users/physique",
    response_model=list[PhysiquePhoto],
)
def get_all_physique_photos(
    session: SessionDep,
    current_user: CurrentUser,
) -> list[PhysiquePhoto]:

    physique_photos = session.exec(
        select(PhysiquePhoto).where(
            PhysiquePhoto.user_id == current_user.id
        )
    ).all()

    return list(physique_photos)