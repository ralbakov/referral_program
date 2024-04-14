# Rest API реферальной системы c регистрацией и аутентификацией пользователя (JWT, Oauth 2.0)

## Стек

API - FlaskAPI  \
ORM - sqlalchemy  \
БД - PostgreSQL  \
DevOps - Docker \
Cache - Redis

## Копирование репозитория

```bash
git clone https://github.com/ralbakov/referral_program.git
```

После завершения клонирования репозитория, необходимо перейти в папку "referral_program".
Для этого в терминале выполните нижеуказанную команду:

```bash
cd referral_program
```

## Тестирование

Находясь в папке "referral_program", в командной строке выполните команду:

```bash
docker-compose -f referral_api_tests.yml up
```

## Запуск

Находясь в папке "referral_program", в командной строке выполните команду:

```bash
docker-compose -f referral_api_prod.yml up
```
<!-- markdownlint-disable MD033 -->
После сообщения "INFO: Uvicorn running on ..."
Перейдите по ссылке:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
