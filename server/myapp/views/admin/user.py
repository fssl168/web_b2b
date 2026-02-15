# Create your views here.
import datetime
from datetime import timedelta

from rest_framework.decorators import api_view, authentication_classes, throttle_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from django.core.cache import cache
from django.utils import timezone

from myapp import utils
from myapp.auth.authentication import AdminTokenAuthtication
from myapp.handler import APIResponse
from myapp.models import User
from myapp.permission.permission import isDemoAdminUser, check_if_demo
from myapp.serializers import UserSerializer, NormalUserSerializer
from myapp.utils import md5value, after_call, clear_cache
from myapp.password_utils import hash_password, verify_password, is_bcrypt_hash, validate_password_complexity
from myapp.security.two_factor import TwoFactorAuthService
from myapp.security.password_policy import PasswordPolicyService
from myapp.security.device_manager import DeviceManager
import logging

logger = logging.getLogger('myapp')


class UserRateThrottle(AnonRateThrottle):
    # 限流 每小时50次
    THROTTLE_RATES = {"anon": "50/h"}


@api_view(['POST'])
@throttle_classes([UserRateThrottle])
@permission_classes([AllowAny])
def admin_login(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        captcha_code = request.data.get('captcha_code')  # 验证码
        captcha_key = request.data.get('captcha_key')  # 验证码key

        print(f"Login attempt - Username: {username}, Captcha: {captcha_code}, Key: {captcha_key}")

        # 验证必填字段
        if not username or not password:
            print("Missing username or password")
            return APIResponse(code=1, msg='用户名或密码不能为空')

        # 验证验证码
        if not captcha_code or not captcha_key:
            print("Missing captcha")
            return APIResponse(code=1, msg='验证码不能为空')

        # 从缓存中获取正确的验证码
        stored_captcha = cache.get(captcha_key)
        print(f"Stored captcha: {stored_captcha}, Input captcha: {captcha_code}")

        # 验证码不存在或已过期
        if not stored_captcha:
            print("Captcha expired")
            return APIResponse(code=1, msg='验证码已过期，请刷新后重试')

        # 验证码不匹配（不区分大小写）
        if captcha_code.upper() != stored_captcha.upper():
            # 清除错误的验证码缓存，防止暴力破解
            cache.delete(captcha_key)
            print("Captcha mismatch")
            return APIResponse(code=1, msg='验证码错误')

        # 验证通过，清除验证码缓存
        cache.delete(captcha_key)

        try:
            user = User.objects.get(username=username)
            print(f"User found: {user.username}, Role: {user.role}, Status: {user.status}")
        except User.DoesNotExist:
            # 统一错误信息，防止用户名枚举
            print("User not found")
            return APIResponse(code=1, msg='用户名或密码错误')

        # 检查账号状态
        if user.status == '1':
            print("Account disabled")
            return APIResponse(code=1, msg='账号已被禁用')

        # 检查用户角色
        if user.role == '2':
            print("Not admin role")
            return APIResponse(code=1, msg='用户名或密码错误')

        # 检查账户是否被锁定
        if user.lock_time:
            # 检查锁定是否过期
            if user.lock_time > timezone.now():
                remaining_time = (user.lock_time - timezone.now()).total_seconds()
                minutes = int(remaining_time / 60) + 1
                print(f"Account locked for {minutes} minutes")
                return APIResponse(code=1, msg=f'账户已被锁定，请在{minutes}分钟后重试')
            else:
                # 锁定已过期，重置登录失败次数
                user.login_attempts = 0
                user.lock_time = None
                user.save()

        # 验证密码
        print(f"Verifying password for user: {username}")
        if not verify_password(password, user.password):
            # 登录失败，增加失败次数
            user.login_attempts = (user.login_attempts or 0) + 1

            # 如果失败次数达到5次，锁定账户30分钟
            if user.login_attempts >= 5:
                user.lock_time = timezone.now() + timedelta(minutes=30)
                user.save()
                print("Account locked due to too many attempts")
                return APIResponse(code=1, msg='登录失败次数过多，账户已被锁定30分钟')

            user.save()

            # 返回剩余尝试次数
            remaining_attempts = 5 - user.login_attempts
            print(f"Password incorrect, remaining attempts: {remaining_attempts}")
            return APIResponse(code=1, msg=f'用户名或密码错误，剩余尝试次数：{remaining_attempts}')

        print("Login successful")

        is_password_expired, days_remaining = PasswordPolicyService.is_password_expired(user)
        if is_password_expired:
            logger.info(f"Password expired for user: {username}")
            return APIResponse(code=2, msg='密码已过期，请修改密码', data={'user_id': user.id, 'require_password_change': True})

        should_warn, warn_days = PasswordPolicyService.should_warn_expiry(user)
        if should_warn and not is_password_expired:
            logger.info(f"Password expiring soon for user: {username}, days remaining: {warn_days}")

        if TwoFactorAuthService.is_2fa_enabled(user):
            temp_token = f"2fa_pending_{user.id}_{utils.get_timestamp()}"
            cache.set(temp_token, user.id, 300)
            
            success, message = TwoFactorAuthService.send_email_code(user)
            if not success:
                logger.error(f"Failed to send 2FA code: {message}")
                return APIResponse(code=1, msg=message)
            
            logger.info(f"2FA required for user: {username}")
            return APIResponse(code=3, msg='需要双因素认证', data={
                'require_2fa': True,
                'temp_token': temp_token,
                'email_masked': f"{user.email[:3]}***{user.email.split('@')[-1]}" if user.email else None
            })

        suspicious_check = DeviceManager.check_suspicious_login(user, request)
        if suspicious_check['is_suspicious']:
            logger.warning(f"Suspicious login detected for user {username}: {suspicious_check['reasons']}")

        DeviceManager.register_device(user, request)

        user.login_attempts = 0
        user.lock_time = None
        user.last_login_time = timezone.now()
        user.last_login_ip = utils.get_ip(request)

        if not is_bcrypt_hash(user.password):
            user.password = hash_password(password)

        ts = utils.get_timestamp()
        data = {
            'admin_token': utils.generate_secure_token(username),
            'exp': ts + (24 * 60 * 60 * 1000)
        }

        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            response_data = serializer.data
            if should_warn and not is_password_expired:
                response_data['password_warning'] = {
                    'show_warning': True,
                    'days_remaining': warn_days,
                    'message': f'您的密码将在{warn_days}天后过期，请及时修改'
                }
            
            logger.info(f"Login successful for user: {username}")
            return APIResponse(code=0, msg='登录成功', data=response_data)
        else:
            print(f"Serializer errors: {serializer.errors}")
            return APIResponse(code=1, msg='登录失败')

    except Exception as e:
        print(f"登录异常: {e}")
        return APIResponse(code=1, msg='登录失败')


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_2fa_login(request):
    """验证双因素认证并完成登录"""
    try:
        temp_token = request.data.get('temp_token')
        code = request.data.get('code')
        
        if not temp_token or not code:
            return APIResponse(code=1, msg='参数不完整')
        
        user_id = cache.get(temp_token)
        if not user_id:
            return APIResponse(code=1, msg='验证已过期，请重新登录')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return APIResponse(code=1, msg='用户不存在')
        
        success, message = TwoFactorAuthService.verify_code(user, code)
        if not success:
            return APIResponse(code=1, msg=message)
        
        cache.delete(temp_token)
        
        DeviceManager.register_device(user, request)
        
        user.login_attempts = 0
        user.lock_time = None
        user.last_login_time = timezone.now()
        user.last_login_ip = utils.get_ip(request)
        
        ts = utils.get_timestamp()
        data = {
            'admin_token': utils.generate_secure_token(user.username),
            'exp': ts + (24 * 60 * 60 * 1000)
        }
        
        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"2FA login successful for user: {user.username}")
            return APIResponse(code=0, msg='登录成功', data=serializer.data)
        return APIResponse(code=1, msg='登录失败')
        
    except Exception as e:
        logger.error(f"2FA verification error: {str(e)}")
        return APIResponse(code=1, msg='验证失败')


