from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from src.auth import utils as auth_utils
from src.auth.repository import ResetPasswordRepository, UserAuthRepository
from src.auth.schemas import ChangePassword, Token, UserRegistration
from src.database.models import User
from src.database.redis_tools import RedisCache

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


class UserRegistrationService:
    '''Сервис для регистрации пользователя'''

    __slots__ = ['repository', 'cache_repo']

    def __init__(
        self,
        repository: UserAuthRepository = Depends(),
    ) -> None:

        self.repository = repository
        self.cache_repo = RedisCache()

    async def create(
        self,
        user: UserRegistration,
    ) -> User:
        '''Создать пользователя'''
        result = await self.repository.create(user)
        await self.cache_repo.set_user(result.username, result)
        return result


class UserAuthService:
    '''Сервис для авторизации пользователя'''

    __slots__ = ['repository', 'form_data', 'cache_repo']

    def __init__(
        self,
        repository: UserAuthRepository = Depends(),
        form_data: OAuth2PasswordRequestForm = Depends(),
    ) -> None:

        self.repository = repository
        self.form_data = form_data
        self.cache_repo = RedisCache()

    async def validate_auth_user(self) -> User:
        '''Проверка данных пользователя'''
        user = await self.repository.read(self.form_data.username.strip())
        if not user:
            raise ValueError('Invalid username')

        if not auth_utils.validate_password(
            password=self.form_data.password.strip(),
            hashed_password=user.hashed_password,
        ):
            raise ValueError('Invalid password')

        if not user.is_active:
            raise ValueError('User not found')
        await self.cache_repo.set_user(self.form_data.username.strip(), user)
        return user


class TokenService:
    '''Сервис для работы с токеном'''
    __slots__ = ['__user']

    def __init__(
        self,
        user: UserAuthService = Depends()
    ):
        self.__user = user

    async def create_access_jwt(self) -> Token:
        '''Создать токен'''
        auth_user = await self.__user.validate_auth_user()
        jwt_payload = {
            'sub': str(auth_user.id),
            'username': auth_user.username,
            'email': auth_user.email,
        }
        token = auth_utils.encode_jwt(jwt_payload)
        return Token(
            access_token=token,
            token_type='Bearer'
        )


class CurrentSessionService:
    '''Сервис для работы с текущим пользователем'''

    __slots__ = ['token', 'repository', 'cache_repo']

    def __init__(
        self,
        token: str = Depends(oauth2_scheme),
        repository: UserAuthRepository = Depends(),

    ) -> None:
        self.token = token
        self.repository = repository
        self.cache_repo = RedisCache()

    async def get_token_payload(self) -> dict:
        '''Получить токен'''
        try:
            payload = auth_utils.decode_jwt(token=self.token)
        except InvalidTokenError as e:
            raise InvalidTokenError(f'Invalid token error: {e}')
        return payload

    async def get_auth_user(self) -> User:
        '''Проверить авторизацию пользователя'''
        payload = await self.get_token_payload()
        username: str | None = payload.get('username')
        if username is None:
            raise InvalidTokenError('Invalid token error: User not found')
        cache = await self.cache_repo.get_user(username)
        if cache:
            return cache
        user = await self.repository.read(username)
        if user:
            await self.cache_repo.set_user(username, user)
            return user
        raise InvalidTokenError('Invalid token error: User not found')

    async def get_active_auth_user(self) -> User:
        '''Проверить активен ли пользователь'''
        user = await self.get_auth_user()
        if user.is_active:
            return user
        raise ValueError('User not found')


class ResetPasswordService:
    '''Сервис для сброса пароля'''

    __slots__ = ['repository']

    def __init__(
        self,
        repository: ResetPasswordRepository = Depends(),
    ) -> None:

        self.repository = repository

    async def create_reset_key(
        self,
        email: str,
    ) -> str:
        '''Создать ключ для сброса'''
        try:
            return await self.repository.create_reset_key(email)
        except ValueError as e:
            raise e

    async def send_reset_key(
        self,
        email: str,
    ) -> None:
        '''Отправить ключ для сброса пароля'''
        key = await self.create_reset_key(email)
        auth_utils.send_key_for_reset_password(email, key)
        return None

    async def change_password(
        self,
        data: ChangePassword,
    ) -> None:
        '''Изменить пароль'''
        await self.repository.change_password(data)
        return None
