from uuid import uuid4

from pydantic import BaseModel, Field

from .enums import UserStatus


class User(BaseModel):
    username: str
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    status: UserStatus = UserStatus.read_only


class StoredUser(User):
    hashed_password: str