@api_view(['POST'])
@permission_classes([AllowAny])
def force_change_password(request):
    """强制修改过期密码"""
    try:
        user_id = request.data.get('user_id')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not user_id or not new_password or not confirm_password:
            return APIResponse(code=1, msg='参数不完整')
        
        if new_password != confirm_password:
            return APIResponse(code=1, msg='两次密码不一致')
        
        is_valid, error_msg = validate_password_complexity(new_password)
        if not is_valid:
            return APIResponse(code=1, msg=error_msg)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return APIResponse(code=1, msg='用户不存在')
        
        if PasswordPolicyService.is_password_reused(user, new_password):
            return APIResponse(code=1, msg='不能使用最近5次使用过的密码')
        
        PasswordPolicyService.add_password_to_history(user, user.password)
        
        user.password = hash_password(new_password)
        PasswordPolicyService.update_password_changed_time(user)
        
        ts = utils.get_timestamp()
        user.admin_token = utils.generate_secure_token(user.username)
        user.exp = ts + (24 * 60 * 60 * 1000)
        user.save()
        
        logger.info(f"Password force changed for user: {user.username}")
        return APIResponse(code=0, msg='密码修改成功', data=UserSerializer(user).data)
        
    except Exception as e:
        logger.error(f"Force change password error: {str(e)}")
        return APIResponse(code=1, msg='修改失败')


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

        is_valid, error_msg = validate_password_complexity(password)
        if not is_valid:
            return APIResponse(code=1, msg=error_msg)

        data = request.data.copy()
        data['password'] = hash_password(password)
        data['password_hash_type'] = 'bcrypt'
        data.setdefault('role', '1')
        data.setdefault('status', '0')

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            # 生成初始token和过期时间
            ts = utils.get_timestamp()
            user.admin_token = utils.generate_secure_token(username)
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
        # 同时支持 FormData 和 JSON 格式的请求
        pk = request.data.get('id') or request.POST.get('id')
        if not pk:
            return APIResponse(code=1, msg='用户ID不能为空')
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return APIResponse(code=1, msg='对象不存在')

    # 同时支持 FormData 和 JSON 格式的请求
    data = {}
    # 优先使用 request.data（JSON格式），如果没有则使用 request.POST（FormData格式）
    if hasattr(request, 'data') and request.data:
        data.update(request.data)
    elif hasattr(request, 'POST') and request.POST:
        data.update(request.POST.dict())
    
    # 处理用户名更新
    if 'username' in data:
        # 检查用户名是否已存在（排除当前用户）
        if User.objects.filter(username=data['username']).exclude(id=pk).exists():
            return APIResponse(code=1, msg='该用户名已存在')
    
    # 处理密码更新
    if 'password' in data and data['password']:
        # 验证密码复杂度
        is_valid, error_msg = validate_password_complexity(data['password'])
        if not is_valid:
            return APIResponse(code=1, msg=error_msg)
        # 哈希密码
        data['password'] = hash_password(data['password'])
        data['password_hash_type'] = 'bcrypt'
        # 更新密码修改时间
        PasswordPolicyService.update_password_changed_time(user)
    elif 'password' in data and not data['password']:
        # 密码为空，不更新
        del data['password']
    
    serializer = UserSerializer(user, data=data)
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='更新成功', data=serializer.data)
    else:
        print(serializer.errors)
        return APIResponse(code=1, msg='更新失败: ' + str(serializer.errors))


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

        if not verify_password(password, user.password):
            return APIResponse(code=1, msg='原密码不正确')

        if newPassword1 != newPassword2:
            return APIResponse(code=1, msg='两次密码不一致')

        is_valid, error_msg = validate_password_complexity(newPassword1)
        if not is_valid:
            return APIResponse(code=1, msg=error_msg)

        if PasswordPolicyService.is_password_reused(user, newPassword1):
            return APIResponse(code=1, msg='不能使用最近5次使用过的密码')

        PasswordPolicyService.add_password_to_history(user, user.password)

        user.password = hash_password(newPassword1)
        user.password_hash_type = 'bcrypt'
        PasswordPolicyService.update_password_changed_time(user)
        
        ts = utils.get_timestamp()
        user.admin_token = utils.generate_secure_token(user.username)
        user.exp = ts + (24 * 60 * 60 * 1000)
        user.save()

        logger.info(f"Password updated for user: {user.username}")
        return APIResponse(code=0, msg='密码更新成功', data=UserSerializer(user).data)

    except Exception as e:
        logger.error(f"Password update error: {str(e)}")
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
