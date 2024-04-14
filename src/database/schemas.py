from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, EmailStr, StrictBool, StrictStr


class User(BaseModel):
    model_config = ConfigDict(strict=True)

    id: UUID4
    username: StrictStr
    email: EmailStr
    created_at: datetime
    is_active: StrictBool
    id_referal: Optional[UUID4 | None]
    referal_code: Optional[StrictStr | None]
    exp_ref_code: Optional[datetime | None]
