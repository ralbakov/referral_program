import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy_utils import create_database, drop_database  # noqa # type: ignore

from core.config import settings
from main import app
from src.database.config import get_async_session
from src.database.models import Base

# # used on local
# create_database(settings.db.create_db_url + '_test') # used on local
# engine = create_async_engine(settings.db.url + '_test', poolclass=NullPool) # used on local

# used on docker
engine = create_async_engine(settings.db.url, poolclass=NullPool)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_db


@pytest.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # # used on local
    # drop_database(settings.db.create_db_url + '_test')  # used on local

    # used on docker
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
async def ac_client():
    async with AsyncClient(app=app, base_url='http://test/auth') as ac_client:
        yield ac_client


@pytest.fixture(scope='session')
def save_token() -> dict[str, str]:
    return {}


@pytest.fixture(scope='session')
def save_response_data() -> dict[str, str]:
    return {}


@pytest.fixture
def registration_with_code_good(save_response_data: dict[str, str]) -> dict[str, str | None]:
    referal_code = save_response_data.get('referal_code')
    data = {
        'referal_code': referal_code,
        'username': 'user2',
        'email': 'user2@user2.user',
        'password': 'user2'
    }
    return data


@pytest.fixture(scope='session')
def save_response_data_user_2() -> dict[str, str]:
    return {}
