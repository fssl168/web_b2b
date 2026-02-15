"""
双因素认证服务
支持邮箱验证码方式
"""
import random
import string
import time
from datetime import datetime, timedelta
from django.core.cache import cache
from myapp.utils import send_email
import logging

logger = logging.getLogger('myapp')


class TwoFactorAuthService:
    """
    双因素认证服务
    
    支持的认证方式：
    - email: 邮箱验证码
    """
    
    # 验证码配置
    CODE_LENGTH = 6
    CODE_EXPIRE_SECONDS = 300  # 5分钟过期
    MAX_ATTEMPTS = 5  # 最大尝试次数
    ATTEMPT_LOCK_SECONDS = 300  # 锁定时间（秒）
    
    @classmethod
    def generate_code(cls):
        """生成6位数字验证码"""
        return ''.join(random.choices(string.digits, k=cls.CODE_LENGTH))
    
    @classmethod
    def get_cache_key(cls, user_id, method='email'):
        """获取缓存键"""
        return f"2fa_{method}_{user_id}"
    
    @classmethod
    def get_attempt_key(cls, user_id, method='email'):
        """获取尝试次数缓存键"""
        return f"2fa_attempt_{method}_{user_id}"
    
    @classmethod
    def send_email_code(cls, user):
        """
        发送邮箱验证码
        
        Args:
            user: 用户对象
            
        Returns:
            tuple: (success, message)
        """
        if not user.email:
            return False, "用户未设置邮箱地址"
        
        # 检查是否被锁定
        attempt_key = cls.get_attempt_key(user.id, 'email')
        attempts = cache.get(attempt_key, 0)
        if attempts >= cls.MAX_ATTEMPTS:
            return False, "验证码验证次数过多，请5分钟后再试"
        
        # 生成验证码
        code = cls.generate_code()
        
        # 存储验证码到缓存
        cache_key = cls.get_cache_key(user.id, 'email')
        cache.set(cache_key, {
            'code': code,
            'created_at': time.time(),
            'attempts': 0
        }, cls.CODE_EXPIRE_SECONDS)
        
        # 发送邮件
        try:
            subject = "【安全验证】您的登录验证码"
            content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">安全验证</h2>
                <p>尊敬的 <strong>{user.username}</strong>：</p>
                <p>您正在进行双因素认证，验证码如下：</p>
                <div style="background-color: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #1890ff;">{code}</span>
                </div>
                <p style="color: #666;">验证码有效期为 <strong>5分钟</strong>，请尽快完成验证。</p>
                <p style="color: #999; font-size: 12px;">如果这不是您本人的操作，请忽略此邮件。</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #999; font-size: 12px;">此邮件由系统自动发送，请勿回复。</p>
            </div>
            """
            
            send_email(
                subject=subject,
                receivers=[user.email],
                content=content,
                sender_email='',
                sender_pass=''
            )
            
            logger.info(f"2FA code sent to user {user.username} ({user.email})")
            return True, f"验证码已发送至 {user.email[:3]}***{user.email.split('@')[-1]}"
            
        except Exception as e:
            logger.error(f"Failed to send 2FA email: {str(e)}")
            return False, f"发送验证码失败: {str(e)}"
    
    @classmethod
    def verify_code(cls, user, code, method='email'):
        """
        验证验证码
        
        Args:
            user: 用户对象
            code: 用户输入的验证码
            method: 验证方式
            
        Returns:
            tuple: (success, message)
        """
        cache_key = cls.get_cache_key(user.id, method)
        attempt_key = cls.get_attempt_key(user.id, method)
        
        # 检查尝试次数
        attempts = cache.get(attempt_key, 0)
        if attempts >= cls.MAX_ATTEMPTS:
            return False, "验证次数过多，请5分钟后再试"
        
        # 获取存储的验证码
        stored_data = cache.get(cache_key)
        if not stored_data:
            return False, "验证码已过期，请重新获取"
        
        # 验证码匹配
        if stored_data['code'] != code:
            # 增加尝试次数
            cache.set(attempt_key, attempts + 1, cls.ATTEMPT_LOCK_SECONDS)
            remaining = cls.MAX_ATTEMPTS - attempts - 1
            return False, f"验证码错误，剩余尝试次数: {remaining}"
        
        # 验证成功，清除缓存
        cache.delete(cache_key)
        cache.delete(attempt_key)
        
        logger.info(f"2FA verification successful for user {user.username}")
        return True, "验证成功"
    
    @classmethod
    def is_2fa_enabled(cls, user):
        """
        检查用户是否启用了双因素认证
        
        Args:
            user: 用户对象
            
        Returns:
            bool: 是否启用
        """
        return getattr(user, 'two_factor_enabled', False)
    
    @classmethod
    def enable_2fa(cls, user, method='email'):
        """
        启用双因素认证
        
        Args:
            user: 用户对象
            method: 认证方式
            
        Returns:
            bool: 是否成功
        """
        if not user.email:
            return False
        
        user.two_factor_enabled = True
        user.two_factor_method = method
        user.save(update_fields=['two_factor_enabled', 'two_factor_method'])
        
        logger.info(f"2FA enabled for user {user.username}")
        return True
    
    @classmethod
    def disable_2fa(cls, user):
        """
        禁用双因素认证
        
        Args:
            user: 用户对象
        """
        user.two_factor_enabled = False
        user.save(update_fields=['two_factor_enabled'])
        
        logger.info(f"2FA disabled for user {user.username}")
