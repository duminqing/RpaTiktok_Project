import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

logger = logging.getLogger(__name__)

# 全局调度器实例
scheduler = None

def start_scheduler():
    """启动定时任务调度器"""
    global scheduler
    
    if not getattr(settings, 'TESTING', False):  # 避免测试时启动调度器
        if scheduler is None:
            scheduler = BackgroundScheduler()
            scheduler.start()
        
        # 添加每5秒执行一次的任务
        if not scheduler.running:
            scheduler.start()
        
        # 检查任务是否已经存在，避免重复添加
        job_exists = any(job.name == 'hello_world_job' for job in scheduler.get_jobs())
        
        if not job_exists:
            scheduler.add_job(
                hello_world_job,
                'interval',
                seconds=5,
                id='hello_world_job',
                name='每5秒输出Hello World的任务',
                replace_existing=True
            )
            print("定时任务已添加: 每5秒输出Hello World")
            logger.info("定时任务已添加: 每5秒输出Hello World")


def stop_scheduler():
    """停止定时任务调度器"""
    global scheduler
    
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("定时任务调度器已关闭")