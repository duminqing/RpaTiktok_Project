# models/tiktok_account_model.py
from django.db import models
from django.utils import timezone

TAG_CHOICES = [
    (0, '未分类'),
    (1, '女士'),
    (2, '宠物'),
    (3, '婴儿'),
]
STATUS_CHOICES = [
    (0, '正常'),
    (1, '封号'),
    (2, '养号'),
]
STATUS2_CHOICES = [
    (0, '未使用'),
    (1, '已使用'),
]
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
    account_tag = models.IntegerField(choices=TAG_CHOICES, null=True, blank=True, verbose_name='账号标签')
    account_status = models.IntegerField(choices=STATUS_CHOICES, null=True, blank=True, verbose_name='状态')

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


class Video(models.Model):
    """
    视频信息模型
    对应数据库表: rpa_video
    """
    video_path = models.CharField(max_length=128, null=True, blank=True, verbose_name='视频路径')
    video_tag = models.IntegerField(choices=TAG_CHOICES, default=0, null=True, blank=True, verbose_name='视频标签')
    status = models.IntegerField(choices=STATUS2_CHOICES, default=0, verbose_name='视频状态')

    # 时间字段
    create_date = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    update_date = models.DateTimeField(null=True, blank=True, verbose_name='更新时间')

    class Meta:
        db_table = 'rpa_video'
        verbose_name = '视频信息'
        verbose_name_plural = '视频信息'
        ordering = ['id']

    def __str__(self):
        return f"Video(id={self.id}, video_path='{self.video_path}', status={self.status})"


class VideoCopy(models.Model):
    """
    视频文案模型
    对应数据库表: rpa_video_copy
    """
    copy_content = models.CharField(max_length=256, null=True, blank=True, verbose_name='文案内容')
    copy_tag = models.IntegerField(choices=TAG_CHOICES, null=True, blank=True, verbose_name='文案标签')
    status = models.IntegerField(choices=STATUS2_CHOICES, default=0, verbose_name='文案状态')

    # 时间字段
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'rpa_video_copy'
        verbose_name = '视频文案'
        verbose_name_plural = '视频文案'
        ordering = ['id']

    def __str__(self):
        return f"VideoCopy(id={self.id}, copy_content='{self.copy_content[:30]}...', status={self.status})"


class SearchWord(models.Model):
    """
    搜索词汇模型
    对应数据库表: rpa_search_word
    """
    tag_type = models.IntegerField(choices=TAG_CHOICES, null=True, blank=True, verbose_name='标签类型')
    search_word = models.TextField(null=True, blank=True, verbose_name='搜索词汇')

    class Meta:
        db_table = 'rpa_search_word'
        verbose_name = '搜索词汇'
        verbose_name_plural = '搜索词汇'
        ordering = ['id']

    def __str__(self):
        return f"SearchWord(id={self.id}, search_word='{self.search_word[:30]}...')"


class VideoData(models.Model):
    id = models.AutoField(primary_key=True)
    tiktok_account = models.CharField(max_length=255, null=True, blank=True, verbose_name='TikTok账号')
    video_id = models.CharField(max_length=255, unique=True, null=True, blank=True, verbose_name='视频ID')
    desc = models.TextField(null=True, blank=True, verbose_name='视频描述')
    collect_count = models.IntegerField(default=0, verbose_name='收藏数')
    comment_count = models.IntegerField(default=0, verbose_name='评论数')
    digg_count = models.IntegerField(default=0, verbose_name='点赞数')
    play_count = models.IntegerField(default=0, verbose_name='播放数')
    share_count = models.IntegerField(default=0, verbose_name='分享数')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'rpa_video_data'
        verbose_name = '视频数据'
        verbose_name_plural = '视频数据'
        ordering = ['-create_date']

    def __str__(self):
        return f"VideoData(id={self.id}, tiktok_account='{self.tiktok_account}', video_id='{self.video_id}')"
