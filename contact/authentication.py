from rest_framework import authentication, exceptions
from django.contrib.auth.models import User
from django.conf import settings
import jwt


class JWTAuthentication(authentication.BaseAuthentication):

    def _authenticate_credentials(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except Exception:
            msg = 'Invalid authentication. Could not decode token.'
            raise exceptions.AuthenticationFailed(msg)
        try:
            user = User.objects.get(email=payload["email"])
        except User.DoesNotExist:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)
        return (user, token)

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        if len(auth_header) != 1:
            return None
        token = auth_header[0].decode('utf-8')

        return self._authenticate_credentials(request, token)