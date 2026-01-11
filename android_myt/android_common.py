import random
import logging
import time
logger = logging.getLogger(__name__)

def press_home(device):
    device.press("home")

def screenshot(device,task_id, error_detail):
    screenshot_path = rf"E:/ScreenShot/{error_detail}_{task_id}_{time.strftime('%Y%m%d%H%M%S', time.localtime())}.png"
    device.screenshot(screenshot_path)
    random_sleep()
    return screenshot_path

def open_tiktok(device):
    device.shell("am start -S -n com.zhiliaoapp.musically/com.ss.android.ugc.aweme.main.MainActivity")
    random_sleep(8,10)

def random_sleep(min_sleep=3, max_sleep=5):
    sleep_time = random.randint(min_sleep, max_sleep)
    time.sleep(sleep_time)

def click_bound(device, bounds):
    x1, y1, x2, y2 = bounds
    # 模拟真人的“中心偏向”随机（正态分布）
    # 相比均匀分布，这更像人类点击习惯：更倾向于点中心，偶尔点到边缘
    mean_x = (x1 + x2) / 2
    mean_y = (y1 + y2) / 2
    std_x = (x2 - x1) / 6
    std_y = (y2 - y1) / 6
    target_x = int(random.gauss(mean_x, std_x))
    target_y = int(random.gauss(mean_y, std_y))
    # 确保坐标最终没超出边界
    target_x = max(x1, min(target_x, x2))
    target_y = max(y1, min(target_y, y2))
    device.click(target_x, target_y)
    random_sleep()

def click_element(device, element):
    """
    点击DeviceXMLElement元素，参考click_bound方法的实现
    """
    fl_info = element.info
    bounds = fl_info.get('bounds')
    if bounds:
        x1, y1 = bounds.get('left'), bounds.get('top')
        x2, y2 = bounds.get('right'), bounds.get('bottom')
        click_bound(device, (x1, y1, x2, y2))
    else:
        logger.error(f"元素没有bounds信息，无法点击")
