from fastapi import BackgroundTasks, Depends
from jwt import InvalidTokenError

from src.api.auth.service import CurrentSessionService
from src.api.user.repository import UserRepository
from src.api.user.schemas import UserUpdate
from src.database.models import User
from src.database.redis_tools import RedisCache


class UserService:

    __slots__ = ['user', 'repository', 'cache_repo']

    def __init__(self,
                 current: CurrentSessionService = Depends(),
                 repository: UserRepository = Depends(),
                 ) -> None:
        self.user = current.get_active_auth_user()
        self.repository = repository
        self.cache_repo = RedisCache()

    async def read(self) -> User:
        try:
            return await self.user
        except ValueError as e:
            raise e
        except InvalidTokenError as e:
            raise e

    async def update(self, data: UserUpdate, background_tasks: BackgroundTasks) -> User:
        user = await self.user
        background_tasks.add_task(self.cache_repo.del_user, user.username)
        try:
            result = await self.repository.update(user, data)
        except ValueError as e:
            raise e
        background_tasks.add_task(self.cache_repo.set_user, result)
        return result

    async def deactivate(self, background_tasks: BackgroundTasks) -> None:
        user = await self.user
        background_tasks.add_task(self.repository.deactivate, user)
        background_tasks.add_task(self.cache_repo.del_user, user.username)
        return None

    async def get_all_referral(self, background_tasks: BackgroundTasks) -> list[User]:
        user = await self.user
        cache = await self.cache_repo.get_about_referrals_with_id(str(user.id))
        if cache:
            return cache
        result = await self.repository.get_all_referral(user.id)
        background_tasks.add_task(
            self.cache_repo.set_about_referrals_with_id, id=str(user.id), items=result)
        return result

    async def create_ref_code(self, expire_timedelta_day: int | None, background_tasks: BackgroundTasks) -> User:
        user = await self.user
        try:
            result = await self.repository.create_referral_code(user, expire_timedelta_day)
        except ValueError as e:
            raise e
        background_tasks.add_task(self.cache_repo.set_user, result)
        return result

    async def delete_ref_code(self, background_tasks: BackgroundTasks) -> None:
        user = await self.user
        result = await self.repository.delete_referral_code(user)
        background_tasks.add_task(
            self.cache_repo.delete_email_user, user.email)
        background_tasks.add_task(self.cache_repo.set_user, result)
        return None
