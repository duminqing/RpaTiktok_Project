from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

# 全球调度器实例
scheduler = None


def execute_video_publishing_job():
    """每天凌晨3点执行的视频发布任务"""
    # 延迟导入，避免AppRegistryNotReady错误
    from common.task_executor import execute_tiktok_publishing_tasks
    print("开始执行定时视频发布任务...")
    try:
        execute_tiktok_publishing_tasks()
        print("定时视频发布任务执行完成")
    except Exception as e:
        print(f"定时视频发布任务执行失败: {str(e)}")

def execute_scrolling_job():
    """每天凌晨3点执行的视频发布任务"""
    # 延迟导入，避免AppRegistryNotReady错误
    from common.task_executor import execute_tiktok_scrolling_tasks
    print("开始执行定时刷视频任务...")
    try:
        execute_tiktok_scrolling_tasks()
        print("定时刷视频任务执行完成")
    except Exception as e:
        print(f"定时刷视频执行失败: {str(e)}")

def execute_video_data_job():
    """每天凌晨3点执行的视频发布任务"""
    # 延迟导入，避免AppRegistryNotReady错误
    from common.task_executor import execute_tiktok_video_data_tasks
    print("开始执行定时视频数据抓取任务...")
    try:
        execute_tiktok_video_data_tasks()
        print("定时视频数据抓取任务执行完成")
    except Exception as e:
        print(f"定时视频数据抓取执行失败: {str(e)}")
        
def start_scheduler():
    """启动定时任务调度器"""
    global scheduler
    
    if not getattr(settings, 'TESTING', False):  # 避免测试时启动调度器
        if scheduler is None:
            scheduler = BackgroundScheduler()
        
        # 检查任务是否已经存在，避免重复添加
        if not scheduler.running:
            scheduler.start()
        # 检查是否已有相同ID的任务
        if not scheduler.get_job('video_publishing_job'):
            scheduler.add_job(
                execute_video_publishing_job,  # 传递函数引用而不是执行函数
                'cron',
                hour=3,
                minute=0,
                id='video_publishing_job',
                name='每天凌晨3点执行视频发布的任务',
                misfire_grace_time=3600  # 设置错过执行的宽限时间为1小时
            )
            print("定时任务已添加: 每天凌晨3点执行视频发布")
        else:
            print("定时任务已存在，无需重复添加")
            
        if not scheduler.get_job('scrolling_job'):
            scheduler.add_job(
                execute_scrolling_job,  # 传递函数引用而不是执行函数
                'cron',
                hour='1,7',  # 表示1点和8点
                minute=0,
                id='scrolling_job',
                name='每天1,7点执行刷视频任务',
                misfire_grace_time=3600  # 设置错过执行的宽限时间为1小时
            )
            print("定时任务已添加: 每天1,7点执行刷视频")
        else:
            print("定时任务已存在，无需重复添加")

        if not scheduler.get_job('video_data_job'):
            scheduler.add_job(
                execute_video_data_job,  # 传递函数引用而不是执行函数
                'cron',
                hour='6,12,18,24',  #
                minute=0,
                id='video_data_job',
                name='每天6,12,18,24点执行视频数据任务',
                misfire_grace_time=3600  # 设置错过执行的宽限时间为1小时
            )
            print("定时任务已添加: 每天6,12,18,24点执行视频数据任务")
        else:
            print("定时任务已存在，无需重复添加")


def stop_scheduler():
    """停止定时任务调度器"""
    global scheduler
    
    if scheduler and scheduler.running:
        scheduler.shutdown()