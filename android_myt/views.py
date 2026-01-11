
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .android_manager import android_task_manager
from .android_post import perform_tiktok_post
from .android_scrolling import perform_tiktok_scrolling
from .android_video_data import perform_tiktok_video_data

# Create your views here.

@csrf_exempt
@require_http_methods(["POST"])
def post_video(request):
    """
    安卓视频发布接口
    """
    try:
        data = json.loads(request.body)
        
        # 准备参数字典
        kwargs = {
            'device_id': data.get('device_id'),
            'pad_code': data.get('pad_code'),
            'local_ip': data.get('local_ip'),
            'local_port': data.get('local_port'),
            'video_path': data.get('video_path'),
            'video_desc': data.get('video_desc'),
        }
        
        # 过滤掉 None 值
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        # 提交任务到内存队列
        task_id = android_task_manager.submit_task(perform_tiktok_post, **kwargs)
        
        # 立即返回任务ID，不等待任务完成
        return JsonResponse({
            'success': True, 
            'task_id': task_id,
            'message': 'Android post video task has been queued successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def scroll_videos(request):
    """
    安卓视频滚动接口
    """
    try:
        data = json.loads(request.body)
        
        # 准备参数字典
        kwargs = {
            'device_id': data.get('device_id'),
            'pad_code': data.get('pad_code'),
            'local_ip': data.get('local_ip'),
            'local_port': data.get('local_port'),
            'scrolling_time': data.get('scrolling_time')
        }
        
        # 过滤掉 None 值
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        # 提交任务到内存队列
        task_id = android_task_manager.submit_task(perform_tiktok_scrolling, **kwargs)
        
        # 立即返回任务ID，不等待任务完成
        return JsonResponse({
            'success': True, 
            'task_id': task_id,
            'message': 'Android scroll videos task has been queued successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def get_video_data(request):
    """
    安卓视频数据获取接口
    """
    try:
        data = json.loads(request.body)
        
        # 准备参数字典
        kwargs = {
            'device_id': data.get('device_id'),
            'pad_code': data.get('pad_code'),
            'local_ip': data.get('local_ip'),
            'local_port': data.get('local_port'),
            'tiktok_account': data.get('tiktok_account'),
        }
        
        # 过滤掉 None 值
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        # 提交任务到内存队列
        task_id = android_task_manager.submit_task(perform_tiktok_video_data, **kwargs)
        
        # 立即返回任务ID，不等待任务完成
        return JsonResponse({
            'success': True, 
            'task_id': task_id,
            'message': 'Android video data task has been queued successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})