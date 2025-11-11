from rest_framework.authentication import SessionAuthentication

class DevSessionAuthentication(SessionAuthentication):
    """
    DEV only: отключаем CSRF-проверку для запросов из Swagger UI,
    чтобы session-auth работала без 403/редиректов на логин.
    """
    def enforce_csrf(self, request):
        return
