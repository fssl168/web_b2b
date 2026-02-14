# Create your views here.
import datetime

from rest_framework.decorators import api_view, authentication_classes, throttle_classes
from rest_framework.throttling import AnonRateThrottle

from myapp import utils
from myapp.auth.authentication import AdminTokenAuthtication
from myapp.handler import APIResponse
from myapp.models import User
from myapp.permission.permission import isDemoAdminUser, check_if_demo
from myapp.serializers import UserSerializer, NormalUserSerializer
from myapp.utils import md5value, after_call, clear_cache


class UserRateThrottle(AnonRateThrottle):
    # 限流 每小时10次
    THROTTLE_RATES = {"anon": "10/h"}


@api_view(['POST'])
@throttle_classes([UserRateThrottle])
def admin_login(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return APIResponse(code=1, msg='用户名或密码不能为空')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 统一错误信息，防止用户名枚举
            return APIResponse(code=1, msg='用户名或密码错误')

        # 检查账号状态
        if user.status == '1':
            return APIResponse(code=1, msg='用户名或密码错误')

        # 检查用户角色
        if user.role == '2':
            return APIResponse(code=1, msg='用户名或密码错误')

        # 验证密码
        if user.password != utils.md5value(password):
            return APIResponse(code=1, msg='用户名或密码错误')

        # 生成新的token和过期时间
        ts = utils.get_timestamp()
        data = {
            'admin_token': utils.md5value(username + str(ts)),  # 使用单一时间戳确保一致性
            'exp': ts + (24 * 60 * 60 * 1000)  # 24小时过期
        }

        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(code=0, msg='登录成功', data=serializer.data)
        else:
            return APIResponse(code=1, msg='登录失败')

    except Exception as e:
        return APIResponse(code=1, msg='登录失败')


@api_view(['GET'])
@authentication_classes([AdminTokenAuthtication])
def list_api(request):
    if request.method == 'GET':
        keyword = request.GET.get("keyword", '')
        users = User.objects.filter(username__contains=keyword).order_by('-create_time')
        serializer = NormalUserSerializer(users, many=True)
        return APIResponse(code=0, msg='查询成功', data=serializer.data)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
@after_call(clear_cache)
def create(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return APIResponse(code=1, msg='用户名或密码不能为空')

        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return APIResponse(code=1, msg='该用户名已存在')

        # 密码强度验证
        if len(password) < 6:
            return APIResponse(code=1, msg='密码长度不能少于6位')

        # 准备用户数据
        data = request.data.copy()
        data['password'] = utils.md5value(password)
        # 设置默认值
        data.setdefault('role', '1')  # 默认为管理员
        data.setdefault('status', '0')  # 默认为启用

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            # 生成初始token和过期时间
            ts = utils.get_timestamp()
            user.admin_token = utils.md5value(username + str(ts))
            user.exp = ts + (24 * 60 * 60 * 1000)
            user.save()
            return APIResponse(code=0, msg='创建成功', data=UserSerializer(user).data)
        else:
            return APIResponse(code=1, msg='创建失败: ' + str(serializer.errors))

    except Exception as e:
        return APIResponse(code=1, msg='创建失败: ' + str(e))


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
@after_call(clear_cache)
def update(request):
    try:
        pk = request.data['id']
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return APIResponse(code=1, msg='对象不存在')

    data = request.data.copy()
    if 'username' in data.keys():
        del data['username']
    if 'password' in data.keys():
        del data['password']
    serializer = UserSerializer(user, data=data)
    print(serializer.is_valid())
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='更新成功', data=serializer.data)
    else:
        print(serializer.errors)
    return APIResponse(code=1, msg='更新失败')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
@after_call(clear_cache)
def updatePwd(request):
    try:
        pk = request.data.get('id')
        if not pk:
            return APIResponse(code=1, msg='用户ID不能为空')

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return APIResponse(code=1, msg='用户不存在')

        password = request.data.get('password')
        newPassword1 = request.data.get('newPassword1')
        newPassword2 = request.data.get('newPassword2')

        if not password or not newPassword1 or not newPassword2:
            return APIResponse(code=1, msg='所有字段不能为空')

        # 验证原密码
        if user.password != utils.md5value(password):
            return APIResponse(code=1, msg='原密码不正确')

        # 验证两次新密码是否一致
        if newPassword1 != newPassword2:
            return APIResponse(code=1, msg='两次密码不一致')

        # 密码强度验证
        if len(newPassword1) < 6:
            return APIResponse(code=1, msg='新密码长度不能少于6位')

        # 更新密码
        user.password = utils.md5value(newPassword1)
        # 重置token和过期时间
        ts = utils.get_timestamp()
        user.admin_token = utils.md5value(user.username + str(ts))
        user.exp = ts + (24 * 60 * 60 * 1000)
        user.save()

        return APIResponse(code=0, msg='密码更新成功', data=UserSerializer(user).data)

    except Exception as e:
        return APIResponse(code=1, msg='密码更新失败: ' + str(e))


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
@after_call(clear_cache)
def delete(request):
    try:
        user_id = request.data.get('id')
        if not user_id:
            return APIResponse(code=1, msg='用户ID不能为空')

        # 检查用户是否存在
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return APIResponse(code=1, msg='用户不存在')

        # 防止删除最后一个管理员
        admin_count = User.objects.filter(role='1').count()
        if admin_count <= 1 and user.role == '1':
            return APIResponse(code=1, msg='不能删除最后一个管理员账号')

        # 执行删除
        user.delete()
        return APIResponse(code=0, msg='删除成功')

    except Exception as e:
        return APIResponse(code=1, msg='删除失败: ' + str(e))
