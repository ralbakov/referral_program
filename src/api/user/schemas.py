from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, StrictStr


class User(BaseModel):
    model_config = ConfigDict(strict=True, str_strip_whitespace=True)

    username: StrictStr


class UserUpdate(User):

    email: EmailStr
    password: StrictStr


class ReferralCode(User):

    referal_code: StrictStr
    exp_ref_code: datetime
