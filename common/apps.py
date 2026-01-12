from django.apps import AppConfig
from .scheduler import start_scheduler
import threading
import os

class CommonConfig(AppConfig):
    name = 'common'
    
    def ready(self): 
        """
        在Django应用准备就绪时启动定时任务
        使用线程确保不会阻塞Django启动过程
        """
        # 检查是否在Django主进程中运行（避免重载进程重复启动）
        if os.environ.get('RUN_MAIN') == 'true':
            # 启动调度器的线程
            scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
            scheduler_thread.start()