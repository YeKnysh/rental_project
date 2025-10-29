# apps/users/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailModelBackend(ModelBackend):
    """
    Authenticate strictly with e-mail + password.
    - E-mail сравнивается без учета регистра (case-insensitive).
    - Пробелы обрезаются.
    - Не даём логиниться неактивным пользователям (поведение как у ModelBackend).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Django передаёт e-mail обычно в username, но поддержим и kwargs['email'] на всякий случай
        raw_email = username or kwargs.get("email")
        if not raw_email or "@" not in str(raw_email):
            return None

        email = str(raw_email).strip().lower()
        if not password:
            return None

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
