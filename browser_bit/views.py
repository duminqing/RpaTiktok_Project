from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .bit_manager import browser_task_manager
from .bit_post import post
from .bit_scrolling import scrolling
from . import bit_video_data


@csrf_exempt
@require_http_methods(["POST"])
def post_video(request):
    """
    视频发布接口
    """
    try:
        data = json.loads(request.body)

        # 准备参数字典
        kwargs = {
            "device_id": data.get("device_id"),
            "device_code": data.get("device_code"),
            "video_path": data.get("video_path"),
            "video_copy": data.get("video_copy"),
        }

        # 过滤掉 None 值
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # 提交任务到内存队列
        task_id = browser_task_manager.submit_task(post, **kwargs)

        # 立即返回任务ID，不等待任务完成
        return JsonResponse(
            {
                "success": True,
                "task_id": task_id,
                "message": "Task has been queued successfully",
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def scroll_videos(request):
    """
    视频滚动接口
    """
    try:
        data = json.loads(request.body)

        # 准备参数字典
        kwargs = {
            "device_id": data.get("device_id"),
            "device_code": data.get("device_code"),
            "search_word": data.get("search_word"),
            "scrolling_time": data.get("scrolling_time"),
        }

        # 过滤掉 None 值
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # 提交任务到内存队列
        task_id = browser_task_manager.submit_task(scrolling, **kwargs)

        # 立即返回任务ID，不等待任务完成
        return JsonResponse(
            {
                "success": True,
                "task_id": task_id,
                "message": "Task has been queued successfully",
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def get_video_data(request):
    """
    获取视频数据接口
    """
    try:
        data = json.loads(request.body)

        # 准备参数字典
        kwargs = {
            "device_id": data.get("device_id"),
            "device_code": data.get("device_code"),
            "tiktok_account": data.get("tiktok_account"),
        }

        # 过滤掉 None 值
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # 提交任务到内存队列
        task_id = browser_task_manager.submit_task(bit_video_data.get_video_data, **kwargs)

        # 立即返回任务ID，不等待任务完成
        return JsonResponse(
            {
                "success": True,
                "task_id": task_id,
                "message": "Task has been queued successfully",
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
