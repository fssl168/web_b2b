from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from myapp import utils
from myapp.models import User


# 后台接口认证
class AdminTokenAuthtication(BaseAuthentication):
    def authenticate(self, request):
        adminToken = request.META.get("HTTP_ADMINTOKEN")

        if not adminToken or adminToken == '':
            # 当token为空时，返回None让DRF继续处理其他认证方法
            # 这是标准的DRF认证流程，避免了潜在的认证漏洞
            return None

        try:
            user = User.objects.get(admin_token=adminToken)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("无效的认证token")

        # 检查token是否过期
        ts = utils.get_timestamp()
        try:
            if int(user.exp) < ts:
                raise exceptions.AuthenticationFailed("token已过期")
        except (ValueError, TypeError):
            raise exceptions.AuthenticationFailed("无效的过期时间")

        # 返回用户对象和token，符合DRF认证标准
        return (user, adminToken)

