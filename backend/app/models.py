import uuid
from datetime import UTC, date, datetime
from pydantic import EmailStr
from sqlalchemy import DateTime,  JSON
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(UTC)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list[Item] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)




    # Profile model
class Profile(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True, index=True)
    date_of_birth: date
    gender: str
    height: float
    weight: float
    activity_level: str

class ProfileCreate(SQLModel):
    date_of_birth: date
    gender: str
    height: float
    weight: float
    activity_level: str


class ProfilePublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    date_of_birth: date
    gender: str
    height: float
    weight: float
    activity_level: str

class ProfileUpdate(SQLModel):
    date_of_birth: date | None = None
    gender: str | None = None
    height: float | None = None
    weight: float | None = None
    activity_level: str | None = None    

#goal actaul database table model
class Goal(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        index=True,
    )
    goal_type: str
    target_value: float
    current_value: float
    target_date: date
    description: str | None = None

# post request model for creating a new goal
class GoalCreate(SQLModel):
    goal_type: str
    target_value: float
    current_value: float
    target_date: date
    description: str | None = None

# api response model for returning goal data
class GoalPublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    goal_type: str
    target_value: float
    current_value: float
    target_date: date
    description: str | None = None


# User Preferences database model
class UserPreference(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        unique=True,
        index=True,
    )

    preferred_workout_duration: int
    workouts_per_week: int
    available_equipment: list[str] = Field(sa_type=JSON)
    workout_location: str


# Request model for creating user preferences
class UserPreferenceCreate(SQLModel):
    preferred_workout_duration: int
    workouts_per_week: int
    available_equipment: list[str]
    workout_location: str


# Response model for returning user preferences
class UserPreferencePublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    preferred_workout_duration: int
    workouts_per_week: int
    available_equipment: list[str]
    workout_location: str