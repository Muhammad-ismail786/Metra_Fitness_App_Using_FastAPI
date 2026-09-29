from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_physique_photo(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # Current user ka user_id get karte hain
    user_response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
    )

    assert user_response.status_code == 200

    user = user_response.json()
    user_id = user["id"]

    # Physique photo ka form data
    data = {
        "photo_type": "front",
        "log_date": "2026-09-29",
    }

    # Fake image file
    files = {
        "file": (
            "test-physique.jpg",
            b"fake physique image content",
            "image/jpeg",
        )
    }

    # ============================================================
    # OLD LOCAL STORAGE TEST CODE
    # Kept for reference - DO NOT REMOVE
    # ============================================================

    # Local storage mein file save hoti thi.
    #
    # file_extension = Path(file.filename or "").suffix
    # new_file_name = f"{uuid.uuid4()}{file_extension}"
    # file_path = UPLOAD_DIR / new_file_name
    #
    # with file_path.open("wb") as buffer:
    #     buffer.write(file.file.read())
    #
    # photo_url = str(file_path)

    # ============================================================
    # SUPABASE STORAGE
    # ============================================================

    # Physique photo create/upload karte hain
    response = client.post(
        f"{settings.API_V1_STR}/users/physique/upload",
        headers=normal_user_token_headers,
        data=data,
        files=files,
    )

    # API successful honi chahiye
    assert response.status_code == 200

    content = response.json()

    # Basic response check
    assert "id" in content
    assert content["user_id"] == user_id

    # Physique photo data check
    assert content["photo_type"] == "front"
    assert content["log_date"] == "2026-09-29"

    # Photo URL check
    assert "photo_url" in content
    assert content["photo_url"]

    # Supabase Storage URL check
    assert (
        "supabase.co/storage/v1/object/public/"
        "metra-images/physique_photos/"
        in content["photo_url"]
    )


def test_get_physique_photos(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    # Pehle ek physique photo create karte hain
    data = {
        "photo_type": "side",
        "log_date": "2026-09-29",
    }

    # Fake image file
    files = {
        "file": (
            "test-get-physique.jpg",
            b"fake physique image content",
            "image/jpeg",
        )
    }

    # ============================================================
    # OLD LOCAL STORAGE
    # Kept for reference - DO NOT REMOVE
    # ============================================================

    # Pehle local filesystem mein image save hoti thi.
    #
    # file_extension = Path(file.filename or "").suffix
    # new_file_name = f"{uuid.uuid4()}{file_extension}"
    # file_path = UPLOAD_DIR / new_file_name
    #
    # with file_path.open("wb") as buffer:
    #     buffer.write(file.file.read())

    # ============================================================
    # SUPABASE STORAGE
    # ============================================================

    # Pehle POST API call
    create_response = client.post(
        f"{settings.API_V1_STR}/users/physique/upload",
        headers=normal_user_token_headers,
        data=data,
        files=files,
    )

    # Create successful honi chahiye
    assert create_response.status_code == 200

    created_photo = create_response.json()
    physique_photo_id = created_photo["id"]

    # Ab GET API call karte hain
    response = client.get(
        f"{settings.API_V1_STR}/users/physique",
        headers=normal_user_token_headers,
    )

    # GET successful honi chahiye
    assert response.status_code == 200

    physique_photos = response.json()

    # Response list honi chahiye
    assert isinstance(physique_photos, list)

    # Jo photo abhi create ki thi
    # wo GET response mein honi chahiye
    physique_photo = next(
        (
            item
            for item in physique_photos
            if item["id"] == physique_photo_id
        ),
        None,
    )

    assert physique_photo is not None

    # Photo data verify karte hain
    assert physique_photo["photo_type"] == "side"
    assert physique_photo["log_date"] == "2026-09-29"

    # Photo URL verify karte hain
    assert "photo_url" in physique_photo
    assert physique_photo["photo_url"]

    # Supabase Storage URL verify karte hain
    assert (
        "supabase.co/storage/v1/object/public/"
        "metra-images/physique_photos/"
        in physique_photo["photo_url"]
    )