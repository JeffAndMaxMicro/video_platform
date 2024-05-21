from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import jwt

from videoPlateform import settings

User = get_user_model()

class ExternalServiceAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('No token provided')

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Invalid token payload')
            
            # Check if the user exists in the database, if not create a new user
            user, created = User.objects.get_or_create(external_id=user_id, defaults={
                'username': payload.get('username', 'default_username'),
                'email': payload.get('email', 'default_email@example.com'),
                'external_id': user_id
            })
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            raise AuthenticationFailed('Invalid token or user not found')

        return (user, token)