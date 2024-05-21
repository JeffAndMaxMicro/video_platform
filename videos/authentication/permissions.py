from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class ExternalServicePermission(BasePermission):
    def has_permission(self, request, view):
        return True
        token = request.headers.get('Authorization')
        if not token:
            raise PermissionDenied('No token provided')

        # 假设外部授权服务的URL如下
        auth_service_url = 'https://external-auth-service.com/check-permission'
        
        response = requests.post(auth_service_url, headers={'Authorization': token}, json={
            'user_id': request.user.id,
            'endpoint': view.__class__.__name__,  # 或者其他你认为合适的标识
            'method': request.method
        })

        if response.status_code != 200 or not response.json().get('has_permission', False):
            raise PermissionDenied('You do not have permission to access this resource')

        return True