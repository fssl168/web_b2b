import time
import hashlib
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class AdminProtectionMiddleware(MiddlewareMixin):
    """
    后台入口防黑保护中间件
    """
    
    # 允许访问的IP白名单
    ALLOWED_IPS = getattr(settings, 'ADMIN_ALLOWED_IPS', [])
    
    # 后台访问密码（可选）
    ACCESS_PASSWORD = getattr(settings, 'ADMIN_ACCESS_PASSWORD', '')
    
    # 访问密码有效期（秒）
    PASSWORD_EXPIRE_TIME = getattr(settings, 'ADMIN_PASSWORD_EXPIRE_TIME', 3600)
    
    # 后台入口路径
    ADMIN_PATH_PREFIX = getattr(settings, 'ADMIN_PATH_PREFIX', 'admin')
    
    # 公开访问的API路径（不需要IP白名单和密码验证）
    PUBLIC_PATHS = [
        '/myapp/admin/captcha',
        '/myapp/admin/captcha/key',
        '/myapp/admin/basicGlobal/listInfo',
        '/myapp/admin/adminLogin',
    ]
    
    def process_request(self, request):
        """
        处理请求
        """
        # 获取请求路径
        path = request.path
        
        # 检查是否是公开访问的API
        if path in self.PUBLIC_PATHS:
            return None
        
        # 检查是否是后台相关路径
        if f'/{self.ADMIN_PATH_PREFIX}' in path:
            # 1. IP白名单检查
            if self.ALLOWED_IPS:
                client_ip = self.get_client_ip(request)
                if client_ip not in self.ALLOWED_IPS:
                    return JsonResponse({
                        'code': 1,
                        'msg': 'Access denied: IP not allowed'
                    }, status=403)
            
            # 2. 访问密码检查（如果设置了）
            if self.ACCESS_PASSWORD:
                # 从cookie获取访问密码
                access_token = request.COOKIES.get('admin_access_token')
                
                # 验证访问密码
                if not self.validate_access_token(access_token):
                    # 检查是否是密码验证请求
                    if request.path == f'/{self.ADMIN_PATH_PREFIX}/verify-access':
                        # 处理密码验证
                        password = request.POST.get('password')
                        if password == self.ACCESS_PASSWORD:
                            # 生成访问令牌
                            token = self.generate_access_token()
                            response = JsonResponse({
                                'code': 0,
                                'msg': 'Access granted'
                            })
                            # 设置cookie
                            response.set_cookie(
                                'admin_access_token',
                                token,
                                max_age=self.PASSWORD_EXPIRE_TIME,
                                httponly=True,
                                secure=request.is_secure(),
                                samesite='Strict'
                            )
                            return response
                        else:
                            return JsonResponse({
                                'code': 1,
                                'msg': 'Invalid access password'
                            }, status=401)
                    else:
                        # 重定向到密码验证页面
                        return JsonResponse({
                            'code': 1,
                            'msg': 'Access password required',
                            'redirect_to': f'/{self.ADMIN_PATH_PREFIX}/access-verify'
                        }, status=401)
        
        return None
    
    def get_client_ip(self, request):
        """
        获取客户端IP
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def generate_access_token(self):
        """
        生成访问令牌
        """
        # 使用时间戳和访问密码生成令牌
        timestamp = str(int(time.time()))
        token_data = f"{timestamp}:{self.ACCESS_PASSWORD}"
        token = hashlib.md5(token_data.encode()).hexdigest()
        return f"{timestamp}:{token}"
    
    def validate_access_token(self, token):
        """
        验证访问令牌
        """
        if not token:
            return False
        
        try:
            # 解析令牌
            timestamp_str, token_hash = token.split(':')
            timestamp = int(timestamp_str)
            
            # 检查是否过期
            current_time = int(time.time())
            if current_time - timestamp > self.PASSWORD_EXPIRE_TIME:
                return False
            
            # 验证令牌哈希
            token_data = f"{timestamp}:{self.ACCESS_PASSWORD}"
            expected_hash = hashlib.md5(token_data.encode()).hexdigest()
            
            return token_hash == expected_hash
        except:
            return False
