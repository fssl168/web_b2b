from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from myapp import utils
from myapp.models import User


# 后台接口认证
class AdminTokenAuthtication(BaseAuthentication):
    def authenticate(self, request):
        adminToken = request.META.get("HTTP_ADMINTOKEN")

        if not adminToken or adminToken == '':
            return None

        try:
            user = User.objects.get(admin_token=adminToken)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("无效的认证token")

        ts = utils.get_timestamp()
        try:
            if int(user.exp) < ts:
                raise exceptions.AuthenticationFailed("token已过期")
        except (ValueError, TypeError):
            raise exceptions.AuthenticationFailed("无效的过期时间")

        return (user, adminToken)

