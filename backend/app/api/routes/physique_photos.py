from datetime import date
from pathlib import Path
import uuid

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.models import PhysiquePhoto
from fastapi import APIRouter, File, Form, UploadFile
from sqlmodel import select
from supabase import create_client


router = APIRouter(tags=["physique photos"])


# ============================================================
# LOCAL STORAGE CODE - COMMENTED OUT
# Keeping this for future reference
# ============================================================

# UPLOAD_DIR = Path("uploads/physique_photos")
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# SUPABASE STORAGE
# ============================================================

supabase = create_client(
    str(settings.SUPABASE_URL),
    settings.SUPABASE_SERVICE_ROLE_KEY,
)

SUPABASE_BUCKET = "metra-images"
SUPABASE_FOLDER = "physique_photos"


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

    storage_path = (
        f"{SUPABASE_FOLDER}/"
        f"{current_user.id}/"
        f"{new_file_name}"
    )

    # Read uploaded file
    file_bytes = file.file.read()

    # Upload image to Supabase Storage
    supabase.storage.from_(SUPABASE_BUCKET).upload(
        storage_path,
        file_bytes,
        {
            "content-type": file.content_type
            or "application/octet-stream",
        },
    )

    # Public URL of uploaded image
    photo_url = (
        f"{settings.SUPABASE_URL}"
        f"/storage/v1/object/public/"
        f"{SUPABASE_BUCKET}/"
        f"{storage_path}"
    )

    physique_photo = PhysiquePhoto(
        user_id=current_user.id,
        photo_type=photo_type,
        photo_url=photo_url,
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