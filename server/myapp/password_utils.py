import bcrypt
import hashlib
import re


def validate_password_complexity(password):
    """
    验证密码复杂度
    
    要求：
    - 至少8个字符
    - 至少1个大写字母
    - 至少1个小写字母
    - 至少1个数字
    - 至少1个特殊字符
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, "密码不能为空"
    
    if len(password) < 8:
        return False, "密码长度至少为8个字符"
    
    if len(password) > 128:
        return False, "密码长度不能超过128个字符"
    
    if not re.search(r'[A-Z]', password):
        return False, "密码必须包含至少1个大写字母"
    
    if not re.search(r'[a-z]', password):
        return False, "密码必须包含至少1个小写字母"
    
    if not re.search(r'\d', password):
        return False, "密码必须包含至少1个数字"
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        return False, "密码必须包含至少1个特殊字符（!@#$%^&*等）"
    
    # 检查常见弱密码
    common_passwords = [
        'password', 'Password1!', '12345678', 'qwerty', 'abc123',
        'admin123', 'Admin123!', 'password123', 'Password123!'
    ]
    if password.lower() in [p.lower() for p in common_passwords]:
        return False, "密码过于简单，请使用更复杂的密码"
    
    return True, ""


def hash_password(password, salt="987654321hello"):
    """
    使用 bcrypt 加密密码
    如果密码已经是 bcrypt 哈希格式，直接返回
    否则使用 bcrypt 重新加密
    """
    # 检查是否已经是 bcrypt 哈希（以 $2b$ 开头）
    if password and password.startswith('$2b$'):
        return password

    # 否则使用 bcrypt 加密
    password_bytes = password.encode('utf-8')
    salt_bytes = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt_bytes)
    return hashed.decode('utf-8')


def verify_password(plain_password, hashed_password):
    """
    验证密码

    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码（可能是 bcrypt 或 MD5 格式）

    Returns:
        bool: 密码是否匹配
    """
    try:
        # 如果是 bcrypt 哈希
        if hashed_password and hashed_password.startswith('$2b$'):
            plain_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(plain_bytes, hashed_bytes)

        # 如果是旧的 MD5 哈希，兼容旧用户
        else:
            salt = "987654321hello"
            hash_result = hashlib.sha256((plain_password + salt).encode("utf-8")).hexdigest()
            md5_hash = hash_result.lower()[:32]
            return md5_hash == hashed_password

    except Exception as e:
        print(f"密码验证错误: {e}")
        return False


def is_bcrypt_hash(password_hash):
    """检查密码是否是 bcrypt 哈希格式"""
    return password_hash and password_hash.startswith('$2b$')
