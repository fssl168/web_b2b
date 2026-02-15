import datetime
import hashlib
import smtplib
import time
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from smtplib import SMTP_SSL

from django.core.cache import cache

from myapp.serializers import ErrorLogSerializer


def get_timestamp():
    return int(round(time.time() * 1000))


def md5value(key, salt="987654321hello"):
    # 使用sha256算法
    hash_result = hashlib.sha256((key + salt).encode("utf-8")).hexdigest()
    return hash_result.lower()[:32]


def dict_fetchall(cursor):  # cursor是执行sql_str后的记录，作入参
    columns = [col[0] for col in cursor.description]  # 得到域的名字col[0]，组成List
    return [
        dict(zip(columns, row)) for row in cursor.fetchall()
    ]


def get_ip(request):
    """
    获取请求者的IP信息
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_ua(request):
    """
    获取请求者的IP信息
    """
    ua = request.META.get('HTTP_USER_AGENT')
    return ua[0:200]


def getWeekDays():
    """
    获取近一周的日期
    """
    week_days = []
    now = datetime.datetime.now()
    for i in range(7):
        day = now - datetime.timedelta(days=i)
        week_days.append(day.strftime('%Y-%m-%d %H:%M:%S.%f')[:10])
    week_days.reverse()  # 逆序
    return week_days


def get_monday():
    """
    获取本周周一日期
    """
    now = datetime.datetime.now()
    monday = now - datetime.timedelta(now.weekday())
    return monday.strftime('%Y-%m-%d %H:%M:%S.%f')[:10]


def log_error(request, content):
    """
    记录错误日志
    """
    ip = get_ip(request)
    method = request.method
    url = request.path

    data = {
        'ip': ip,
        'method': method,
        'url': url,
        'content': content
    }

    # 入库
    serializer = ErrorLogSerializer(data=data)
    if serializer.is_valid():
        serializer.save()


def clear_cache(request, response):
    try:
        # 清除所有缓存
        cache.clear()
        print("缓存清空----success")
        return True
    except Exception as e:
        # 记录异常信息
        error_message = f"清除缓存时发生错误: {str(e)}"
        return False, error_message


def after_call(*after_funcs):
    """
    用作装饰器，在视图执行后依次执行所有 after_func(request, response)
    after_call(func1, func2, ...)
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            for func in after_funcs:
                try:
                    func(request, response)
                except Exception as e:
                    print(f'after_func [{func.__name__}] 执行异常：', e)
            return response

        return _wrapped_view

    return decorator


def send_email(
        subject,
        receivers,
        content,
        smtp_server='smtp.qq.com',
        port=465,
        sender_email='285126081@qq.com',
        sender_pass='your_password_or_app_code'
):
    """
    发送邮件的通用方法
    subject: 邮件主题
    receivers: 收件人邮箱（字符串或字符串列表）
    content: 邮件正文（支持html）
    smtp_server: SMTP服务器地址（如smtp.qq.com, smtp.163.com, smtp.gmail.com）
    port: SMTP端口（SSL一般用465）
    sender_email: 发件人邮箱账号
    sender_pass: 邮箱授权码或密码
    """
    if isinstance(receivers, str):
        receivers = [receivers]

    print('send email to =>', ', '.join(receivers))

    msg = MIMEMultipart()
    msg["Subject"] = Header(subject, 'utf-8')
    msg["From"] = sender_email
    msg["To"] = ', '.join(receivers)
    msg.attach(MIMEText(content, 'html', 'utf-8'))

    try:
        smtp = SMTP_SSL(smtp_server, port)
        smtp.set_debuglevel(0)
        smtp.ehlo(smtp_server)
        smtp.login(sender_email, sender_pass)
        smtp.sendmail(sender_email, receivers, msg.as_string())
        smtp.quit()
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print("邮件发送失败, 错误信息:", e)


def generate_secure_token(username, secret_key=None):
    """
    生成安全的token
    """
    from django.conf import settings
    import secrets
    
    secret = secret_key or settings.SECRET_KEY
    timestamp = get_timestamp()
    random_string = secrets.token_hex(32)
    
    data = f"{username}:{timestamp}:{random_string}:{secret}"
    return hashlib.sha256(data.encode('utf-8')).hexdigest()
