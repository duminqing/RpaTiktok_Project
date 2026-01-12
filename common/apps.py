from django.apps import AppConfig
from .scheduler import start_scheduler
import threading

# 用于防止重复启动的标志
scheduler_started = False

class CommonConfig(AppConfig):
    name = 'common'
    
    def ready(self): 
        """
        在Django应用准备就绪时启动定时任务
        使用线程确保不会阻塞Django启动过程
        """
        global scheduler_started
        # 防止Django的reload过程中重复启动
        if not scheduler_started:
            scheduler_started = True
            # 启动调度器的线程
            scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
            scheduler_thread.start()