import logging
import datetime
from django.db.models import Q
from myapp.models import User, ErrorLog, OpLog
from myapp.utils import send_email

logger = logging.getLogger('myapp')


class SecurityIncidentResponse:
    """
    安全事件响应类
    用于处理安全事件的检测、报告、响应和恢复
    """
    
    # 安全事件类型
    INCIDENT_TYPES = {
        'LOGIN_FAILURE': '登录失败',
        'LOGIN_SUCCESS': '登录成功',
        'PERMISSION_DENIED': '权限拒绝',
        'SQL_INJECTION_ATTEMPT': 'SQL注入尝试',
        'XSS_ATTEMPT': 'XSS攻击尝试',
        'CSRF_ATTEMPT': 'CSRF攻击尝试',
        'FILE_UPLOAD_VIOLATION': '文件上传违规',
        'BRUTE_FORCE_ATTEMPT': '暴力破解尝试',
        'UNAUTHORIZED_ACCESS': '未授权访问',
        'SUSPICIOUS_ACTIVITY': '可疑活动'
    }
    
    # 安全事件级别
    INCIDENT_LEVELS = {
        'LOW': '低',
        'MEDIUM': '中',
        'HIGH': '高',
        'CRITICAL': '严重'
    }
    
    @classmethod
    def detect_incident(cls, incident_type, level, description, user=None, ip=None):
        """
        检测安全事件
        
        Args:
            incident_type: 事件类型
            level: 事件级别
            description: 事件描述
            user: 用户对象
            ip: 客户端IP
        
        Returns:
            bool: 是否成功检测
        """
        try:
            # 记录安全事件
            logger.info(f"Security incident detected: {incident_type} - {level} - {description} - User: {user.username if user else 'anonymous'} - IP: {ip}")
            
            # 保存到错误日志
            error_data = {
                'ip': ip,
                'url': description,
                'method': incident_type,
                'content': f"Level: {level} - Description: {description}"
            }
            
            from myapp.serializers import ErrorLogSerializer
            serializer = ErrorLogSerializer(data=error_data)
            if serializer.is_valid():
                serializer.save()
            
            # 对于高风险事件，发送邮件通知
            if level in ['HIGH', 'CRITICAL']:
                cls.notify_security_team(incident_type, level, description, user, ip)
            
            return True
        except Exception as e:
            logger.error(f"Error detecting security incident: {str(e)}")
            return False
    
    @classmethod
    def respond_to_incident(cls, incident_type, level, description, user=None, ip=None):
        """
        响应安全事件
        
        Args:
            incident_type: 事件类型
            level: 事件级别
            description: 事件描述
            user: 用户对象
            ip: 客户端IP
        
        Returns:
            bool: 是否成功响应
        """
        try:
            # 根据事件类型和级别采取不同的响应措施
            if incident_type == 'BRUTE_FORCE_ATTEMPT' and level in ['HIGH', 'CRITICAL']:
                # 处理暴力破解尝试
                cls.handle_brute_force_attempt(user, ip)
            
            elif incident_type == 'UNAUTHORIZED_ACCESS' and level in ['HIGH', 'CRITICAL']:
                # 处理未授权访问
                cls.handle_unauthorized_access(user, ip)
            
            elif incident_type == 'FILE_UPLOAD_VIOLATION' and level in ['HIGH', 'CRITICAL']:
                # 处理文件上传违规
                cls.handle_file_upload_violation(user, ip)
            
            # 记录响应
            logger.info(f"Responded to security incident: {incident_type} - {level} - {description} - User: {user.username if user else 'anonymous'} - IP: {ip}")
            
            return True
        except Exception as e:
            logger.error(f"Error responding to security incident: {str(e)}")
            return False
    
    @classmethod
    def handle_brute_force_attempt(cls, user, ip):
        """
        处理暴力破解尝试
        """
        # 锁定用户账户
        if user:
            user.status = '1'  # 封号
            user.save()
            logger.info(f"Locked user account due to brute force attempt: {user.username}")
    
    @classmethod
    def handle_unauthorized_access(cls, user, ip):
        """
        处理未授权访问
        """
        # 记录IP地址
        logger.info(f"Unauthorized access from IP: {ip}")
    
    @classmethod
    def handle_file_upload_violation(cls, user, ip):
        """
        处理文件上传违规
        """
        # 记录违规行为
        logger.info(f"File upload violation from user: {user.username if user else 'anonymous'} IP: {ip}")
    
    @classmethod
    def notify_security_team(cls, incident_type, level, description, user, ip):
        """
        通知安全团队
        """
        try:
            # 发送邮件通知
            subject = f"[安全警报] {cls.INCIDENT_TYPES.get(incident_type, incident_type)} - {cls.INCIDENT_LEVELS.get(level, level)}"
            content = f"""
            <h2>安全事件通知</h2>
            <p><strong>事件类型:</strong> {cls.INCIDENT_TYPES.get(incident_type, incident_type)}</p>
            <p><strong>事件级别:</strong> {cls.INCIDENT_LEVELS.get(level, level)}</p>
            <p><strong>事件描述:</strong> {description}</p>
            <p><strong>用户:</strong> {user.username if user else 'anonymous'}</p>
            <p><strong>IP地址:</strong> {ip}</p>
            <p><strong>时间:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>请及时处理此安全事件。</p>
            """
            
            # 从环境变量获取安全团队邮箱
            from django.conf import settings
            security_team_emails = getattr(settings, 'SECURITY_TEAM_EMAILS', [])
            
            # 从管理员列表获取邮箱
            admin_emails = []
            try:
                admins = User.objects.filter(role='1')  # 假设role=1是管理员
                for admin in admins:
                    if admin.email:
                        admin_emails.append(admin.email)
            except Exception as e:
                logger.error(f"Error getting admin emails: {str(e)}")
            
            # 合并邮箱列表，去重
            all_emails = list(set(security_team_emails + admin_emails))
            
            if all_emails:
                send_email(
                    subject=subject,
                    receivers=all_emails,
                    content=content,
                    sender_email=getattr(settings, 'SENDER_EMAIL', 'security@example.com'),
                    sender_pass=getattr(settings, 'SENDER_PASS', '')
                )
            
            logger.info(f"Notified security team about incident: {incident_type} - {level} - Emails: {all_emails}")
        except Exception as e:
            logger.error(f"Error notifying security team: {str(e)}")
    
    @classmethod
    def generate_incident_report(cls, start_time, end_time):
        """
        生成安全事件报告
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            dict: 事件报告
        """
        try:
            # 查询错误日志
            error_logs = ErrorLog.objects.filter(log_time__range=(start_time, end_time))
            
            # 统计事件类型
            incident_stats = {}
            for log in error_logs:
                incident_type = log.method
                if incident_type not in incident_stats:
                    incident_stats[incident_type] = 0
                incident_stats[incident_type] += 1
            
            # 生成报告
            report = {
                'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_incidents': error_logs.count(),
                'incident_stats': incident_stats,
                'details': [{
                    'time': log.log_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'ip': log.ip,
                    'url': log.url,
                    'method': log.method,
                    'content': log.content
                } for log in error_logs]
            }
            
            return report
        except Exception as e:
            logger.error(f"Error generating incident report: {str(e)}")
            return {}
    
    @classmethod
    def run_security_drill(cls):
        """
        运行安全演练
        """
        try:
            # 模拟安全事件
            logger.info("Running security drill...")
            
            # 模拟登录失败事件
            cls.detect_incident(
                'LOGIN_FAILURE',
                'MEDIUM',
                '模拟登录失败事件',
                ip='192.168.1.100'
            )
            
            # 模拟权限拒绝事件
            cls.detect_incident(
                'PERMISSION_DENIED',
                'LOW',
                '模拟权限拒绝事件',
                ip='192.168.1.100'
            )
            
            logger.info("Security drill completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error running security drill: {str(e)}")
            return False


# 安全事件检测装饰器
def security_monitor(incident_type, level):
    """
    安全事件检测装饰器
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            try:
                response = view_func(request, *args, **kwargs)
                
                # 检测成功响应
                if response.status_code == 200:
                    # 记录成功事件
                    SecurityIncidentResponse.detect_incident(
                        incident_type,
                        level,
                        f"Success: {request.method} {request.path}",
                        user=getattr(request, 'user', None),
                        ip=request.META.get('REMOTE_ADDR')
                    )
                else:
                    # 记录失败事件
                    SecurityIncidentResponse.detect_incident(
                        incident_type,
                        'MEDIUM',
                        f"Failed: {request.method} {request.path} - Status: {response.status_code}",
                        user=getattr(request, 'user', None),
                        ip=request.META.get('REMOTE_ADDR')
                    )
                
                return response
            except Exception as e:
                # 记录异常事件
                SecurityIncidentResponse.detect_incident(
                    incident_type,
                    'HIGH',
                    f"Exception: {request.method} {request.path} - {str(e)}",
                    user=getattr(request, 'user', None),
                    ip=request.META.get('REMOTE_ADDR')
                )
                raise
        return wrapped_view
    return decorator