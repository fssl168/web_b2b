"""
安全相关API接口
包括双因素认证、设备管理、密码策略等
"""
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from django.utils import timezone

from myapp.auth.authentication import AdminTokenAuthtication
from myapp.handler import APIResponse
from myapp.models import User, UserDevice
from myapp.security.two_factor import TwoFactorAuthService
from myapp.security.password_policy import PasswordPolicyService
from myapp.security.device_manager import DeviceManager
from myapp.password_utils import hash_password, verify_password, validate_password_complexity
import logging

logger = logging.getLogger('myapp')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def enable_2fa(request):
    """启用双因素认证"""
    try:
        user = request.user
        method = request.data.get('method', 'email')
        
        if not user.email:
            return APIResponse(code=1, msg='请先设置邮箱地址')
        
        success = TwoFactorAuthService.enable_2fa(user, method)
        if success:
            return APIResponse(code=0, msg='双因素认证已启用')
        return APIResponse(code=1, msg='启用失败')
    except Exception as e:
        logger.error(f"Enable 2FA error: {str(e)}")
        return APIResponse(code=1, msg='操作失败')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def disable_2fa(request):
    """禁用双因素认证"""
    try:
        user = request.user
        TwoFactorAuthService.disable_2fa(user)
        return APIResponse(code=0, msg='双因素认证已禁用')
    except Exception as e:
        logger.error(f"Disable 2FA error: {str(e)}")
        return APIResponse(code=1, msg='操作失败')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def send_2fa_code(request):
    """发送双因素认证验证码"""
    try:
        user = request.user
        success, message = TwoFactorAuthService.send_email_code(user)
        if success:
            return APIResponse(code=0, msg=message)
        return APIResponse(code=1, msg=message)
    except Exception as e:
        logger.error(f"Send 2FA code error: {str(e)}")
        return APIResponse(code=1, msg='发送失败')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def verify_2fa_code(request):
    """验证双因素认证验证码"""
    try:
        user = request.user
        code = request.data.get('code')
        
        if not code:
            return APIResponse(code=1, msg='验证码不能为空')
        
        success, message = TwoFactorAuthService.verify_code(user, code)
        if success:
            return APIResponse(code=0, msg=message)
        return APIResponse(code=1, msg=message)
    except Exception as e:
        logger.error(f"Verify 2FA code error: {str(e)}")
        return APIResponse(code=1, msg='验证失败')


@api_view(['GET'])
@authentication_classes([AdminTokenAuthtication])
def get_2fa_status(request):
    """获取双因素认证状态"""
    try:
        user = request.user
        return APIResponse(code=0, data={
            'enabled': user.two_factor_enabled,
            'method': user.two_factor_method,
            'has_email': bool(user.email)
        })
    except Exception as e:
        logger.error(f"Get 2FA status error: {str(e)}")
        return APIResponse(code=1, msg='获取失败')


@api_view(['GET'])
@authentication_classes([AdminTokenAuthtication])
def get_devices(request):
    """获取用户设备列表"""
    try:
        user = request.user
        devices = DeviceManager.get_user_devices(user)
        
        device_list = []
        for device in devices:
            device_list.append({
                'id': device.id,
                'device_id': device.device_id,
                'device_name': device.device_name,
                'device_type': device.device_type,
                'last_login_time': device.last_login_time.strftime('%Y-%m-%d %H:%M:%S') if device.last_login_time else None,
                'last_login_ip': device.last_login_ip,
                'login_count': device.login_count,
                'is_trusted': device.is_trusted,
                'is_active': device.is_active,
                'is_current': device.device_id == DeviceManager.generate_device_id(request)
            })
        
        return APIResponse(code=0, data=device_list)
    except Exception as e:
        logger.error(f"Get devices error: {str(e)}")
        return APIResponse(code=1, msg='获取失败')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def revoke_device(request):
    """撤销设备（强制下线）"""
    try:
        user = request.user
        device_id = request.data.get('device_id')
        
        if not device_id:
            return APIResponse(code=1, msg='设备ID不能为空')
        
        success = DeviceManager.revoke_device(user, device_id)
        if success:
            return APIResponse(code=0, msg='设备已撤销')
        return APIResponse(code=1, msg='设备不存在')
    except Exception as e:
        logger.error(f"Revoke device error: {str(e)}")
        return APIResponse(code=1, msg='操作失败')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def trust_device(request):
    """设置设备为可信"""
    try:
        user = request.user
        device_id = request.data.get('device_id')
        trust = request.data.get('trust', True)
        
        if not device_id:
            return APIResponse(code=1, msg='设备ID不能为空')
        
        success = DeviceManager.trust_device(user, device_id, trust)
        if success:
            return APIResponse(code=0, msg='设备信任状态已更新')
        return APIResponse(code=1, msg='设备不存在')
    except Exception as e:
        logger.error(f"Trust device error: {str(e)}")
        return APIResponse(code=1, msg='操作失败')


@api_view(['GET'])
@authentication_classes([AdminTokenAuthtication])
def get_password_policy(request):
    """获取密码策略信息"""
    try:
        user = request.user
        policy_info = PasswordPolicyService.get_password_policy_info(user)
        return APIResponse(code=0, data=policy_info)
    except Exception as e:
        logger.error(f"Get password policy error: {str(e)}")
        return APIResponse(code=1, msg='获取失败')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def change_password(request):
    """修改密码（带策略验证）"""
    try:
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not old_password or not new_password or not confirm_password:
            return APIResponse(code=1, msg='所有字段不能为空')
        
        if new_password != confirm_password:
            return APIResponse(code=1, msg='两次密码不一致')
        
        if not verify_password(old_password, user.password):
            return APIResponse(code=1, msg='原密码错误')
        
        is_valid, error_msg = validate_password_complexity(new_password)
        if not is_valid:
            return APIResponse(code=1, msg=error_msg)
        
        if PasswordPolicyService.is_password_reused(user, new_password):
            return APIResponse(code=1, msg='不能使用最近5次使用过的密码')
        
        PasswordPolicyService.add_password_to_history(user, user.password)
        
        user.password = hash_password(new_password)
        PasswordPolicyService.update_password_changed_time(user)
        
        return APIResponse(code=0, msg='密码修改成功')
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return APIResponse(code=1, msg='修改失败')


@api_view(['GET'])
@authentication_classes([AdminTokenAuthtication])
def get_security_overview(request):
    """获取安全概览"""
    try:
        user = request.user
        
        password_info = PasswordPolicyService.get_password_policy_info(user)
        
        devices = DeviceManager.get_user_devices(user)
        active_devices = devices.filter(is_active=True).count()
        trusted_devices = devices.filter(is_trusted=True).count()
        
        return APIResponse(code=0, data={
            'two_factor': {
                'enabled': user.two_factor_enabled,
                'method': user.two_factor_method,
                'has_email': bool(user.email)
            },
            'password': password_info,
            'devices': {
                'total': devices.count(),
                'active': active_devices,
                'trusted': trusted_devices
            }
        })
    except Exception as e:
        logger.error(f"Get security overview error: {str(e)}")
        return APIResponse(code=1, msg='获取失败')
