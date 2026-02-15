# Create your views here.

from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.throttling import AnonRateThrottle
from rest_framework.permissions import AllowAny

from myapp import utils
from myapp.handler import APIResponse
from myapp.models import BasicGlobal
from myapp.serializers import InquirySerializer, BasicGlobalSerializer
from myapp.utils import send_email
from server.settings import SMTP_SERVER, SENDER_EMAIL, SENDER_PASS


class MyRateThrottle(AnonRateThrottle):
    # 限流 每小时10次
    THROTTLE_RATES = {"anon": "10/hour"}


@api_view(['POST'])
@throttle_classes([MyRateThrottle])
@permission_classes([AllowAny])
def create(request):
    data = request.data.copy()
    data['ip'] = utils.get_ip(request)
    serializer = InquirySerializer(data=data)
    if serializer.is_valid():
        serializer.save()

        basicGlobal = BasicGlobal.get_solo()
        basicGlobalSerializer = BasicGlobalSerializer(basicGlobal, many=False)
        global_email = basicGlobalSerializer.data['global_email']

        # 发送邮件
        send_email(
            subject="询盘通知",
            receivers=global_email,  # 可以是字符串或者列表
            content="您好，<p>收到了询盘通知，请登录网站后台查看</p>",
            smtp_server=SMTP_SERVER,
            port=465,
            sender_email=SENDER_EMAIL,
            sender_pass=SENDER_PASS
        )

        return APIResponse(code=0, msg='创建成功', data=serializer.data)
    else:
        print(serializer.errors)

    return APIResponse(code=1, msg='创建失败')
