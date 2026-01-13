from .android_connect_device import connect_device
import logging
import time
import random
import asyncio
from .android_common import click_element, press_home, screenshot, open_tiktok, random_sleep, click_bound
logger = logging.getLogger(__name__)


def perform_tiktok_scrolling(**kwargs):
    """
    执行TikTok滚动任务的实际函数
    这个函数将由任务管理器的设备线程调用
    """
    pad_code = kwargs.get('pad_code')
    local_ip = kwargs.get('local_ip')
    local_port = kwargs.get('local_port')
    scrolling_time = int(kwargs.get('scrolling_time'))
    device_id=kwargs.get('device_id')

    # 连接设备
    logger.info(f"{device_id}正在连接设备{device_id}")    
    try:
        device = connect_device(device_id, pad_code, local_ip, local_port)
    except Exception as e:
        logger.error(f"{device_id}连接设备{device_id}失败: {str(e)}")
        return {"status": "error", "message": f"{device_id}连接设备{device_id}失败"}
    
    end_time = time.time() + scrolling_time*60
    total=0
    logger.info(f"{device_id}打开TikTok")
    open_tiktok(device)
    logger.info(f"{device_id}搜索pads")
    search(device,device_id)
    while time.time()<end_time:
        try:
            logger.info(f"{device_id}刷第{total+1}次")
            total+=1
            device.swipe_ext("up")
            app_current = device.app_current()['package']
            if app_current != 'com.zhiliaoapp.musically' and app_current != 'om.ss.android.ugc.trill':
                logger.error(f"{device_id}当前应用包名：{app_current} 当前应用不是TikTok，可能已经退出，截图路径: {screenshot(device, device_id, "EXIT")}")
                open_tiktok(device)
                continue
            random_sleep()
            live_now_exists = device(text="LIVE now").exists()
            watch_live_exists = device(text="Tap to watch LIVE").exists()
            if live_now_exists or watch_live_exists:
                logger.debug(f"{device_id}发现LIVE视频，继续下一个视频")
                continue
            else:
                random_sleep(10,30)
                if random.randint(0, 100)<20:
                    click_like(device,device_id)
                if random.randint(0, 100)<10:
                    click_favourites(device,device_id)
        except Exception as e:
            logger.error(f"{device_id}刷视频异常，截图路径: {screenshot(device,device_id, "ERROR")}，错误信息: {str(e)}")
            open_tiktok(device)
            continue
    logger.info(f"{device_id}刷视频完成，共刷{total}次")
    press_home(device)
    return {"status": "success", "message": "Scrolling completed"}

def search(device,device_id):
    try:
        list = device.xpath('//android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.ImageView').all()
        if len(list) > 1:
            element = list[1]
            click_element(device, element)
        else:
            logger.warning(f"{device_id}元素列表长度不足2个，当前长度: {len(list)}")
        #//android.widget.EditText
        # 方式2：简化写法（直接链式调用，若控件不存在会抛出异常，可按需使用）
        device.xpath('//android.widget.EditText').set_text("pads")
        random_sleep()
        # search按钮[836,84][1080,216]  //*[@text="Search"]
        device.press("enter")
        random_sleep()
        # Videos tab[466,228][615,348]  //*[@text="Videos"]
        device(text="Videos").click()
        random_sleep()
        # 第一个视频 [24,372][528,1178]
        logger.info(f"点击第一个视频")
        click_bound(device, (24,372,528,1178))
        random_sleep()
    except:
        logger.error(f"点击搜索失败,{screenshot(device,device_id, "SEARCH_ERROR")}")

def click_like(device,device_id):
    try:
        logger.info(f"{device_id}点击点赞")
        device(descriptionContains="Like").click()
        random_sleep()
    except:
        logger.error(f"点击点赞失败,{screenshot(device,device_id, "LIKE_ERROR")}")

def click_favourites(device,device_id):
    #//androidx.viewpager.widget.ViewPager/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.LinearLayout
    
    try:
        logger.info(f"{device_id}点击收藏")
        list = device.xpath('//androidx.viewpager.widget.ViewPager/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.LinearLayout/android.widget.FrameLayout').all()
        if len(list) > 3:
            element = list[3]
            click_element(device, element)
        else:
            logger.warning(f"{device_id}收藏元素列表长度不足4个，当前长度: {len(list)}")
        # if device_id.startswith("MYT"):
        #     click_bound(device, (923,1178,1080,1328)) #MYT_006[923,1178][1080,1328] #MYT001#[918,1208][1080,1370] 
        # else:
        #     click_bound(device, (975,1370,1065,1460)) 
        random_sleep()
    except:
        logger.error(f"点击收藏失败,{screenshot(device,device_id, "FAVOURITES_ERROR")}")
