from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class User(models.Model):
    STATUS_CHOICES = (
        ('0', '正常'),
        ('1', '封号'),
    )
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=255, null=True)  # 增加长度以支持bcrypt
    password_hash_type = models.CharField(max_length=20, default='bcrypt')  # 密码加密类型
    role = models.CharField(max_length=2, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
    nickname = models.CharField(blank=True, null=True, max_length=20)
    mobile = models.CharField(max_length=13, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=200, null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    admin_token = models.CharField(max_length=32, blank=True, null=True)
    token = models.CharField(max_length=32, blank=True, null=True)
    exp = models.CharField(max_length=32, blank=True, null=True)
    # 登录安全相关字段
    login_attempts = models.IntegerField(default=0)  # 登录失败次数
    lock_time = models.DateTimeField(null=True, blank=True)  # 账户锁定时间
    last_login_time = models.DateTimeField(null=True, blank=True)  # 最后登录时间
    last_login_ip = models.CharField(max_length=50, null=True, blank=True)  # 最后登录IP

    class Meta:
        db_table = "b_user"


class Category(models.Model):
    list_display = ("title", "id")
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    cover = models.CharField(max_length=200, blank=True, null=True)
    pid = models.BigIntegerField(default=-1)
    sort = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "b_category"


class Thing(models.Model):
    STATUS_CHOICES = (
        ('0', '上架'),
        ('1', '下架'),
    )
    id = models.BigAutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True,
                                 related_name='category_thing')
    title = models.CharField(max_length=200, blank=True, null=True)
    summary = models.CharField(max_length=500, blank=True, null=True)
    cover = models.CharField(max_length=1000, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.CharField(max_length=100, blank=True, null=True)
    dimension = models.CharField(max_length=50, blank=True, null=True)  # 维度
    seo_title = models.CharField(max_length=100, blank=True, null=True)
    seo_description = models.CharField(max_length=500, blank=True, null=True)
    seo_keywords = models.CharField(max_length=200, blank=True, null=True)
    properties = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    pv = models.IntegerField(default=0)
    rate = models.IntegerField(default=3)  # 评分

    class Meta:
        db_table = "b_thing"


class News(models.Model):
    STATUS_CHOICES = (
        ('0', '上架'),
        ('1', '下架'),
    )
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    summary = models.CharField(max_length=500, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    cover = models.CharField(max_length=1000, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    seo_title = models.CharField(max_length=100, blank=True, null=True)
    seo_description = models.CharField(max_length=500, blank=True, null=True)
    seo_keywords = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    pv = models.IntegerField(default=0)

    class Meta:
        db_table = "b_news"


class Case(models.Model):
    STATUS_CHOICES = (
        ('0', '上架'),
        ('1', '下架'),
    )
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    client = models.CharField(max_length=100, blank=True, null=True)
    cover = models.CharField(max_length=1000, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    seo_title = models.CharField(max_length=100, blank=True, null=True)
    seo_description = models.CharField(max_length=500, blank=True, null=True)
    seo_keywords = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    pv = models.IntegerField(default=0)

    class Meta:
        db_table = "b_case"


class Faq(models.Model):
    STATUS_CHOICES = (
        ('0', '上架'),
        ('1', '下架'),
    )
    id = models.BigAutoField(primary_key=True)
    question = models.CharField(max_length=200, blank=True, null=True)
    reply = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    pv = models.IntegerField(default=0)

    class Meta:
        db_table = "b_faq"


class Inquiry(models.Model):
    STATUS_CHOICES = (
        ('0', '上架'),
        ('1', '下架'),
    )
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    tel = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=30, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    message = models.CharField(max_length=500, blank=True, null=True)
    ip = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    pv = models.IntegerField(default=0)

    class Meta:
        db_table = "b_inquiry"


class Download(models.Model):
    STATUS_CHOICES = (
        ('0', '上架'),
        ('1', '下架'),
    )
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    summary = models.CharField(max_length=1000, blank=True, null=True)
    raw = models.CharField(max_length=1000, blank=True, null=True)
    link = models.CharField(max_length=1000, blank=True, null=True)  # 外部链接
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    pv = models.IntegerField(default=0)

    class Meta:
        db_table = "b_download"


class BasicSite(models.Model):
    id = models.BigAutoField(primary_key=True)
    status = models.CharField(max_length=2, default='1')  # 网站状态(1开启 2关闭)
    site_name = models.CharField(max_length=100, blank=True, null=True)  # 网站名称
    site_nickname = models.CharField(max_length=100, blank=True, null=True)  # 网站简称
    site_logo = models.CharField(max_length=100, blank=True, null=True)  # 网站logo
    site_ico = models.CharField(max_length=100, blank=True, null=True)  # 网站ico
    site_address = models.CharField(max_length=100, blank=True, null=True)  # 网站网址
    site_copyright = models.CharField(max_length=100, blank=True, null=True)  # 版权信息
    site_code = models.CharField(max_length=1000, blank=True, null=True)  # 第三方代码
    site_gaid = models.CharField(max_length=100, blank=True, null=True)  # 谷歌gaId
    site_switch_product = models.CharField(max_length=2, default='1')  # 功能开关
    site_switch_about = models.CharField(max_length=2, default='1')  # 功能开关
    site_switch_contact = models.CharField(max_length=2, default='1')  # 功能开关
    site_switch_news = models.CharField(max_length=2, default='1')  # 功能开关
    site_switch_case = models.CharField(max_length=2, default='1')  # 功能开关
    site_switch_faq = models.CharField(max_length=2, default='1')  # 功能开关
    site_switch_download = models.CharField(max_length=2, default='1')  # 功能开关

    class Meta:
        db_table = "b_basic_site"

    @classmethod
    def get_solo(cls):
        try:
            return cls.objects.get()
        except ObjectDoesNotExist:
            return None

    def save(self, *args, **kwargs):
        if not self.pk and BasicSite.objects.exists():
            raise ValueError("There can only be one instance.")
        return super().save(*args, **kwargs)


class BasicTdk(models.Model):
    id = models.BigAutoField(primary_key=True)
    tdk_home_title = models.CharField(max_length=100, blank=True, null=True)
    tdk_home_keywords = models.CharField(max_length=200, blank=True, null=True)
    tdk_home_description = models.CharField(max_length=500, blank=True, null=True)
    tdk_product_title = models.CharField(max_length=100, blank=True, null=True)
    tdk_product_keywords = models.CharField(max_length=200, blank=True, null=True)
    tdk_product_description = models.CharField(max_length=500, blank=True, null=True)
    tdk_about_title = models.CharField(max_length=100, blank=True, null=True)
    tdk_about_keywords = models.CharField(max_length=200, blank=True, null=True)
    tdk_about_description = models.CharField(max_length=500, blank=True, null=True)
    tdk_contact_title = models.CharField(max_length=100, blank=True, null=True)
    tdk_contact_keywords = models.CharField(max_length=200, blank=True, null=True)
    tdk_contact_description = models.CharField(max_length=500, blank=True, null=True)
    tdk_news_title = models.CharField(max_length=100, blank=True, null=True)
    tdk_news_keywords = models.CharField(max_length=200, blank=True, null=True)
    tdk_news_description = models.CharField(max_length=500, blank=True, null=True)
    tdk_case_title = models.CharField(max_length=100, blank=True, null=True)
    tdk_case_keywords = models.CharField(max_length=200, blank=True, null=True)
    tdk_case_description = models.CharField(max_length=500, blank=True, null=True)
    tdk_download_title = models.CharField(max_length=100, blank=True, null=True)
    tdk_download_keywords = models.CharField(max_length=200, blank=True, null=True)
    tdk_download_description = models.CharField(max_length=500, blank=True, null=True)
    tdk_faq_title = models.CharField(max_length=100, blank=True, null=True)
    tdk_faq_keywords = models.CharField(max_length=200, blank=True, null=True)
    tdk_faq_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "b_basic_tdk"

    @classmethod
    def get_solo(cls):
        try:
            return cls.objects.get()
        except ObjectDoesNotExist:
            return None

    def save(self, *args, **kwargs):
        if not self.pk and BasicTdk.objects.exists():
            raise ValueError("There can only be one instance.")
        return super().save(*args, **kwargs)


class BasicBanner(models.Model):
    id = models.BigAutoField(primary_key=True)
    banner_home = models.CharField(max_length=300, blank=True, null=True)
    banner_product = models.CharField(max_length=100, blank=True, null=True)
    banner_about = models.CharField(max_length=100, blank=True, null=True)
    banner_contact = models.CharField(max_length=100, blank=True, null=True)
    banner_news = models.CharField(max_length=100, blank=True, null=True)
    banner_case = models.CharField(max_length=100, blank=True, null=True)
    banner_download = models.CharField(max_length=100, blank=True, null=True)
    banner_faq = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "b_basic_banner"

    @classmethod
    def get_solo(cls):
        try:
            return cls.objects.get()
        except ObjectDoesNotExist:
            return None

    def save(self, *args, **kwargs):
        if not self.pk and BasicBanner.objects.exists():
            raise ValueError("There can only be one instance.")
        return super().save(*args, **kwargs)


class BasicGlobal(models.Model):
    id = models.BigAutoField(primary_key=True)
    global_phone = models.CharField(max_length=100, blank=True, null=True)
    global_email = models.CharField(max_length=100, blank=True, null=True)
    global_company_name = models.CharField(max_length=100, blank=True, null=True)
    global_address = models.CharField(max_length=100, blank=True, null=True)
    global_wechat = models.CharField(max_length=100, blank=True, null=True)
    global_wechat_qrcode = models.CharField(max_length=200, blank=True, null=True)
    global_facebook = models.CharField(max_length=100, blank=True, null=True)
    global_twitter = models.CharField(max_length=100, blank=True, null=True)
    global_linkedin = models.CharField(max_length=100, blank=True, null=True)
    global_whatsapp = models.CharField(max_length=100, blank=True, null=True)
    global_youtube = models.CharField(max_length=100, blank=True, null=True)
    global_instagram = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "b_basic_global"

    @classmethod
    def get_solo(cls):
        try:
            return cls.objects.get()
        except ObjectDoesNotExist:
            return None

    def save(self, *args, **kwargs):
        if not self.pk and BasicGlobal.objects.exists():
            raise ValueError("There can only be one instance.")
        return super().save(*args, **kwargs)


class BasicAdditional(models.Model):
    id = models.BigAutoField(primary_key=True)
    additional_mission = models.CharField(max_length=1000, blank=True, null=True)
    additional_about = models.CharField(max_length=1000, blank=True, null=True)
    global_addition_about_image = models.CharField(max_length=100, blank=True, null=True)  # 关于图片
    global_addition_mission_image = models.CharField(max_length=100, blank=True, null=True)  # 使命图片
    global_addition_company_image = models.CharField(max_length=300, blank=True, null=True)  # 工厂图片
    global_addition_contact_image = models.CharField(max_length=100, blank=True, null=True)  # contact底图
    param_one_name = models.CharField(max_length=100, blank=True, null=True)
    param_one_value = models.CharField(max_length=100, blank=True, null=True)
    param_two_name = models.CharField(max_length=100, blank=True, null=True)
    param_two_value = models.CharField(max_length=100, blank=True, null=True)
    param_three_name = models.CharField(max_length=100, blank=True, null=True)
    param_three_value = models.CharField(max_length=100, blank=True, null=True)
    param_four_name = models.CharField(max_length=100, blank=True, null=True)
    param_four_value = models.CharField(max_length=100, blank=True, null=True)
    ext01 = models.CharField(max_length=100, blank=True, null=True)  # 扩展字段 (hero文案)
    ext02 = models.CharField(max_length=500, blank=True, null=True)  # 扩展字段 (资质图片)
    ext03 = models.CharField(max_length=300, blank=True, null=True)
    ext04 = models.CharField(max_length=300, blank=True, null=True)
    ext05 = models.CharField(max_length=800, blank=True, null=True)
    ext06 = models.CharField(max_length=800, blank=True, null=True)

    class Meta:
        db_table = "b_basic_additional"

    @classmethod
    def get_solo(cls):
        try:
            return cls.objects.get()
        except ObjectDoesNotExist:
            return None

    def save(self, *args, **kwargs):
        if not self.pk and BasicAdditional.objects.exists():
            raise ValueError("There can only be one instance.")
        return super().save(*args, **kwargs)


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    comment_cover = models.CharField(max_length=100, blank=True, null=True)
    comment_name = models.CharField(max_length=100, blank=True, null=True)
    comment_location = models.CharField(max_length=100, blank=True, null=True)
    comment_content = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = "b_comment"


class Advantage(models.Model):
    id = models.BigAutoField(primary_key=True)
    advantage_image = models.CharField(max_length=100, blank=True, null=True)
    advantage_title = models.CharField(max_length=100, blank=True, null=True)
    advantage_description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = "b_advantage"


class About(models.Model):
    id = models.BigAutoField(primary_key=True)
    about_introduction = models.CharField(max_length=1000, blank=True, null=True)
    about_cover = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "b_about"

    @classmethod
    def get_solo(cls):
        try:
            return cls.objects.get()
        except ObjectDoesNotExist:
            return None

    def save(self, *args, **kwargs):
        if not self.pk and About.objects.exists():
            raise ValueError("There can only be one instance.")
        return super().save(*args, **kwargs)


class OpLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    re_ip = models.CharField(max_length=100, blank=True, null=True)
    re_time = models.DateTimeField(auto_now_add=True, null=True)
    re_url = models.CharField(max_length=200, blank=True, null=True)
    re_method = models.CharField(max_length=10, blank=True, null=True)
    re_content = models.CharField(max_length=200, blank=True, null=True)
    access_time = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = "b_op_log"
        indexes = [
            models.Index(fields=['re_time'], name='re_time'),  # 指定索引名称
        ]


class ErrorLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    ip = models.CharField(max_length=100, blank=True, null=True)
    url = models.CharField(max_length=200, blank=True, null=True)
    method = models.CharField(max_length=10, blank=True, null=True)
    content = models.CharField(max_length=200, blank=True, null=True)
    log_time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "b_error_log"
