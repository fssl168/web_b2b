"""
敏感数据加密存储服务
使用AES-256加密算法保护敏感数据
"""
import base64
import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from django.conf import settings
import logging

logger = logging.getLogger('myapp')


class SensitiveDataEncryption:
    """
    敏感数据加密服务
    
    使用AES-256-GCM加密算法
    """
    
    KEY_LENGTH = 32
    IV_LENGTH = 12
    TAG_LENGTH = 16
    
    @classmethod
    def _get_encryption_key(cls):
        """
        获取加密密钥
        
        从Django SECRET_KEY派生，确保密钥稳定性
        """
        secret_key = getattr(settings, 'SECRET_KEY', 'default-secret-key-for-encryption')
        key = hashlib.sha256(secret_key.encode()).digest()
        return key
    
    @classmethod
    def encrypt(cls, plaintext):
        """
        加密敏感数据
        
        Args:
            plaintext: 明文字符串
            
        Returns:
            str: Base64编码的加密数据（IV + 密文 + Tag）
        """
        if not plaintext:
            return plaintext
        
        try:
            key = cls._get_encryption_key()
            iv = os.urandom(cls.IV_LENGTH)
            
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            plaintext_bytes = plaintext.encode('utf-8')
            ciphertext = encryptor.update(plaintext_bytes) + encryptor.finalize()
            
            encrypted_data = iv + encryptor.tag + ciphertext
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise ValueError(f"加密失败: {str(e)}")
    
    @classmethod
    def decrypt(cls, encrypted_text):
        """
        解密敏感数据
        
        Args:
            encrypted_text: Base64编码的加密数据
            
        Returns:
            str: 明文字符串
        """
        if not encrypted_text:
            return encrypted_text
        
        try:
            key = cls._get_encryption_key()
            encrypted_data = base64.b64decode(encrypted_text.encode('utf-8'))
            
            iv = encrypted_data[:cls.IV_LENGTH]
            tag = encrypted_data[cls.IV_LENGTH:cls.IV_LENGTH + cls.TAG_LENGTH]
            ciphertext = encrypted_data[cls.IV_LENGTH + cls.TAG_LENGTH:]
            
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise ValueError(f"解密失败: {str(e)}")
    
    @classmethod
    def is_encrypted(cls, value):
        """
        检查值是否已加密
        
        Args:
            value: 要检查的值
            
        Returns:
            bool: 是否已加密
        """
        if not value:
            return False
        
        try:
            decoded = base64.b64decode(value.encode('utf-8'))
            return len(decoded) > cls.IV_LENGTH + cls.TAG_LENGTH
        except Exception:
            return False
    
    @classmethod
    def encrypt_if_needed(cls, value):
        """
        如果值未加密则加密
        
        Args:
            value: 要处理的值
            
        Returns:
            str: 加密后的值
        """
        if not value or cls.is_encrypted(value):
            return value
        return cls.encrypt(value)
    
    @classmethod
    def decrypt_if_needed(cls, value):
        """
        如果值已加密则解密
        
        Args:
            value: 要处理的值
            
        Returns:
            str: 解密后的值
        """
        if not value:
            return value
        
        if cls.is_encrypted(value):
            return cls.decrypt(value)
        return value


class EncryptedField:
    """
    加密字段描述符
    
    用于模型字段的自动加密/解密
    """
    
    def __init__(self, field_name):
        self.field_name = field_name
        self._encrypted_name = f"_encrypted_{field_name}"
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        encrypted_value = getattr(instance, self._encrypted_name, None)
        if encrypted_value:
            return SensitiveDataEncryption.decrypt(encrypted_value)
        return getattr(instance, self.field_name, None)
    
    def __set__(self, instance, value):
        if value:
            encrypted_value = SensitiveDataEncryption.encrypt(value)
            setattr(instance, self._encrypted_name, encrypted_value)
        else:
            setattr(instance, self._encrypted_name, None)


def mask_email(email):
    """
    遮蔽邮箱地址
    
    Args:
        email: 邮箱地址
        
    Returns:
        str: 遮蔽后的邮箱
    """
    if not email or '@' not in email:
        return email
    
    parts = email.split('@')
    username = parts[0]
    domain = parts[1]
    
    if len(username) <= 2:
        masked_username = username[0] + '***'
    else:
        masked_username = username[:2] + '***'
    
    return f"{masked_username}@{domain}"


def mask_phone(phone):
    """
    遮蔽手机号
    
    Args:
        phone: 手机号
        
    Returns:
        str: 遮蔽后的手机号
    """
    if not phone or len(phone) < 7:
        return phone
    
    return phone[:3] + '****' + phone[-4:]


def mask_id_card(id_card):
    """
    遮蔽身份证号
    
    Args:
        id_card: 身份证号
        
    Returns:
        str: 遮蔽后的身份证号
    """
    if not id_card or len(id_card) < 8:
        return id_card
    
    return id_card[:4] + '**********' + id_card[-4:]
