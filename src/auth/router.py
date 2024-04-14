from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.schemas import ChangePassword, Token, UserRegistration
from src.auth.service import ResetPasswordService, TokenService, UserRegistrationService
from src.database.schemas import User

auth_router = APIRouter(prefix='/auth', tags=['AUTH'])


@auth_router.post(
    '/registration/',
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary='Зарегистрировать пользователя',
)
async def registration(
    data: UserRegistration = Depends(),
    service: UserRegistrationService = Depends()
) -> User:
    try:
        return await service.create(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.args[0],
        )


@auth_router.post(
    '/login',
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary='Получить токен',
)
async def login_for_access_jwt(service: TokenService = Depends()) -> Token:
    try:
        return await service.create_access_jwt()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.args[0],
            headers={'WWW-Authenticate': 'Bearer'}
        )


@auth_router.get(
    '/resetpassword/',
    status_code=status.HTTP_200_OK,
    summary='Отправить ключ для сброса пароля',
)
async def resetpassword(email: str, service: ResetPasswordService = Depends()) -> dict:
    try:
        await service.send_reset_key(email.strip())
        return {'detail': 'Key for reset password has been sent to your email.'}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.args[0],
        )


@auth_router.patch(
    '/resetpassword/',
    status_code=status.HTTP_200_OK,
    summary='Изменить забытый пароль с помощью ключа',
)
async def change_password_with_key(data: ChangePassword = Depends(), service: ResetPasswordService = Depends()) -> dict:
    try:
        await service.change_password(data)
        return {'detail': 'Password update'}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.args[0],
        )
