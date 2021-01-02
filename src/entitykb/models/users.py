from uuid import uuid4

from pydantic import BaseModel, Field

from .enums import UserStatus


class User(BaseModel):
    username: str
    status: UserStatus = UserStatus.read_only
    uuid: str = Field(default_factory=lambda: str(uuid4()))


class StoredUser(User):
    hashed_password: str


class UserToken(BaseModel):
    access_token: str
    token_type: str
