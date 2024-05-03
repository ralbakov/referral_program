from datetime import datetime

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import utils as auth_utils
from src.api.auth.schemas import ChangePassword, UserRegistration
from src.database.config import get_async_session
from src.database.models import ResetPass, User


class UserAuthRepository:
    '''Репозиторий для работой с базой данных при регистрации и аутендификации'''
    __slots__ = ['session']

    def __init__(self, session: AsyncSession = Depends(get_async_session)) -> None:
        self.session = session

    async def create(self, user: UserRegistration) -> User:
        '''Создать пользователя'''
        data = user.model_dump()
        if user.referal_code:
            user_check = await self.read_user_at_referal_code(user.referal_code)
            if not user_check or not user_check.is_active or user_check.exp_ref_code < datetime.now():
                raise ValueError('User with referral code not found or expire referral code')
            del data['referal_code']
            data['id_referal'] = user_check.id
        password = data.pop('password')
        data['hashed_password'] = auth_utils.hash_password(password)
        result = User(**data)
        self.session.add(result)
        try:
            await self.session.commit()
        except IntegrityError as e:
            raise ValueError(e.args[0])
        return result

    async def read(self, username: str) -> User:
        '''Получить пользователя по username'''
        result = (
            await self.session.execute(
                select(User).where(
                    User.username == username
                )
            )
        ).scalar()
        return result

    async def read_user_at_referal_code(self, referal_code: str) -> User:
        '''Получить пользователя по реферальному коду'''
        result = (
            await self.session.execute(
                select(User).where(
                    User.referal_code == referal_code
                )
            )
        ).scalar()
        return result


class ResetPasswordRepository:
    '''Репозиторий для создания ключа сброса пароля'''
    __slots__ = ['session']

    def __init__(self, session: AsyncSession = Depends(get_async_session)) -> None:
        self.session = session

    async def create_reset_key(self, email: str) -> str:
        '''Создает ключ для сброса'''
        result = (
            await self.session.execute(
                select(User.email).where(
                    User.email == email
                )
            )
        ).scalar()
        if not result:
            raise ValueError('Email not found')
        result = ResetPass(email=email)
        self.session.add(result)
        try:
            await self.session.commit()
        except IntegrityError as e:
            raise ValueError(e.args[0])
        return str(result.resetkey)

    async def change_password(self, data: ChangePassword) -> User:
        '''Изменить пароль'''
        try:
            result = (
                await self.session.execute(
                    select(User).join(ResetPass)
                    .where(User.email == ResetPass.email)
                    .where(ResetPass.resetkey == data.resetkey)
                )
            ).scalar()
        except DBAPIError:
            raise ValueError('Key invalid')
        if not result:
            raise ValueError('Email or key not found or invalid')
        result.hashed_password = auth_utils.hash_password(data.new_password)
        try:
            await self.session.merge(result)
            await self.session.commit()
        except IntegrityError as e:
            raise ValueError(e.args[0])
        await self.delete_reset_key(data.resetkey)
        return result

    async def delete_reset_key(self, key: str) -> None:
        '''Удаляет ключ для сброса'''
        await self.session.execute(
            delete(ResetPass).where(
                ResetPass.resetkey == key
            )
        )
        try:
            await self.session.commit()
        except IntegrityError as e:
            raise ValueError(e.args[0])
        return None
