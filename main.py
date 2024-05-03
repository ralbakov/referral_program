from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

# from src.database.config import init_db
from src.api.auth.router import auth_router
from src.api.info.router import info_router
from src.api.user.router import user_router
from src.database.redis_tools import RedisCache


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await init_db() # создание инициалзацию делаю через alembic upgrade head
    RedisCache()
    yield

app = FastAPI(lifespan=lifespan,
              title='API сервис реферальной системы',
              version='1.0',
              openapi_tags=[
                  {
                      'name': 'AUTH',
                      'description': 'Работа с регистрацией и аутентификацией',
                  },
                  {
                      'name': 'INFO',
                      'description': 'Работа с информационными сервисами не '
                                     'требующих авторизации пользователя',
                  },
                  {
                      'name': 'USER',
                      'description': 'Работа с авторизованными пользователями',
                  },
              ],
              )

app.include_router(auth_router)
app.include_router(info_router)
app.include_router(user_router)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
