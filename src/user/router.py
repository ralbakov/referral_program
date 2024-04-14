from fastapi import APIRouter, Depends, HTTPException, status
from jwt import InvalidTokenError

from src.database.schemas import User
from src.user.schemas import ReferralCode, UserUpdate
from src.user.service import UserService

user_router = APIRouter(prefix='/auth/user/me', tags=['USER'])


@user_router.get(
    '/',
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary='Получить информацию авторизованного пользователя',
)
async def read(service: UserService = Depends()) -> User:
    try:
        return await service.read()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.args[0]
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.args[0]
        )


@user_router.patch(
    '/',
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary='Обновить информацию авторизованного пользователя',
)
async def update(
    data: UserUpdate = Depends(),
    service: UserService = Depends()
) -> User:
    try:
        return await service.update(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.args[0]
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.args[0]
        )


@user_router.delete(
    '/',
    status_code=status.HTTP_200_OK,
    summary='Деактивировать авторизованного пользователя (отключить)',
)
async def deactivate(service: UserService = Depends()) -> dict:
    try:
        await service.deactivate()
        return {'detail': 'Username is deleted'}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.args[0]
        )


@user_router.patch(
    '/referralcode/',
    response_model=ReferralCode,
    status_code=status.HTTP_201_CREATED,
    summary='Создать реферальный код авторизованного пользователя, cо сроком действия (по умолчанию 30 дней)',
)
async def create_referral_code(
    expire_timedelta_day: str | int = 30,
    service: UserService = Depends(),
):
    try:
        return await service.create_ref_code(int(expire_timedelta_day))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.args[0]
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.args[0]
        )


@user_router.delete(
    '/referralcode/',
    status_code=status.HTTP_200_OK,
    summary='Удалить реферальный код авторизованного пользователя'
)
async def delete_referral_code(service: UserService = Depends()) -> dict:
    try:
        await service.delete_ref_code()
        return {'detail': 'Referral code is deleted'}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.args[0]
        )


@user_router.get(
    '/referrals/',
    response_model=list[User],
    status_code=status.HTTP_200_OK,
    summary='Получить всех рефералов авторизованного пользователя',
)
async def get_all_referrals(service: UserService = Depends()) -> list[User]:
    try:
        return await service.get_all_referral()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.args[0]
        )
