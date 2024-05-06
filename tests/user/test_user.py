from http import HTTPStatus

from httpx import AsyncClient


async def test_read(
    ac_client: AsyncClient,
    save_token: dict[str, str],
    save_response_data: dict[str, str]
) -> None:
    response = await ac_client.get(
        url='/user/me/',
        headers={'Authorization': f"Bearer {save_token['access_token']}"}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['username'] == 'user1'
    assert response.json()['email'] == 'user1@user1.user'
    save_response_data.update(response.json())


async def test_update(
    ac_client: AsyncClient,
    save_token: dict[str, str],
    save_response_data: dict[str, str],
) -> None:
    response = await ac_client.patch(
        url='/user/me/',
        headers={'Authorization': f"Bearer {save_token['access_token']}"},
        params={
            'username': 'user_update',
            'email': 'update@update.com',
            'password': 'pass_update'
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['username'] == 'user_update'
    assert response.json()['email'] == 'update@update.com'
    save_response_data.update(response.json())


async def test_read_old_data(
    ac_client: AsyncClient,
    save_token: dict[str, str],
) -> None:
    response = await ac_client.get(
        url='/user/me/',
        headers={'Authorization': f"Bearer {save_token['access_token']}"}
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Invalid token error: User not found'}


async def test_update_login(
    ac_client: AsyncClient,
    save_token: dict[str, str],
) -> None:
    response = await ac_client.post(
        url='/login',
        data={
            'username': 'user_update',
            'password': 'pass_update'
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'Bearer'
    save_token['access_token'] = response.json()['access_token']


async def test_update_read(
    ac_client: AsyncClient,
    save_token: dict[str, str],
) -> None:
    response = await ac_client.get(
        url='/user/me/',
        headers={'Authorization': f"Bearer {save_token['access_token']}"}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['username'] == 'user_update'
    assert response.json()['email'] == 'update@update.com'


async def test_create_referral_code(
    ac_client: AsyncClient,
    save_token: dict[str, str],
    save_response_data: dict[str, str]
) -> None:
    response = await ac_client.patch(
        url='/user/me/referralcode/',
        headers={'Authorization': f"Bearer {save_token['access_token']}"},
        data={'expire_timedelta_day': 30}
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['referal_code'] is not None
    assert response.json()['exp_ref_code'] is not None
    save_response_data.update(response.json())


async def test_create_referral_code_alredy_exist(
    ac_client: AsyncClient,
    save_token: dict[str, str],
    save_response_data: dict[str, str]
) -> None:
    response = await ac_client.patch(
        url='/user/me/referralcode/',
        headers={'Authorization': f"Bearer {save_token['access_token']}"},
        data={'expire_timedelta_day': 30}
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': f" Refarral code alredy exist. "
        f"Your code: '{save_response_data.get('referal_code')}' "
    }


async def test_registration_user_with_code(
    registration_with_code_good: dict[str, str],
    ac_client: AsyncClient,
    save_response_data_user_2: dict[str, str]
) -> None:
    response = await ac_client.post(
        url='/registration/',
        params=registration_with_code_good
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['username'] == registration_with_code_good.get('username')
    assert response.json()['email'] == registration_with_code_good.get('email')
    assert response.json()['is_active'] is True
    save_response_data_user_2.update(response.json())


async def test_get_all_referrals(
    ac_client: AsyncClient,
    save_token: dict[str, str],
    save_response_data_user_2: dict[str, str]
) -> None:
    response = await ac_client.get(
        url='/user/me/referrals/',
        headers={'Authorization': f"Bearer {save_token['access_token']}"}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()[0]['username'] == save_response_data_user_2['username']
    assert response.json()[0]['email'] == save_response_data_user_2['email']


async def test_receive_code_by_email(
    save_response_data: dict[str, str],
    ac_client: AsyncClient
) -> None:
    response = await ac_client.get(
        url='/getcode/update@update.com'
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['email'] == 'update@update.com'
    assert response.json()['referal_code'] == save_response_data['referal_code']


async def test_get_info_about_referrals(
    save_response_data: dict[str, str],
    save_response_data_user_2: dict[str, str],
    ac_client: AsyncClient
) -> None:
    response = await ac_client.get(
        url=f"/referrals/{save_response_data['id']}"
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()[0]['id'] == save_response_data_user_2['id']
    assert response.json()[0]['username'] == save_response_data_user_2['username']


async def test_delete_referral_code(
    ac_client: AsyncClient,
    save_token: dict[str, str],
) -> None:
    response = await ac_client.delete(
        url='/user/me/referralcode/',
        headers={'Authorization': f"Bearer {save_token['access_token']}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'detail': 'Referral code is deleted'}


async def test_receive_code_has_been_delet(
    ac_client: AsyncClient
) -> None:
    response = await ac_client.get(
        url='/getcode/update@update.com'
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Referral code not activated or expire referral code'}


async def test_user_deactivate(
    ac_client: AsyncClient,
    save_token: dict[str, str],
) -> None:
    response = await ac_client.delete(
        url='/user/me/',
        headers={'Authorization': f"Bearer {save_token['access_token']}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'detail': 'Username is deleted'}


async def test_read_user_deactivate(
    ac_client: AsyncClient,
    save_token: dict[str, str],
) -> None:
    response = await ac_client.get(
        url='/user/me/',
        headers={'Authorization': f"Bearer {save_token['access_token']}"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'User not found'}
