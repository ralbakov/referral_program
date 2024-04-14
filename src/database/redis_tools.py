import pickle

from redis import Redis  # noqa
from redis import asyncio as aioredis

from core.config import settings
from src.database.models import User


class MetaSingleton(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class RedisCache(metaclass=MetaSingleton):
    _redis = None  # type: Redis

    def __init__(self):
        if self._redis is None:
            self._redis = aioredis.from_url(settings.cache.url)

    async def set_user(self, username: str, item: User) -> None:
        await self._redis.set(  # type: ignore
            username,
            pickle.dumps(item),
            ex=settings.cache.exp_second_set
        )
        return None

    async def get_user(self, username: str) -> User | None:
        result = await self._redis.get(username)  # type: ignore
        if result:
            return pickle.loads(result)
        return None

    async def del_user(self, username: str) -> None:
        await self._redis.delete(username)  # type: ignore
        return None

    async def set_email_user(self, email: str, item: User) -> None:
        await self._redis.set(  # type: ignore
            email,
            pickle.dumps(item),
            ex=300
        )
        return None

    async def get_email_user(self, email: str) -> User | None:
        results = await self._redis.get(email)  # type: ignore
        if results:
            return pickle.loads(results)
        return None

    async def delete_email_user(self, email: str) -> None:
        await self._redis.delete(email)  # type: ignore
        return None

    async def set_about_referrals_with_id(self, id: str, items: list[User]) -> None:
        await self._redis.set(  # type: ignore
            id,
            pickle.dumps(items),
            ex=300
        )
        return None

    async def get_about_referrals_with_id(self, id: str) -> list[User] | None:
        results = await self._redis.get(id)  # type: ignore
        if results:
            return pickle.loads(results)
        return None
