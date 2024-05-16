import jwt
from django.conf import settings
from django.http import JsonResponse

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                request.user_id = payload['user_id']
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, IndexError):
                return JsonResponse({'error': 'Invalid token'}, status=401)
        
        response = self.get_response(request)
        return response