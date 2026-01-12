import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

logger = logging.getLogger(__name__)

# 全球调度器实例
scheduler = None

def start_scheduler():
    """启动定时任务调度器"""
    global scheduler
    
    if not getattr(settings, 'TESTING', False):  # 避免测试时启动调度器
        if scheduler is None:
            scheduler = BackgroundScheduler()
        
        # 检查任务是否已经存在，避免重复添加
        if not scheduler.running:
            scheduler.start()
        from common.task_executor import execute_tiktok_publishing_tasks
        # 检查是否已有相同ID的任务
        if not scheduler.get_job('video_publishing_job'):
            scheduler.add_job(
                execute_tiktok_publishing_tasks,  # 传递函数引用而不是执行函数
                'cron',
                hour=2,
                minute=0,
                id='video_publishing_job',
                name='每天凌晨3点执行视频发布的任务'
            )
            print("定时任务已添加: 每天凌晨3点执行视频发布")
            logger.info("定时任务已添加: 每天凌晨3点执行视频发布")
        else:
            print("定时任务已存在，无需重复添加")
            logger.info("定时任务已存在，无需重复添加")


def stop_scheduler():
    """停止定时任务调度器"""
    global scheduler
    
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("定时任务调度器已关闭")