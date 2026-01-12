from django.utils import timezone

from common.models import TikTokAccountInfo, Device, Video, VideoCopy
from browser_bit.bit_manager import browser_task_manager
from browser_bit.bit_post import post
from android_myt.android_manager import android_task_manager
from android_myt.android_post import perform_tiktok_post

def execute_tiktok_scrolling_tasks():
    # 从数据库查询rpa_tiktok_account_info查询状态为0的数据，循环操作
    # 1）通过rpa_tiktok_account_info.device_id = rpa_device.device_id查询到对应的设备信息
    # 2）
    pass


def execute_tiktok_publishing_tasks():
    """
    执行TikTok发布任务的主要方法
    从rpa_tiktok_account_info表中获取account_status=0的账号，
    然后关联设备信息和视频信息，组装数据后提交任务
    """
    # 获取所有account_status=0的账号
    accounts = TikTokAccountInfo.objects.filter(account_status=0)
    
    for account in accounts:
        # 1) 通过account.device_id关联到Device表获取设备信息
        device = Device.objects.filter(device_id=account.device_id).first()
        
        if not device:
            print(f"未找到设备ID为 {account.device_id} 的设备信息，跳过账号 {account.tiktok_account}")
            continue
            
        # 2) 通过account.account_tag = Video.video_tag 获取status=0的视频数据
        video = Video.objects.filter(video_tag=account.account_tag, status=0).first()
        
        if not video:
            print(f"未找到标签为 {account.account_tag} 且状态为0的视频，跳过账号 {account.tiktok_account}")
            continue
            
        # 3) 通过account.account_tag = VideoCopy.copy_tag 获取status=0的文案数据
        video_copy = VideoCopy.objects.filter(copy_tag=account.account_tag, status=0).first()
        
        if not video_copy:
            print(f"未找到标签为 {account.account_tag} 且状态为0的文案，跳过账号 {account.tiktok_account}")
            continue
            
        # 根据device_id前缀决定使用哪个方法
        if account.device_id.startswith("BIT"):
            # 使用browser_bit的post方法
            kwargs = {
                'device_id': account.device_id,
                'device_code': device.device_code,  # 使用设备编码连接浏览器
                'video_path': video.video_path,
                'video_copy': video_copy.copy_content,
            }
            
            # 提交任务到任务管理器
            task_id = browser_task_manager.submit_task(post, **kwargs)
            print(f"已提交浏览器任务，账号: {account.tiktok_account}, 任务ID: {task_id}")
        else:
            # 使用android_myt的perform_tiktok_post方法
            kwargs = {
                'device_id': account.device_id,
                'pad_code': device.device_code,
                'local_ip': device.local_ip,
                'local_port': device.local_port,
                'video_path': video.video_path,
                'video_desc': video_copy.copy_content,
            }
            
            # 提交任务到Android任务管理器
            task_id = android_task_manager.submit_task(perform_tiktok_post, **kwargs)
            print(f"已提交安卓任务，账号: {account.tiktok_account}, 任务ID: {task_id}")
        
        # 任务提交完成后，将本次使用到的video和video_copy数据的status设为1
        video.status = 1
        video.update_date = timezone.now()
        video.save()

        video_copy.status = 1
        video.update_date = timezone.now()
        video_copy.save()
        print(f"已更新视频和文案状态，视频ID: {video.id}, 文案ID: {video_copy.id}")