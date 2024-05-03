from datetime import datetime, timedelta

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.utils import hash_password
from src.api.user.schemas import UserUpdate
from src.api.user.utils import generate_ref_code
from src.database.config import get_async_session
from src.database.models import User


class UserRepository:
    '''Репозиторий для работы с базой данных пользователя'''

    __slots__ = ['session']

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def update(self, user: User, data: UserUpdate):
        '''Обновить данные пользователя'''
        user.username = data.username
        user.email = data.email
        user.hashed_password = hash_password(data.password)
        self.session.add(user)
        try:
            await self.session.merge(user)
            await self.session.commit()
        except IntegrityError as e:
            raise ValueError(e.args[0])
        return user

    async def deactivate(self, user: User) -> None:
        '''Отключить пользователя'''
        user.is_active = False
        self.session.add(user)
        try:
            await self.session.merge(user)
            await self.session.commit()
        except IntegrityError as e:
            raise ValueError(e.args[0])
        return None

    async def create_referral_code(self, user: User, expire_timedelta_day: int | None) -> User:
        '''Создать реферальный код'''
        now = datetime.now()
        if user.referal_code and user.exp_ref_code > now:
            raise ValueError(f" Refarral code alredy exist. Your code: '{user.referal_code}' ")
        if expire_timedelta_day:
            expire = now + timedelta(days=expire_timedelta_day)
        else:
            expire = now + timedelta(days=30)
        user.referal_code = generate_ref_code()
        user.exp_ref_code = expire
        self.session.add(user)
        try:
            await self.session.merge(user)
            await self.session.commit()
        except IntegrityError as e:
            raise ValueError(e.args[0])
        return user

    async def delete_referral_code(self, user: User) -> User:
        '''Удалить реферальный код'''
        user.referal_code = None
        user.exp_ref_code = None
        self.session.add(user)
        try:
            await self.session.merge(user)
            await self.session.commit()
        except IntegrityError as e:
            raise ValueError(e.args[0])
        return user

    async def get_all_referral(self, id: str) -> list[User]:
        '''Получить всех рефералов пользователя'''
        result = await self.session.execute(
            select(User).where(User.id_referal == id)
        )
        return result.scalars().all()
