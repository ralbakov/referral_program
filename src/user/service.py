from fastapi import Depends
from jwt import InvalidTokenError

from src.auth.service import CurrentSessionService
from src.database.models import User
from src.database.redis_tools import RedisCache
from src.user.repository import UserRepository
from src.user.schemas import UserUpdate


class UserService:

    __slots__ = ['current', 'repository', 'cache_repo']

    def __init__(self,
                 current: CurrentSessionService = Depends(),
                 repository: UserRepository = Depends(),
                 ) -> None:
        self.current = current
        self.repository = repository
        self.cache_repo = RedisCache()

    async def read(self) -> User:
        try:
            return await self.current.get_active_auth_user()
        except ValueError as e:
            raise e
        except InvalidTokenError as e:
            raise e

    async def update(self, data: UserUpdate) -> User:
        user = await self.current.get_active_auth_user()
        await self.cache_repo.del_user(user.username)
        try:
            result = await self.repository.update(user, data)
        except ValueError as e:
            raise e
        await self.cache_repo.set_user(result.username, result)
        return result

    async def deactivate(self) -> None:
        user = await self.current.get_active_auth_user()
        await self.repository.deactivate(user)
        await self.cache_repo.del_user(user.username)
        return None

    async def get_all_referral(self) -> list[User]:
        user = await self.current.get_active_auth_user()
        cache = await self.cache_repo.get_about_referrals_with_id(str(user.id))
        if cache:
            return cache
        result = await self.repository.get_all_referral(user.id)
        await self.cache_repo.set_about_referrals_with_id(str(user.id), result)
        return result

    async def create_ref_code(self, expire_timedelta_day: int | None) -> User:
        user = await self.current.get_active_auth_user()
        try:
            result = await self.repository.create_referral_code(user, expire_timedelta_day)
        except ValueError as e:
            raise e
        await self.cache_repo.set_user(result.username, result)
        return result

    async def delete_ref_code(self) -> None:
        user = await self.current.get_active_auth_user()
        result = await self.repository.delete_referral_code(user)
        await self.cache_repo.delete_email_user(user.email)
        await self.cache_repo.set_user(result.username, result)
        return None
