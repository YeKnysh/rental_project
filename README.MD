# Rental API

Django + DRF + Swagger (drf-spectacular). Auth = **session (cookie)**.

## Как запустить ЛОКАЛЬНО (без Docker)

1. Установи зависимости:
pip install -r requirements.txt

markdown
Копировать код
2. Создай `.env` (см. раздел “.env / .env.example” ниже).
3. Прогони миграции:
python manage.py migrate

markdown
Копировать код
4. (Опционально) создай суперпользователя:
python manage.py createsuperuser

markdown
Копировать код
5. Запусти сервер:
python manage.py runserver

markdown
Копировать код
6. Проверь:
- Swagger: `http://127.0.0.1:8000/api/docs`
- Redoc: `http://127.0.0.1:8000/api/redoc`
- Admin: `http://127.0.0.1:8000/admin/`
- Логин формой (сессия): `http://127.0.0.1:8000/api-auth/login/`

**Важно про авторизацию в Swagger:** кнопки “Authorize” может не быть — это нормально.  
Залогинься на странице `/api-auth/login/`, вернись в `/api/docs`, обнови — Swagger возьмёт cookie `sessionid`.

## .env / .env.example

- `.env.example` — шаблон, его **коммитим**.
- `.env` — твои реальные переменные, **не коммитим**.

Пример `.env.example`:
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000

Учебный сервер MySQL (как в проекте)
DATABASE_URL=mysql://ich1:ich1_password_ilovedbs@ich-edit.edu.itcareerhub.de:3306/ich1_rental_knysh?charset=utf8mb4

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@rental.local

scss
Копировать код

Сгенерировать **SECRET_KEY** (любой способ):
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"

markdown
Копировать код
Вставь полученное значение в `SECRET_KEY=` в **.env**.

## Docker (если хочешь контейнер)

### Файлы
- `Dockerfile` — в корень репозитория (имя **без расширения**, просто `Dockerfile`).
- (Опционально) `docker-compose.yml` — тоже в корень.

### Сборка и запуск **через один Dockerfile**
1. Построй образ:
docker build -t rental:dev .

markdown
Копировать код
2. Прогони миграции внутри контейнера (один раз, переопределим команду):
docker run --rm --env-file .env rental:dev python manage.py migrate

markdown
Копировать код
3. Запусти сервер:
docker run --rm --env-file .env -p 8000:8000 rental:dev

markdown
Копировать код
Открой `http://127.0.0.1:8000/api/docs`

### Быстрый старт через docker-compose (опционально)
Если нужен локальный MySQL в Docker — используй `docker-compose.yml` и в `.env` поставь:
DATABASE_URL=mysql://app:app@db:3306/rental?charset=utf8mb4

makefile
Копировать код
Далее:
docker compose up --build

markdown
Копировать код

## Маршруты (основные)
- `/api/v1/users/register/` — регистрация + автологин (cookie)
- `/api/v1/users/me/` — текущий пользователь
- `/api/v1/listings/` — объявления (публичные GET, авторизованный владелец — write)
- `/api/v1/bookings/` — бронирования + действия: `confirm`, `decline`, `cancel`
- `/api/v1/reviews/` — отзывы (1 на пользователя и объявление)
- `/api/v1/statistics/` — агрегаты (summary, bookings_by_status, top_cities, owner_dashboard)

## Seed (необязательно)
Только если нужно быстро наполнить БД демо-данными:
python manage.py shell -c "from utils.seed import seed_min; seed_min()"

откатить:
python manage.py shell -c "from utils.seed import unseed_min; unseed_min()"
graphql
Копировать код
Демо логины:  
admin@example.com / Admin123!  
owner1@example.com / Owner123!  
owner2@example.com / Owner123!  
customer1@example.com / Customer123!
