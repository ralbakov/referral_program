import uuid
from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    UUID,
    Boolean,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.config import Base


class User(Base):

    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(length=100), nullable=False, index=True, unique=True
    )
    email: Mapped[str] = mapped_column(
        String(length=320), nullable=False, index=True, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.now()
    )
    hashed_password: Mapped[bytes] = mapped_column(
        LargeBinary(length=1024), nullable=False, unique=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    id_referal: Mapped[uuid.UUID] = mapped_column(
        UUID, nullable=True, index=True, default=None
    )
    referal_code: Mapped[str] = mapped_column(
        String(length=10), nullable=True, default=None, unique=True
    )
    exp_ref_code: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=True, default=None
    )
    resetpass = relationship('ResetPass', back_populates='user')


class ResetPass(Base):

    __tablename__ = 'resetpass'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(length=320), ForeignKey('user.email', ondelete='cascade'), nullable=False, unique=True
    )
    resetkey: Mapped[uuid.UUID] = mapped_column(
        UUID, nullable=True, default=uuid.uuid4
    )
    user = relationship('User', back_populates='resetpass')
