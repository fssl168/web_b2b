import logging
import re
from django.utils.deprecation import MiddlewareMixin
from myapp import utils
from myapp.security.incident_response import SecurityIncidentResponse

logger = logging.getLogger('myapp')

# XSS攻击模式
XSS_PATTERNS = [
    r'<script[^>]*>.*?</script>',
    r'javascript:',
    r'onerror\s*=',
    r'onload\s*=',
    r'onclick\s*=',
    r'onmouseover\s*=',
    r'onfocus\s*=',
    r'onblur\s*=',
    r'<iframe[^>]*>',
    r'<embed[^>]*>',
    r'<object[^>]*>',
    r'eval\s*\(',
    r'document\.cookie',
    r'document\.write',
    r'window\.location',
    r'<img[^>]+onerror',
    r'<svg[^>]+onload',
]

# CSRF攻击检测配置
CSRF_SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS', 'TRACE']
CSRF_TRUSTED_ORIGINS = ['localhost', '127.0.0.1', 'fktool.com']

# SQL注入攻击模式
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b)",
    r"(\b(UNION|JOIN)\b.*\b(SELECT|FROM)\b)",
    r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
    r"(\b(OR|AND)\b\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
    r"(--\s*$)",
    r"(;\s*$)",
    r"(/\*.*\*/)",
    r"(@@version)",
    r"(@@datadir)",
    r"(CONCAT\s*\()",
    r"(CHAR\s*\()",
    r"(LOAD_FILE\s*\()",
    r"(INTO\s+OUTFILE)",
    r"(INTO\s+DUMPFILE)",
    r"(BENCHMARK\s*\()",
    r"(SLEEP\s*\()",
    r"(WAITFOR\s+DELAY)",
    r"(EXEC\s*\()",
    r"(EXECUTE\s*\()",
    r"(XP_CMDSHELL)",
    r"(INFORMATION_SCHEMA)",
    r"(SYSOBJECTS)",
    r"(SYSCOLUMNS)",
    r"('\s*(OR|AND)\s+')",
    r"(\bOR\b\s+'[^']*'\s*=\s*'[^']*')",
    r"(\bAND\b\s+'[^']*'\s*=\s*'[^']*')",
]


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    安全日志记录中间件
    记录登录尝试、权限变更、敏感操作等安全相关事件
    """
    
    def _check_xss(self, value):
        """
        检查字符串是否包含XSS攻击模式
        """
        if not isinstance(value, str):
            return False
        
        value_lower = value.lower()
        for pattern in XSS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        return False
    
    def _check_sql_injection(self, value):
        """
        检查字符串是否包含SQL注入模式
        """
        if not isinstance(value, str):
            return False
        
        value_upper = value.upper()
        for pattern in SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True
        return False
    
    def _check_request_for_xss(self, request):
        """
        检查请求中是否包含XSS攻击
        """
        xss_found = []
        
        # 检查GET参数
        for key, value in request.GET.items():
            if self._check_xss(value):
                xss_found.append(f"GET参数 '{key}': {value[:100]}")
        
        # 检查POST参数
        for key, value in request.POST.items():
            if self._check_xss(value):
                xss_found.append(f"POST参数 '{key}': {value[:100]}")
        
        # 检查JSON请求体
        try:
            import json
            body = request.body.decode('utf-8')
            if body:
                json_data = json.loads(body)
                if isinstance(json_data, dict):
                    for key, value in json_data.items():
                        if isinstance(value, str) and self._check_xss(value):
                            xss_found.append(f"JSON参数 '{key}': {value[:100]}")
        except Exception:
            pass
        
        return xss_found
    
    def _check_request_for_sql_injection(self, request):
        """
        检查请求中是否包含SQL注入攻击
        """
        sql_found = []
        
        # 检查GET参数
        for key, value in request.GET.items():
            if self._check_sql_injection(value):
                sql_found.append(f"GET参数 '{key}': {value[:100]}")
        
        # 检查POST参数
        for key, value in request.POST.items():
            if self._check_sql_injection(value):
                sql_found.append(f"POST参数 '{key}': {value[:100]}")
        
        # 检查JSON请求体
        try:
            import json
            body = request.body.decode('utf-8')
            if body:
                json_data = json.loads(body)
                if isinstance(json_data, dict):
                    for key, value in json_data.items():
                        if isinstance(value, str) and self._check_sql_injection(value):
                            sql_found.append(f"JSON参数 '{key}': {value[:100]}")
        except Exception:
            pass
        
        return sql_found
    
    def _check_csrf(self, request):
        """
        检查CSRF攻击尝试
        """
        # 只检查不安全的方法
        if request.method in CSRF_SAFE_METHODS:
            return None
        
        # 获取Referer头
        referer = request.META.get('HTTP_REFERER', '')
        origin = request.META.get('HTTP_ORIGIN', '')
        host = request.META.get('HTTP_HOST', '')
        
        # 检查是否有Referer或Origin头
        if not referer and not origin:
            # 对于本地IP（开发环境），放宽检测
            client_ip = request.META.get('REMOTE_ADDR', '')
            if client_ip in ['127.0.0.1', 'localhost', '::1']:
                return None
            # 对于敏感操作，缺少Referer/Origin可能是CSRF攻击
            if '/admin/' in request.path:
                return "Missing Referer and Origin headers for sensitive operation"
        
        # 检查Referer是否来自可信来源
        if referer:
            referer_host = self._extract_host(referer)
            if referer_host and not self._is_trusted_origin(referer_host):
                return f"Referer from untrusted origin: {referer_host}"
        
        # 检查Origin是否来自可信来源
        if origin:
            origin_host = self._extract_host(origin)
            if origin_host and not self._is_trusted_origin(origin_host):
                return f"Origin from untrusted source: {origin_host}"
        
        # 检查Host头是否与Referer/Origin匹配
        if host and referer:
            referer_host = self._extract_host(referer)
            # 从host中移除端口号进行比较
            host_without_port = host.split(':')[0]
            if referer_host and referer_host != host_without_port:
                return f"Host mismatch: Host={host}, Referer={referer_host}"
        
        return None
    
    def _extract_host(self, url):
        """
        从URL中提取主机名
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.split(':')[0]  # 移除端口号
        except Exception:
            return None
    
    def _is_trusted_origin(self, host):
        """
        检查主机名是否是可信来源
        """
        for trusted in CSRF_TRUSTED_ORIGINS:
            if trusted in host:
                return True
        return False
    
    def process_request(self, request):
        """
        处理请求
        """
        # 检查XSS攻击
        xss_found = self._check_request_for_xss(request)
        if xss_found:
            client_ip = utils.get_ip(request)
            user = getattr(request, 'user', None)
            
            SecurityIncidentResponse.detect_incident(
                'XSS_ATTEMPT',
                'HIGH',
                f"XSS attack detected: {', '.join(xss_found[:3])}",  # 只显示前3个
                user=user,
                ip=client_ip,
                request=request
            )
        
        # 检查SQL注入攻击
        sql_found = self._check_request_for_sql_injection(request)
        if sql_found:
            client_ip = utils.get_ip(request)
            user = getattr(request, 'user', None)
            
            SecurityIncidentResponse.detect_incident(
                'SQL_INJECTION_ATTEMPT',
                'HIGH',
                f"SQL injection detected: {', '.join(sql_found[:3])}",  # 只显示前3个
                user=user,
                ip=client_ip,
                request=request
            )
        
        # 检查CSRF攻击尝试
        csrf_issue = self._check_csrf(request)
        if csrf_issue:
            client_ip = utils.get_ip(request)
            user = getattr(request, 'user', None)
            
            SecurityIncidentResponse.detect_incident(
                'CSRF_ATTEMPT',
                'HIGH',
                f"CSRF attack attempt: {csrf_issue}",
                user=user,
                ip=client_ip,
                request=request
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
        
        # 获取用户信息（在process_response中，request.user已经被设置）
        user = getattr(request, 'user', None)
        logger.info(f"SecurityLoggingMiddleware - Path: {path}, User: {user.username if user and hasattr(user, 'username') else 'None'}, Status: {response.status_code}")
        
        # 记录登录成功/失败
        if '/adminLogin' in path and request.method == 'POST':
            logger.info(f"SecurityLoggingMiddleware - Login detected, status: {response.status_code}")
            
            # 尝试从POST数据中获取用户名
            username = request.POST.get('username', None)
            
            # 如果POST数据中没有，尝试从JSON请求体中获取
            if not username:
                try:
                    import json
                    body = request.body.decode('utf-8')
                    if body:
                        json_data = json.loads(body)
                        username = json_data.get('username', 'unknown')
                except Exception as e:
                    print(f"[SecurityLoggingMiddleware] Error parsing JSON body: {e}")
                    username = 'unknown'
            
            if response.status_code == 200:
                # 登录成功，使用POST中的用户名
                logger.info(f"SecurityLoggingMiddleware - Login success for user: {username}")
                SecurityIncidentResponse.detect_incident(
                    'LOGIN_SUCCESS',
                    'LOW',
                    f"Login success for user: {username}",
                    user=None,  # 登录时user还没有被设置
                    ip=client_ip,
                    request=request
                )
            else:
                # 登录失败，使用POST中的用户名
                SecurityIncidentResponse.detect_incident(
                    'LOGIN_FAILURE',
                    'MEDIUM',
                    f"Login failed for user: {username}",
                    user=None,
                    ip=client_ip,
                    request=request
                )
        
        # 记录敏感操作（POST, PUT, DELETE）
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
                if response.status_code < 400:  # 只记录成功的操作
                    SecurityIncidentResponse.detect_incident(
                        'SUSPICIOUS_ACTIVITY',
                        'MEDIUM',
                        f"Sensitive operation: {request.method} {path}",
                        user=user,
                        ip=client_ip,
                        request=request
                    )
        
        # 记录权限错误
        if response.status_code in [401, 403]:
            SecurityIncidentResponse.detect_incident(
                'PERMISSION_DENIED',
                'HIGH',
                f"Permission denied: {request.method} {path}",
                user=user,
                ip=client_ip,
                request=request
            )
        
        # 记录服务器错误
        if response.status_code >= 500:
            SecurityIncidentResponse.detect_incident(
                'SUSPICIOUS_ACTIVITY',
                'HIGH',
                f"Server error: {request.method} {path} - Status: {response.status_code}",
                user=user,
                ip=client_ip,
                request=request
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
        
        # 记录异常
        SecurityIncidentResponse.detect_incident(
            'SUSPICIOUS_ACTIVITY',
            'CRITICAL',
            f"Exception: {request.method} {path} - {str(exception)}",
            user=user,
            ip=client_ip,
            request=request
        )
        
        return None
