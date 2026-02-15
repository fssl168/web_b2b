"""
登录设备管理服务
"""
import hashlib
import json
from datetime import datetime
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger('myapp')


class DeviceManager:
    """
    设备管理服务
    
    功能：
    - 设备识别
    - 设备注册
    - 设备管理
    - 异常登录检测
    """
    
    # 设备类型检测关键词
    MOBILE_KEYWORDS = ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone']
    TABLET_KEYWORDS = ['tablet', 'ipad', 'playbook', 'silk']
    
    @classmethod
    def generate_device_id(cls, request):
        """
        生成设备唯一标识
        
        基于User-Agent和IP地址生成
        """
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = request.META.get('REMOTE_ADDR', '')
        
        # 使用User-Agent和IP生成设备ID
        device_string = f"{user_agent}_{ip_address}"
        return hashlib.sha256(device_string.encode()).hexdigest()[:32]
    
    @classmethod
    def detect_device_type(cls, user_agent):
        """
        检测设备类型
        
        Args:
            user_agent: User-Agent字符串
            
        Returns:
            str: 设备类型
        """
        if not user_agent:
            return 'unknown'
        
        ua_lower = user_agent.lower()
        
        # 检测平板设备
        for keyword in cls.TABLET_KEYWORDS:
            if keyword in ua_lower:
                return 'tablet'
        
        # 检测移动设备
        for keyword in cls.MOBILE_KEYWORDS:
            if keyword in ua_lower:
                return 'mobile'
        
        return 'desktop'
    
    @classmethod
    def parse_device_name(cls, user_agent):
        """
        解析设备名称
        
        Args:
            user_agent: User-Agent字符串
            
        Returns:
            str: 设备名称
        """
        if not user_agent:
            return '未知设备'
        
        # 简单解析浏览器和操作系统
        ua = user_agent
        
        # 检测浏览器
        browser = '未知浏览器'
        if 'Chrome' in ua and 'Edg' not in ua:
            browser = 'Chrome'
        elif 'Firefox' in ua:
            browser = 'Firefox'
        elif 'Safari' in ua and 'Chrome' not in ua:
            browser = 'Safari'
        elif 'Edg' in ua:
            browser = 'Edge'
        elif 'MSIE' in ua or 'Trident' in ua:
            browser = 'IE'
        
        # 检测操作系统
        os = '未知系统'
        if 'Windows' in ua:
            os = 'Windows'
        elif 'Mac' in ua:
            os = 'Mac'
        elif 'Linux' in ua:
            os = 'Linux'
        elif 'Android' in ua:
            os = 'Android'
        elif 'iPhone' in ua or 'iPad' in ua:
            os = 'iOS'
        
        return f"{os} - {browser}"
    
    @classmethod
    def register_device(cls, user, request):
        """
        注册或更新设备信息

        Args:
            user: 用户对象
            request: 请求对象

        Returns:
            UserDevice: 设备对象
        """
        from myapp.models import UserDevice

        device_id = cls.generate_device_id(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = request.META.get('REMOTE_ADDR', '')

        logger.info(f"Registering device for user {user.username} (ID: {user.id}), device_id: {device_id}")

        # 尝试获取已存在的设备（特定用户的）
        try:
            device = UserDevice.objects.get(user=user, device_id=device_id)
            # 更新设备信息
            device.last_login_time = timezone.now()
            device.last_login_ip = ip_address
            device.login_count += 1
            device.user_agent = user_agent[:500]
            device.save()

            logger.info(f"Device updated: {device.device_name} for user {user.username}")
            return device

        except UserDevice.DoesNotExist:
            # 创建新设备
            device = UserDevice.objects.create(
                user=user,
                device_id=device_id,
                device_name=cls.parse_device_name(user_agent),
                device_type=cls.detect_device_type(user_agent),
                user_agent=user_agent[:500],
                ip_address=ip_address,
                last_login_time=timezone.now(),
                last_login_ip=ip_address,
                login_count=1,
                is_trusted=False
            )

            logger.info(f"New device registered: {device.device_name} for user {user.username}")
            return device
    
    @classmethod
    def get_user_devices(cls, user, active_only=True):
        """
        获取用户的所有设备
        
        Args:
            user: 用户对象
            active_only: 是否只返回活跃设备
            
        Returns:
            QuerySet: 设备列表
        """
        from myapp.models import UserDevice
        
        devices = UserDevice.objects.filter(user=user)
        if active_only:
            devices = devices.filter(is_active=True)
        
        return devices.order_by('-last_login_time')
    
    @classmethod
    def revoke_device(cls, user, device_id):
        """
        撤销设备（强制下线）
        
        Args:
            user: 用户对象
            device_id: 设备ID
            
        Returns:
            bool: 是否成功
        """
        from myapp.models import UserDevice
        
        try:
            device = UserDevice.objects.get(user=user, device_id=device_id)
            device.is_active = False
            device.save()
            
            logger.info(f"Device revoked: {device.device_name} for user {user.username}")
            return True
            
        except UserDevice.DoesNotExist:
            return False
    
    @classmethod
    def trust_device(cls, user, device_id, trust=True):
        """
        设置设备为可信/不可信
        
        Args:
            user: 用户对象
            device_id: 设备ID
            trust: 是否信任
            
        Returns:
            bool: 是否成功
        """
        from myapp.models import UserDevice
        
        try:
            device = UserDevice.objects.get(user=user, device_id=device_id)
            device.is_trusted = trust
            device.save()
            
            logger.info(f"Device trust status changed: {device.device_name} for user {user.username}")
            return True
            
        except UserDevice.DoesNotExist:
            return False
    
    @classmethod
    def check_suspicious_login(cls, user, request):
        """
        检测可疑登录
        
        Args:
            user: 用户对象
            request: 请求对象
            
        Returns:
            dict: 可疑登录检测结果
        """
        from myapp.models import UserDevice
        
        device_id = cls.generate_device_id(request)
        ip_address = request.META.get('REMOTE_ADDR', '')
        
        result = {
            'is_suspicious': False,
            'reasons': []
        }
        
        # 检查是否是新设备
        try:
            device = UserDevice.objects.get(device_id=device_id)
            if not device.is_trusted:
                result['is_suspicious'] = True
                result['reasons'].append('新设备登录')
        except UserDevice.DoesNotExist:
            result['is_suspicious'] = True
            result['reasons'].append('首次登录设备')
        
        # 检查IP地址是否变化
        if user.last_login_ip and user.last_login_ip != ip_address:
            result['is_suspicious'] = True
            result['reasons'].append(f'IP地址变化: {user.last_login_ip} -> {ip_address}')
        
        return result
