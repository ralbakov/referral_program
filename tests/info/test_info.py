from http import HTTPStatus

from httpx import AsyncClient


async def test_receive_code_by_email_not_exist(ac_client: AsyncClient) -> None:
    response = await ac_client.get(
        url='/getcode/bademail@example.com'
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Referral with email not found'}


async def test_receive_code_by_email_not_created_code(ac_client: AsyncClient) -> None:
    response = await ac_client.get(
        url='/getcode/user1@user1.user'
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Referral code not activated or expire referral code'}


async def test_get_info_about_referrals(ac_client: AsyncClient) -> None:
    response = await ac_client.get(
        url='/referrals/8ad5a1a9-0181-4859-9865-15f335c131af'
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Referrals not found'}
