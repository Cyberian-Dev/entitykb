from uuid import uuid4

from pydantic import BaseModel, Field

from .enums import UserStatus


class User(BaseModel):
    """ Public user account information. """

    username: str
    status: UserStatus = UserStatus.read_only


class StoredUser(User):
    """ User account with private information not sent via servers. """

    uuid: str = Field(default_factory=lambda: str(uuid4()))
    hashed_password: str


class UserToken(BaseModel):
    access_token: str
    token_type: str
