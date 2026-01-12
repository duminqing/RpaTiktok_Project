# models/tiktok_account_model.py
from django.db import models
from django.utils import timezone


class TikTokAccountInfo(models.Model):
    """
    TikTok 账号信息模型
    对应数据库表: rpa_tiktok_account_info
    """
    # 账号基本信息
    device_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='设备ID')
    tiktok_account = models.CharField(max_length=255, null=True, blank=True, verbose_name='TK账号')
    account_password = models.CharField(max_length=255, null=True, blank=True, verbose_name='TK密码')

    # 账号标签和状态
    account_tag = models.IntegerField(null=True, blank=True, verbose_name='账号标签')
    account_status = models.IntegerField(null=True, blank=True, verbose_name='状态')

    # 统计信息
    account_likes = models.IntegerField(null=True, blank=True, verbose_name='点赞数')
    account_followers = models.IntegerField(null=True, blank=True, verbose_name='关注数')

    # 联系信息
    account_phone = models.CharField(max_length=255, null=True, blank=True, verbose_name='手机号')
    account_mail = models.CharField(max_length=255, null=True, blank=True, verbose_name='邮箱')
    mail_password = models.CharField(max_length=255, null=True, blank=True, verbose_name='邮箱密码')

    # 备注信息
    account_momo = models.TextField(null=True, blank=True, verbose_name='备注')

    # 时间字段
    create_date = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'rpa_tiktok_account_info'
        verbose_name = '账号信息'
        verbose_name_plural = '账号信息'
        ordering = ['-create_date']

    def __str__(self):
        return f"TikTokAccountInfo(id={self.id}, tiktok_account='{self.tiktok_account}', device_id='{self.device_id}')"


class Device(models.Model):
    """
    设备信息模型
    对应数据库表: rpa_device
    """
    device_id = models.CharField(max_length=32, null=True, blank=True, verbose_name='设备ID')
    device_type = models.CharField(max_length=64, null=True, blank=True, verbose_name='设备类型')
    device_code = models.CharField(max_length=128, null=True, blank=True, verbose_name='设备编码')
    local_ip = models.CharField(max_length=64, null=True, blank=True, verbose_name='本地IP')
    local_port = models.IntegerField(null=True, blank=True, verbose_name='本地端口')
    proxy_ip = models.CharField(max_length=64, null=True, blank=True, verbose_name='代理IP')

    class Meta:
        db_table = 'rpa_device'
        verbose_name = '设备信息'
        verbose_name_plural = '设备信息'
        ordering = ['id']

    def __str__(self):
        return f"Device(id={self.id}, device_id='{self.device_id}', device_type='{self.device_type}')"