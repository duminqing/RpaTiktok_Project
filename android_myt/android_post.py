import requests
import datetime
from . android_connect_device import connect_device

from . android_common import press_home, screenshot, open_tiktok, random_sleep, click_bound
import logging
logger = logging.getLogger(__name__)

def perform_tiktok_post(**kwargs):
    device_id = kwargs.get('device_id')
    pad_code = kwargs.get('pad_code')
    local_ip = kwargs.get('local_ip')
    local_port = kwargs.get('local_port')
    video_path = kwargs.get('video_path')
    device_id = kwargs.get('device_id')
    # 连接设备
    logger.info(f"{device_id}连接设备")
    try:
        device = connect_device(device_id, pad_code, local_ip, local_port)
        upload_video(device, video_path)
    except Exception as e:
        logger.error(f"{device_id}连接设备失败: {str(e)}")
        return {"status": "error", "message": f"连接设备失败: {str(e)}"}
    open_tiktok(device)
    try:
        post_video(device,**kwargs)
    except Exception as e:
        logger.error(f"{device_id}发布视频失败: {str(e)}，截图地址{screenshot(device,device_id,"POST_ERROR")}")
        return {"status": "error", "message": f"发布视频失败: {str(e)}"}
    press_home(device)
    return None


def post_video(device, **kwargs):
    device_id = kwargs.get('device_id')
    video_desc = kwargs.get('video_desc')
    if device_id.startswith("VMOS"):
        logger.info(f"{device_id}点击发视频...")
        click_bound(device, (465,1822,615,1920)) #[465,1822][615,1920]
        logger.info(f"{device_id}选择相册...")
        click_bound(device, (804,1650,916,1762)) #[804,1650][916,1762]
        logger.info(f"{device_id}点击视频TAB...")
        device(text="Videos").click()
        random_sleep()
        logger.info(f"{device_id}选择第一个视频...")
        click_bound(device, (4,238,359,596)) #[4,238][359,596]
        logger.info(f"{device_id}点击下一步...")
        device(text="Next").click()
        random_sleep()
        logger.info(f"{device_id}输入视频描述...")
        input_element = device(textContains="Add description")
        input_element.set_text(video_desc)
        random_sleep()
        logger.info(f"{device_id}点击发布...")
        device(text="Post").click()
        random_sleep()
    else:
        logger.info(f"{device_id}点击发视频...")
        click_bound(device, (432,1794,648,1920))
        if device_id== 'MYT_001':
            logger.info(f"{device_id}点击相册...")
            click_bound(device, (48,1767,156,1875)) 
        else:
            logger.info(f"{device_id}选择相册...")
            click_bound(device, (807,1521,963,1677))
        logger.info(f"{device_id}点击视频TAB...")
        device(text="Videos").click()
        random_sleep()
        logger.info(f"{device_id}选择第一个视频...")
        click_bound(device, (6,357,358,713)) 
        logger.info(f"{device_id}点击下一步...")
        device(text="Next").click()
        random_sleep()
        logger.info(f"{device_id}输入视频描述...")
        input_element = device(textContains="Add description")
        input_element.set_text(video_desc)
        random_sleep()
        logger.info(f"{device_id}点击发布...")
        device(text="Post").click()
        random_sleep()
    click_bound(device, (954,1475,1050,1571)) #[954,1475][1050,1571]
    device(description="Copy link").click()
    random_sleep(60,61)
    kwargs['post_url'] = device.clipboard
    print(f"任务{device_id}上传成功 {kwargs['post_url']}")
    screenshot(device,device_id, "POST_END")
    press_home(device)

def upload_video(device, video_path):
    # 获取当前日期，格式为YYYYMMDDHHMMSS
    current_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # 获取原文件名
    ext_part = video_path.split('.')[-1]
    video_name = f"{current_date}.{ext_part}"
    tmp_path = f"/data/local/tmp/{video_name}"      
    final_path = f"/sdcard/Download/{video_name}"
    # 第一步：推送到临时目录
    logger.info(f"正在通过中转推送: {video_path}=>{tmp_path}")
    device.push(video_path, tmp_path)
    # 第二步：通过 shell 移动并清理（mv 命令在 shell 里通常权限更高）
    logger.info(f"正在通过shell移动: {tmp_path}=>{final_path}")
    device.shell(f"mv {tmp_path} {final_path}")
    # 第三步：关键！通知系统扫描新视频，否则 TikTok 选视频时看不到它
    device.shell(f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{final_path}")
    logger.info(f"视频已成功就绪: {final_path}")
    random_sleep(10,11)
    return final_path


