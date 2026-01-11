import logging

from browser_bit.bit_manager import task_manager
from browser_bit.bit_video_data import video_data
from .android_common import open_tiktok, press_home, random_sleep
from .android_connect_device import connect_device

logger = logging.getLogger(__name__)

def perform_tiktok_video_data(**kwargs):
    """
    执行TikTok视频数据获取任务
    """
    device_id = kwargs.get('device_id')
    pad_code = kwargs.get('pad_code')
    local_ip = kwargs.get('local_ip')
    local_port = kwargs.get('local_port')
    task_id = kwargs.get('task_id')
    tiktok_account = kwargs.get('tiktok_account')
    
    # 连接设备
    logger.info(f"{task_id}正在连接设备{device_id}")
    try:
        device = connect_device(device_id, pad_code, local_ip, local_port)
    except Exception as e:
        logger.error(f"{task_id}连接设备{device_id}失败: {str(e)}")
        return {"status": "error", "message": f"{task_id}连接设备{device_id}失败"}
    
    # 打开TikTok应用
    open_tiktok(device)
    
    # 这里可以添加视频数据收集的逻辑
    logger.info(f"{task_id}开始收集用户 {tiktok_account} 的视频数据")
    
    # 示例：滚动并收集数据
    for i in range(5):  # 滚动5次
        device.swipe_ext("up")
        random_sleep(2, 3)
    
    press_home(device)
    logger.info(f"{task_id}视频数据收集完成")
    
    return {"status": "success", "message": "Video data collection completed"}

def get_video_data(**kwargs):
    """
    提交视频数据获取任务, 通过代理浏览器获取比较方便
    """
    kwargs['pad_code'] = '';
    task_id = task_manager.submit_task(video_data, **kwargs)
    return task_id