from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, EmailStr, StrictBool, StrictStr


class UserInfo(BaseModel):
    model_config = ConfigDict(strict=True)

    id: UUID4
    username: StrictStr
    created_at: datetime
    is_active: StrictBool
    referal_code: Optional[StrictStr | None]
    exp_ref_code: Optional[datetime | None]


class ReferralCodeInfo(BaseModel):
    model_config = ConfigDict(strict=True)

    email: EmailStr
    referal_code: StrictStr
