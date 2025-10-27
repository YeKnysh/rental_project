# rental_project/settings.py
from pathlib import Path
import os
import environ
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ---- env ----
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# ---- apps ----
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # our apps
    "apps.users.apps.UsersConfig",
    "apps.listings.apps.ListingsConfig",
    "apps.bookings.apps.BookingsConfig",
    "apps.reviews.apps.ReviewsConfig",
    "apps.booking_statistics.apps.BookingStatisticsConfig",
    "apps.common.apps.CommonConfig",

    # third-party
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "drf_spectacular_sidecar",
]

# ---- middleware ----
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "rental_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "rental_project.wsgi.application"

# ---- db ----
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",  # используется ТОЛЬКО если переменной нет
        conn_max_age=0,  # <-- это мы поменяли (было 600). База остаётся той, что в DATABASE_URL (MySQL)
    )
}


# ---- auth / users ----
AUTH_USER_MODEL = "users.User"

# login по e-mail
AUTHENTICATION_BACKENDS = [
    "apps.users.backends.EmailModelBackend",        # email + password
    "django.contrib.auth.backends.ModelBackend",    # fallback (админка и т.п.)
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---- i18n / tz ----
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---- static / media ----
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# WhiteNoise: сжатые и хешированные статики для продакшена
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---- DRF ----
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,

    # ВАЖНО: приоритет basicAuth над сессией, чтобы Swagger не цеплял admin sessionid
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# ---- email ----
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@rental.local")

# ---- drf-spectacular ----
SPECTACULAR_SETTINGS = {
    "TITLE": "Rental API",
    "DESCRIPTION": "Listings, Bookings, Reviews, Statistics",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # чтобы не выбрасывало авторизацию при перезагрузках UI
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True},
}
