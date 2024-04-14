from fastapi import APIRouter, Depends, HTTPException, status

from src.info.schemas import ReferralCodeInfo, UserInfo
from src.info.service import EmailHunter, InfoService, ReceiveCodeEmailService

info_router = APIRouter(prefix='/auth', tags=['INFO'])


@info_router.get(
    '/checkemail',
    status_code=status.HTTP_200_OK,
    summary='Проверить указанный email адрес с использованием сервиса emailhunter.co',
)
async def check_email_with_emailhunter(service: EmailHunter = Depends()) -> dict:
    return await service.check_email()


@info_router.get(
    '/getcode/{email}',
    status_code=status.HTTP_200_OK,
    response_model=ReferralCodeInfo,
    summary='Получить реферальный код по email адресу реферера',
)
async def receive_code_by_email(
    email: str,
    service: ReceiveCodeEmailService = Depends()
) -> ReferralCodeInfo:
    try:
        return await service.get_code(email.strip())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.args[0],
        )


@info_router.get(
    '/referrals/{id}',
    status_code=status.HTTP_200_OK,
    response_model=list[UserInfo],
    summary='Получить информацию о рефералах по id реферера',
)
async def get_info_about_referrals(
    id: str,
    service: InfoService = Depends(),
) -> list[UserInfo]:
    try:
        return await service.about_referrals(id.strip())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.args[0],
        )
