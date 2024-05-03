from datetime import datetime

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.config import get_async_session
from src.database.models import User


class InfoRepository:
    '''Репозиторий для работой с базой данных при регистрации и аутендификации'''
    __slots__ = ['session']

    def __init__(self, session: AsyncSession = Depends(get_async_session)) -> None:
        self.session = session

    async def read_user_at_email(self, email: str) -> User:
        '''Получить пользователя по email'''
        user = (
            await self.session.execute(
                select(User).where(
                    User.email == email
                )
            )
        ).scalar()
        if not user or not user.is_active:
            raise ValueError('Referral with email not found')
        if not user.referal_code or user.exp_ref_code < datetime.now():
            raise ValueError('Referral code not activated or expire referral code')
        return user

    async def get_users_id_referal(self, id: str) -> list[User]:
        '''Получить всех пользователей по id реферала'''
        users = (
            await self.session.execute(
                select(User).where(
                    User.id_referal == id
                )
            )
        ).scalars().all()
        return users
