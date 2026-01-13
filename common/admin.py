from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from .models import TikTokAccountInfo, Device, Video, VideoCopy, SearchWord, VideoData
from django import forms
import os

# 定义常量以避免模型加载问题
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


@admin.register(TikTokAccountInfo)
class TikTokAccountInfoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'tiktok_account', 'account_tag', 'device_id', 'account_status',
        'account_likes', 'account_followers', 'create_date'
    ]
    list_filter = ['account_status', 'account_tag', 'create_date']
    search_fields = ['tiktok_account', 'device_id', 'account_mail']
    readonly_fields = ['create_date', 'update_date']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('device_id', 'tiktok_account', 'account_password')
        }),
        ('账号信息', {
            'fields': ('account_tag', 'account_status', 'account_likes', 'account_followers')
        }),
        ('联系方式', {
            'fields': ('account_phone', 'account_mail', 'mail_password')
        }),
        ('备注', {
            'fields': ('account_momo',)
        }),
        ('时间信息', {
            'fields': ('create_date', 'update_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'device_id', 'device_type', 'device_code', 
        'local_ip', 'local_port', 'proxy_ip'
    ]
    list_filter = ['device_type', 'local_port']
    search_fields = ['device_id', 'device_code', 'local_ip', 'proxy_ip']
    
    fieldsets = (
        ('基本设备信息', {
            'fields': ('device_id', 'device_type', 'device_code')
        }),
        ('网络配置', {
            'fields': ('local_ip', 'local_port', 'proxy_ip')
        }),
    )


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'video_path', 'video_tag', 'status', 
        'create_date', 'update_date'
    ]
    list_filter = ['status', 'video_tag', 'create_date']
    search_fields = ['video_path']
    
    fieldsets = (
        ('视频信息', {
            'fields': ('video_path', 'video_tag', 'status')
        }),
        ('时间信息', {
            'fields': ('create_date', 'update_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VideoCopy)
class VideoCopyAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'copy_content', 'copy_tag', 'status', 
        'create_date', 'update_date'
    ]
    list_filter = ['status', 'copy_tag', 'create_date']
    search_fields = ['copy_content']
    
    fieldsets = (
        ('文案信息', {
            'fields': ('copy_content', 'copy_tag', 'status')
        }),
        ('时间信息', {
            'fields': ('create_date', 'update_date'),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-add/', self.admin_site.admin_view(self.bulk_add_view), name='common_videocopy_bulk_add'),
        ]
        return custom_urls + urls

    def bulk_add_view(self, request):
        # 在函数内部定义表单，使用模块级常量
        class BulkVideoCopyForm(forms.Form):
            copy_file = forms.FileField(label='选择TXT文件')
            copy_tag = forms.ChoiceField(
                choices=[('', '---------')] + [(i, label) for i, label in TAG_CHOICES],
                required=False,
                label='文案标签'
            )
        
        if request.method == 'POST':
            form = BulkVideoCopyForm(request.POST, request.FILES)
            if form.is_valid():
                copy_file = request.FILES['copy_file']
                copy_tag = form.cleaned_data['copy_tag']
                
                # 检查文件扩展名
                if not copy_file.name.endswith('.txt'):
                    messages.error(request, '请选择一个TXT文件')
                    return render(request, 'admin/bulk_add_videocopy.html', {'form': form, 'title': '批量添加视频文案'})
                
                # 读取文件内容
                file_content = copy_file.read().decode('utf-8')
                lines = file_content.splitlines()
                
                created_count = 0
                for line in lines:
                    line = line.strip()
                    if line:  # 忽略空行
                        VideoCopy.objects.create(
                            copy_content=line,
                            copy_tag=int(copy_tag) if copy_tag else None,
                            status=0  # 默认设置为未使用
                            # 注意：不需要手动设置create_date和update_date，因为模型中有auto_now_add和auto_now
                        )
                        created_count += 1
                
                messages.success(request, f'成功批量添加了 {created_count} 条文案内容')
                
                # 根据按钮判断跳转
                if '_continue' in request.POST:
                    # 继续编辑 - 保持在当前页面
                    form = BulkVideoCopyForm()
                    return render(request, 'admin/bulk_add_videocopy.html', {'form': form, 'title': '批量添加视频文案'})
                elif '_addanother' in request.POST:
                    # 再添加一个 - 返回当前页面，清空表单
                    form = BulkVideoCopyForm()
                    return render(request, 'admin/bulk_add_videocopy.html', {'form': form, 'title': '批量添加视频文案'})
                else:
                    # 批量 - 返回列表页
                    return redirect('../')
        else:
            form = BulkVideoCopyForm()

        context = {
            'form': form,
            'title': '批量添加视频文案',
        }
        return render(request, 'admin/bulk_add_videocopy.html', context)


@admin.register(SearchWord)
class SearchWordAdmin(admin.ModelAdmin):
    list_display = [
        'id',  'tag_type', 'search_word',
    ]
    list_filter = ['tag_type']
    search_fields = ['search_word']
    
    fieldsets = (
        ('搜索词信息', {
            'fields': ['search_word', 'tag_type']
        }),
    )

@admin.register(VideoData)
class VideoDataAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'tiktok_account', 'video_id', 'desc',
        'collect_count', 'comment_count', 'digg_count',
        'play_count', 'share_count', 'create_date', 'update_date'
    ]
    list_filter = ['tiktok_account', 'create_date']
    search_fields = ['tiktok_account', 'video_id', 'desc']

    fieldsets = ()