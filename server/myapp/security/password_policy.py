"""
密码过期策略服务
实现90天强制修改密码
"""
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger('myapp')


class PasswordPolicyService:
    """
    密码策略服务
    
    功能：
    - 密码过期检查
    - 密码历史记录
    - 密码重用检查
    """
    
    # 密码过期天数（默认90天）
    PASSWORD_EXPIRE_DAYS = getattr(settings, 'PASSWORD_EXPIRE_DAYS', 90)
    
    # 密码历史记录数量（防止重用最近N次密码）
    PASSWORD_HISTORY_COUNT = getattr(settings, 'PASSWORD_HISTORY_COUNT', 5)
    
    # 提前警告天数（过期前N天开始提醒）
    PASSWORD_EXPIRE_WARNING_DAYS = getattr(settings, 'PASSWORD_EXPIRE_WARNING_DAYS', 7)
    
    @classmethod
    def is_password_expired(cls, user):
        """
        检查密码是否过期
        
        Args:
            user: 用户对象
            
        Returns:
            tuple: (is_expired, days_remaining)
        """
        if not user.password_changed_at:
            # 如果没有记录密码修改时间，设置为当前时间
            user.password_changed_at = timezone.now()
            user.save(update_fields=['password_changed_at'])
            return False, cls.PASSWORD_EXPIRE_DAYS
        
        expire_date = user.password_changed_at + timedelta(days=cls.PASSWORD_EXPIRE_DAYS)
        now = timezone.now()
        
        if now >= expire_date:
            return True, 0
        
        days_remaining = (expire_date - now).days
        return False, days_remaining
    
    @classmethod
    def should_warn_expiry(cls, user):
        """
        检查是否应该警告密码即将过期
        
        Args:
            user: 用户对象
            
        Returns:
            tuple: (should_warn, days_remaining)
        """
        is_expired, days_remaining = cls.is_password_expired(user)
        
        if is_expired:
            return True, 0
        
        if days_remaining <= cls.PASSWORD_EXPIRE_WARNING_DAYS:
            return True, days_remaining
        
        return False, days_remaining
    
    @classmethod
    def add_password_to_history(cls, user, password_hash):
        """
        将密码添加到历史记录
        
        Args:
            user: 用户对象
            password_hash: 密码哈希
        """
        from myapp.models import PasswordHistory
        
        # 创建新的密码历史记录
        PasswordHistory.objects.create(
            user=user,
            password_hash=password_hash
        )
        
        # 删除超过限制的旧记录
        old_histories = PasswordHistory.objects.filter(user=user).order_by('-created_at')
        if old_histories.count() > cls.PASSWORD_HISTORY_COUNT:
            for history in old_histories[cls.PASSWORD_HISTORY_COUNT:]:
                history.delete()
    
    @classmethod
    def is_password_reused(cls, user, password):
        """
        检查密码是否在历史记录中使用过
        
        Args:
            user: 用户对象
            password: 明文密码
            
        Returns:
            bool: 是否重用
        """
        from myapp.models import PasswordHistory
        from myapp.password_utils import verify_password
        
        # 获取最近的密码历史记录
        histories = PasswordHistory.objects.filter(user=user).order_by('-created_at')[:cls.PASSWORD_HISTORY_COUNT]
        
        for history in histories:
            if verify_password(password, history.password_hash):
                return True
        
        return False
    
    @classmethod
    def update_password_changed_time(cls, user):
        """
        更新密码修改时间
        
        Args:
            user: 用户对象
        """
        user.password_changed_at = timezone.now()
        user.password_expired = False
        user.save(update_fields=['password_changed_at', 'password_expired'])
    
    @classmethod
    def get_password_policy_info(cls, user):
        """
        获取密码策略信息
        
        Args:
            user: 用户对象
            
        Returns:
            dict: 密码策略信息
        """
        is_expired, days_remaining = cls.is_password_expired(user)
        should_warn, _ = cls.should_warn_expiry(user)
        
        return {
            'is_expired': is_expired,
            'days_remaining': days_remaining,
            'should_warn': should_warn,
            'expire_days': cls.PASSWORD_EXPIRE_DAYS,
            'last_changed': user.password_changed_at.strftime('%Y-%m-%d %H:%M:%S') if user.password_changed_at else None,
            'expire_date': (user.password_changed_at + timedelta(days=cls.PASSWORD_EXPIRE_DAYS)).strftime('%Y-%m-%d') if user.password_changed_at else None,
        }
