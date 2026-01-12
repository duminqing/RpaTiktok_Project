default_app_config = 'common.apps.CommonConfig'

# 导入调度器相关功能
try:
    from .scheduler import start_scheduler, stop_scheduler
except ImportError:
    pass