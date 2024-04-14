from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, StrictStr


class Token(BaseModel):
    model_config = ConfigDict(strict=True)

    access_token: StrictStr
    token_type: StrictStr


class UserRegistration(BaseModel):
    model_config = ConfigDict(strict=True, str_strip_whitespace=True)

    referal_code: Optional[StrictStr | None] = None
    username: StrictStr
    email: EmailStr
    password: StrictStr


class ChangePassword(BaseModel):
    model_config = ConfigDict(strict=True, str_strip_whitespace=True)

    email: EmailStr
    resetkey: StrictStr
    new_password: StrictStr
