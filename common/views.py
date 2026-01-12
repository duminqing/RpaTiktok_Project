from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import TikTokAccountInfo
from django.views.decorators.csrf import csrf_exempt
import json

def get_all_accounts(request):
    """获取所有 TikTok 账号信息"""
    accounts = TikTokAccountInfo.objects.all()
    data = []
    for account in accounts:
        data.append({
            'id': account.id,
            'device_id': account.device_id,
            'tiktok_account': account.tiktok_account,
            'account_tag': account.account_tag,
            'account_status': account.account_status,
            'account_likes': account.account_likes,
            'account_followers': account.account_followers,
            'account_phone': account.account_phone,
            'account_mail': account.account_mail,
            'account_momo': account.account_momo,
            'create_date': account.create_date.isoformat() if account.create_date else None,
            'update_date': account.update_date.isoformat() if account.update_date else None,
        })
    return JsonResponse({'accounts': data})

def get_account_by_id(request, account_id):
    """根据ID获取特定的 TikTok 账号信息"""
    account = get_object_or_404(TikTokAccountInfo, id=account_id)
    data = {
        'id': account.id,
        'device_id': account.device_id,
        'tiktok_account': account.tiktok_account,
        'account_password': account.account_password,  # 注意：实际部署时可能需要隐藏此字段
        'account_tag': account.account_tag,
        'account_status': account.account_status,
        'account_likes': account.account_likes,
        'account_followers': account.account_followers,
        'account_phone': account.account_phone,
        'account_mail': account.account_mail,
        'mail_password': account.mail_password,  # 注意：实际部署时可能需要隐藏此字段
        'account_momo': account.account_momo,
        'create_date': account.create_date.isoformat() if account.create_date else None,
        'update_date': account.update_date.isoformat() if account.update_date else None,
    }
    return JsonResponse(data)

@csrf_exempt
def create_account(request):
    """创建新的 TikTok 账号信息"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            account = TikTokAccountInfo.objects.create(
                device_id=data.get('device_id'),
                tiktok_account=data.get('tiktok_account'),
                account_password=data.get('account_password'),
                account_tag=data.get('account_tag'),
                account_status=data.get('account_status', 1),  # 默认状态为1
                account_likes=data.get('account_likes', 0),
                account_followers=data.get('account_followers', 0),
                account_phone=data.get('account_phone'),
                account_mail=data.get('account_mail'),
                mail_password=data.get('mail_password'),
                account_momo=data.get('account_momo'),
            )
            return JsonResponse({'id': account.id, 'message': 'Account created successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def update_account(request, account_id):
    """更新 TikTok 账号信息"""
    if request.method == 'PUT':
        try:
            account = get_object_or_404(TikTokAccountInfo, id=account_id)
            data = json.loads(request.body)
            
            # 更新字段
            for field, value in data.items():
                if hasattr(account, field):
                    setattr(account, field, value)
            
            account.save()
            return JsonResponse({'message': 'Account updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def delete_account(request, account_id):
    """删除 TikTok 账号信息"""
    if request.method == 'DELETE':
        try:
            account = get_object_or_404(TikTokAccountInfo, id=account_id)
            account.delete()
            return JsonResponse({'message': 'Account deleted successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)