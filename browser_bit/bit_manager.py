import asyncio
from playwright.async_api import async_playwright
import threading
from typing import Dict, Any, Callable
from queue import Queue
import uuid
from concurrent.futures import ThreadPoolExecutor
import time

class TaskManager:
    """
    任务管理器，包含任务队列和浏览器实例管理
    """
    def __init__(self, max_concurrent=4):
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.task_queue = Queue()
        self.active_devices = set()  # 正在运行的 device_id 集合
        self.device_locks = {}  # 每个 device_id 的锁
        self.lock = threading.Lock()  # 线程安全锁
        self.playwright_instance = None
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self.worker_thread.start()

    async def initialize(self):
        """初始化 playwright 实例"""
        if not self.playwright_instance:
            self.playwright_instance = await async_playwright().start()

    def _get_device_id(self, kwargs: Dict[str, Any]) -> str:
        """从参数中获取设备ID"""
        device_id = kwargs.get('device_id') or kwargs.get('pad_code')
        if not device_id:
            raise ValueError("任务参数中必须包含 device_id 或 pad_code")
        return str(device_id)

    def get_or_create_device_lock(self, device_id: str):
        """获取或创建特定设备的锁"""
        with self.lock:
            if device_id not in self.device_locks:
                self.device_locks[device_id] = threading.Lock()
            return self.device_locks[device_id]

    def submit_task(self, task_func: Callable, **kwargs):
        """
        提交任务到队列
        :param task_func: 要执行的任务函数
        :param kwargs: 传递给任务函数的参数，必须包含 device_id 或 pad_code
        """
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'func': task_func,
            'kwargs': kwargs,
            'submit_time': time.time()
        }
        self.task_queue.put(task)
        return task_id

    def _process_tasks(self):
        """在后台线程中处理任务"""
        while self.running:
            try:
                # 从队列中获取任务
                task = self.task_queue.get(timeout=1)
                if task is None:  # 用于停止线程的信号
                    break
                
                # 执行任务
                self._execute_task(task)
                self.task_queue.task_done()
            except:
                continue  # 超时或其他异常，继续循环

    def _execute_task(self, task: dict):
        """执行单个任务"""
        device_id = self._get_device_id(task['kwargs'])
        
        # 获取设备特定的锁
        device_lock = self.get_or_create_device_lock(device_id)

        # 先获取设备级锁，确保同一设备不会并发执行
        with device_lock:
            # 将设备标记为活跃状态
            with self.lock:
                self.active_devices.add(device_id)
            
            try:
                # 执行任务，传入 playwright 实例
                if self.playwright_instance:
                    # 使用 asyncio.run 在新事件循环中运行协程
                    import asyncio
                    asyncio.run(task['func'](self.playwright_instance, **task['kwargs']))
                else:
                    raise RuntimeError("Playwright instance not initialized")
            finally:
                # 移除活跃设备标记
                with self.lock:
                    self.active_devices.discard(device_id)

    def shutdown(self):
        """关闭管理器"""
        self.running = False
        self.task_queue.put(None)  # 发送停止信号
        self.executor.shutdown(wait=True)
        if self.playwright_instance:
            import asyncio
            # 在单独的线程中关闭 playwright
            close_thread = threading.Thread(
                target=lambda: asyncio.run(self.playwright_instance.stop())
            )
            close_thread.start()

# 创建全局任务管理器实例
task_manager = TaskManager(max_concurrent=4)