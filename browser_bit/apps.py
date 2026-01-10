from django.apps import AppConfig
import asyncio


class BrowserBitConfig(AppConfig):
    name = 'browser_bit'

    def ready(self):
        # 初始化任务管理器
        from .bit_manager import task_manager
        # 在后台初始化 playwright 实例
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(task_manager.initialize())
        except RuntimeError:
            # 如果事件循环已经存在，则在后台任务中初始化
            pass