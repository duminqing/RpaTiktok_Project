from django.contrib import admin
from .models import TikTokAccountInfo, Device

@admin.register(TikTokAccountInfo)
class TikTokAccountInfoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'tiktok_account', 'device_id', 'account_status', 
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