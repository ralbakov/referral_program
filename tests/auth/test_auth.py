from http import HTTPStatus

from httpx import AsyncClient


async def test_registration(ac_client: AsyncClient) -> None:
    response = await ac_client.post(
        url='/registration/',
        params={
            'username': 'user1',
            'email': 'user1@user1.user',
            'password': 'password'
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['username'] == 'user1'
    assert response.json()['email'] == 'user1@user1.user'
    assert response.json()['is_active'] is True


async def test_registration_exist_name(ac_client: AsyncClient) -> None:
    response = await ac_client.post(
        url='/registration/',
        params={
            'username': 'user1',
            'email': 'user2@user2.user',
            'password': 'user2'
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert '(user1) already exists.' in response.json()['detail']


async def test_registration_exist_email(ac_client: AsyncClient) -> None:
    response = await ac_client.post(
        url='/registration/',
        params={
            'username': 'user2',
            'email': 'user1@user1.user',
            'password': 'user2'
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert '(user1@user1.user) already exists.' in response.json()['detail']


async def test_login(
    ac_client: AsyncClient,
    save_token: dict[str, str],
) -> None:
    response = await ac_client.post(
        url='/login',
        data={
            'username': 'user1',
            'password': 'password'
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'Bearer'
    save_token['access_token'] = response.json()['access_token']


async def test_login_bad_username(ac_client: AsyncClient) -> None:
    response = await ac_client.post(
        url='/login',
        data={
            'username': 'user2',
            'password': 'user1'
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid username'}


async def test_login_bad_password(ac_client: AsyncClient) -> None:
    response = await ac_client.post(
        url='/login',
        data={
            'username': 'user1',
            'password': 'user2'
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid password'}


async def test_registration_with_code_bad(ac_client: AsyncClient) -> None:
    response = await ac_client.post(
        url='/registration/',
        params={
            'referal_code': 'BadCod',
            'username': 'user2',
            'email': 'user2@user2.user',
            'password': 'user2'
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User with referral code '
                                         'not found or expire referral code'}
