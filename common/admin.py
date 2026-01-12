from django.contrib import admin
from .models import TikTokAccountInfo

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