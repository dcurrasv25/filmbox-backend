from rest_framework import authentication
from rest_framework import exceptions
from .models import FilmBoxUser


class FilmBoxAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # 1. Buscamos el header de Authorization
        auth = request.headers.get("Authorization")

        # 2. Si no hay header o no empieza con Bearer, no autenticamos (pasamos al siguiente método)
        if not auth or not auth.startswith("Bearer "):
            return None

        # 3. Extraemos el token
        token = auth[len("Bearer "):].strip()

        # 4. Buscamos al usuario en TU tabla FilmBoxUser
        try:
            user = FilmBoxUser.objects.get(session_token=token)
        except FilmBoxUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid session token')

        # 5. Devolvemos al usuario.
        # Esto hace que 'request.user' se rellene automáticamente.
        return (user, None)