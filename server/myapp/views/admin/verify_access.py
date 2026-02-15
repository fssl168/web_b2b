from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view

from myapp.handler import APIResponse


@api_view(['POST'])
def verify_access(request):
    """
    验证后台访问密码
    """
    try:
        password = request.data.get('password')
        
        # 验证必填字段
        if not password:
            return APIResponse(code=1, msg='访问密码不能为空')
        
        # 验证密码
        if password != settings.ADMIN_ACCESS_PASSWORD:
            return APIResponse(code=1, msg='访问密码错误')
        
        # 验证成功
        return APIResponse(code=0, msg='访问验证成功')
    except Exception as e:
        return APIResponse(code=1, msg='验证失败: ' + str(e))
