import httpx
from fastapi import BackgroundTasks, Depends

from src.api.info.repository import InfoRepository
from src.database.models import User
from src.database.redis_tools import RedisCache


class ReceiveCodeEmailService:

    __slots__ = ['repository', 'cache_repo']

    def __init__(
        self,
        repository: InfoRepository = Depends(),
    ) -> None:
        self.repository = repository
        self.cache_repo = RedisCache()

    async def get_code(self, email: str, background_tasks: BackgroundTasks) -> User:
        '''Получить реферальный код'''
        cache = await self.cache_repo.get_email_user(email)
        if cache:
            return cache
        else:
            try:
                user = await self.repository.read_user_at_email(email)
            except ValueError as e:
                raise e
        background_tasks.add_task(self.cache_repo.set_email_user, user)
        return user


class InfoService:

    __slots__ = ['repository', 'cache_repo']

    def __init__(
        self,
        repository: InfoRepository = Depends(),
    ) -> None:
        self.repository = repository
        self.cache_repo = RedisCache()

    async def about_referrals(self, id: str, background_tasks: BackgroundTasks) -> list[User]:
        '''Получить информацию о рефералах по id рефера'''
        cache = await self.cache_repo.get_about_referrals_with_id(id)
        if cache:
            return cache
        result = await self.repository.get_users_id_referal(id)
        if result != []:
            background_tasks.add_task(
                self.cache_repo.set_about_referrals_with_id, id=id, items=result)
            return result
        raise ValueError('Referrals not found')


class EmailHunter:

    __slots__ = ['email', 'api_key', 'url']

    def __init__(self, email: str, api_key: str) -> None:
        self.email = email.strip()
        self.api_key = api_key.strip()
        self.url = 'https://api.hunter.io/v2/email-verifier'

    async def check_email(self):
        '''Использовать emailhunter.co для проверки указанного email адреса'''
        async with httpx.AsyncClient() as client:
            result = await client.get(
                url=self.url,
                params={
                    'email': self.email,
                    'api_key': self.api_key
                }
            )
            return result.json()
