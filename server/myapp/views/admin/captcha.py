# 验证码视图
from captcha.image import ImageCaptcha
import random
import string
import io
from PIL import Image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse
from django.core.cache import cache
from myapp.handler import APIResponse


def generate_random_code(length=4):
    """生成随机验证码"""
    characters = string.digits  # 只使用数字，避免混淆
    return ''.join(random.choice(characters) for _ in range(length))


def create_captcha_image():
    """创建验证码图片"""
    code = generate_random_code(4)

    # 创建ImageCaptcha实例，调整字体大小以确保数字完全可见
    image = ImageCaptcha(
        width=140, 
        height=60,
        font_sizes=[32]  # 增大字体大小
    )

    # 生成验证码图片
    data = image.generate(code)

    # 将图片保存到内存
    image_io = io.BytesIO()
    image.write(code, image_io)

    return code, image_io.getvalue()


class CaptchaView(APIView):
    """获取验证码"""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # 生成验证码
            code, image_data = create_captcha_image()

            # 使用前端传递的key，或者生成一个新的
            captcha_key = request.GET.get('key', f"captcha_{random.randint(100000, 999999)}")

            # 将验证码存储到缓存中，5分钟过期
            cache.set(captcha_key, code, 300)

            # 返回验证码图片
            return HttpResponse(image_data, content_type='image/png')

        except Exception as e:
            return APIResponse(code=1, msg=f'验证码生成失败: {str(e)}')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_captcha_key(request):
    """获取验证码key"""
    try:
        captcha_key = f"captcha_{random.randint(100000, 999999)}"
        return APIResponse(code=0, msg='获取成功', data={'key': captcha_key})
    except Exception as e:
        return APIResponse(code=1, msg=f'获取失败: {str(e)}')
