import logging
from django.utils.deprecation import MiddlewareMixin
from myapp import utils
from myapp.security.incident_response import SecurityIncidentResponse

logger = logging.getLogger('myapp')


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    安全日志记录中间件
    记录登录尝试、权限变更、敏感操作等安全相关事件
    """
    
    def process_request(self, request):
        """
        处理请求
        """
        # 获取请求路径
        path = request.path
        
        # 获取客户端IP
        client_ip = utils.get_ip(request)
        
        # 获取用户信息
        user = getattr(request, 'user', None)
        username = user.username if user and hasattr(user, 'username') else 'anonymous'
        
        # 记录登录尝试
        if '/adminLogin' in path and request.method == 'POST':
            SecurityIncidentResponse.detect_incident(
                'LOGIN_FAILURE',
                'MEDIUM',
                f"Login attempt for user: {request.POST.get('username', 'unknown')}",
                user=user,
                ip=client_ip
            )
        
        # 记录敏感操作
        sensitive_paths = [
            '/admin/user',
            '/admin/category',
            '/admin/thing',
            '/admin/news',
            '/admin/case',
            '/admin/download',
            '/admin/faq',
            '/admin/inquiry',
            '/admin/basic'
        ]
        
        for sensitive_path in sensitive_paths:
            if sensitive_path in path and request.method in ['POST', 'PUT', 'DELETE']:
                SecurityIncidentResponse.detect_incident(
                    'SUSPICIOUS_ACTIVITY',
                    'MEDIUM',
                    f"Sensitive operation: {request.method} {path}",
                    user=user,
                    ip=client_ip
                )
        
        return None
    
    def process_response(self, request, response):
        """
        处理响应
        """
        # 获取请求路径
        path = request.path
        
        # 获取客户端IP
        client_ip = utils.get_ip(request)
        
        # 获取用户信息
        user = getattr(request, 'user', None)
        username = user.username if user and hasattr(user, 'username') else 'anonymous'
        
        # 记录登录成功/失败
        if '/adminLogin' in path and request.method == 'POST':
            if response.status_code == 200:
                SecurityIncidentResponse.detect_incident(
                    'LOGIN_SUCCESS',
                    'LOW',
                    f"Login success for user: {username}",
                    user=user,
                    ip=client_ip
                )
            else:
                SecurityIncidentResponse.detect_incident(
                    'LOGIN_FAILURE',
                    'MEDIUM',
                    f"Login failed for user: {username}",
                    user=user,
                    ip=client_ip
                )
        
        # 记录权限错误
        if response.status_code in [401, 403]:
            SecurityIncidentResponse.detect_incident(
                'PERMISSION_DENIED',
                'HIGH',
                f"Permission denied: {request.method} {path}",
                user=user,
                ip=client_ip
            )
        
        # 记录服务器错误
        if response.status_code >= 500:
            SecurityIncidentResponse.detect_incident(
                'SUSPICIOUS_ACTIVITY',
                'HIGH',
                f"Server error: {request.method} {path} - Status: {response.status_code}",
                user=user,
                ip=client_ip
            )
        
        return response
    
    def process_exception(self, request, exception):
        """
        处理异常
        """
        # 获取请求路径
        path = request.path
        
        # 获取客户端IP
        client_ip = utils.get_ip(request)
        
        # 获取用户信息
        user = getattr(request, 'user', None)
        username = user.username if user and hasattr(user, 'username') else 'anonymous'
        
        # 记录异常
        SecurityIncidentResponse.detect_incident(
            'SUSPICIOUS_ACTIVITY',
            'CRITICAL',
            f"Exception: {request.method} {path} - {str(exception)}",
            user=user,
            ip=client_ip
        )
        
        return None