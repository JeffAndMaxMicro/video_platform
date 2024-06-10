# from rest_framework.authentication import BaseAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from django.contrib.auth import get_user_model
# import jwt

# from videoPlateform import settings

# User = get_user_model()

import requests
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import jwt

User = get_user_model()

class ExternalServiceAuthentication(BaseAuthentication):
    # def authenticate(self, request):
    #     token = request.headers.get('Authorization')
    #     if not token:
    #         raise AuthenticationFailed('No token provided')

    #     # 提取实际的令牌字符串
    #     token = token.split(" ")[1] if " " in token else token

    #     # 向认证服务发送请求以验证令牌
    #     try:
    #         response = requests.post(settings.AUTH_SERVICE_URL, json={'token': token})
    #         response.raise_for_status()  # 如果请求失败，抛出HTTPError
    #     except requests.exceptions.RequestException as e:
    #         raise AuthenticationFailed(f'Authentication service error: {e}')

    #     # 解析认证服务的响应
    #     if response.status_code == 200:
    #         payload = response.json()
    #         user_id = payload.get('user_id')
    #         if not user_id:
    #             raise AuthenticationFailed('Invalid token payload')

    #         # 检查用户是否存在于数据库，如果不存在则创建新用户
    #         user, created = User.objects.get_or_create(external_id=user_id, defaults={
    #             'username': payload.get('username', 'default_username'),
    #             'email': payload.get('email', 'default_email@example.com'),
    #             'external_id': user_id
    #         })
    #     else:
    #         raise AuthenticationFailed('Invalid token or user not found')

    #     return (user, token)

    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('No token provided')

        # 提取实际的令牌字符串
        token = token.split(" ")[1] if " " in token else token

        try:
            # 解码JWT令牌而不验证签名
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get('userId')
            if not user_id:
                raise AuthenticationFailed('Invalid token payload')

            # 检查用户是否存在于数据库，如果不存在则创建新用户
            user, created = User.objects.get_or_create(external_id=user_id, defaults={
                'username': payload.get('username', 'default_username'),
                'email': payload.get('email', 'default_email@example.com'),
                'external_id': user_id
            })
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

        return (user, token)