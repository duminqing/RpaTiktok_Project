import asyncio
from playwright.async_api import async_playwright
import threading
from typing import Dict, Any, Callable
from queue import Queue
import uuid
import time
import concurrent.futures
from datetime import datetime, timedelta

class TaskManager:
    """
    任务管理器，包含任务队列和浏览器实例管理
    """
    def __init__(self, max_concurrent=4):
        self.max_concurrent = max_concurrent
        self.task_queue = Queue()
        self.active_devices = set()  # 正在运行的 device_id 集合
        self.device_locks = {}  # 每个 device_id 的锁
        self.lock = threading.Lock()  # 线程安全锁
        self.running = True
        
        # 启动任务分发线程
        self.dispatcher_thread = threading.Thread(target=self._dispatch_tasks, daemon=True)
        self.dispatcher_thread.start()

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

    def _dispatch_tasks(self):
        """在单独的线程中分发任务，动态创建工作线程"""
        active_workers = []
        
        while self.running:
            try:
                # 从队列中获取任务
                task = self.task_queue.get(timeout=1)
                if task is None:  # 用于停止线程的信号
                    break
                
                # 清理已完成的线程
                active_workers = [w for w in active_workers if w.is_alive()]
                
                # 如果活跃线程数未达到上限，创建新线程处理任务
                if len(active_workers) < self.max_concurrent:
                    worker = threading.Thread(
                        target=self._worker_execute_task, 
                        args=(task,),
                        daemon=True
                    )
                    worker.start()
                    active_workers.append(worker)
                else:
                    # 如果达到最大并发数，等待其中一个线程完成
                    # 将任务放回队列，等待下次循环
                    self.task_queue.put(task)
                    time.sleep(0.1)  # 短暂休眠，避免忙等待
                    continue
                
                self.task_queue.task_done()
            except:
                continue  # 超时或其他异常，继续循环

    def _worker_execute_task(self, task):
        """工作线程执行单个任务"""
        device_id = self._get_device_id(task['kwargs'])
        
        # 获取设备特定的锁
        device_lock = self.get_or_create_device_lock(device_id)

        # 先获取设备级锁，确保同一设备不会并发执行
        with device_lock:
            # 将设备标记为活跃状态
            with self.lock:
                self.active_devices.add(device_id)
            
            try:
                # 执行任务，这里不再需要传递 playwright 实例，因为任务内部会自行创建
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # 直接运行任务，不再传递 playwright 实例
                    loop.run_until_complete(task['func'](**task['kwargs']))
                finally:
                    loop.close()
            finally:
                # 移除活跃设备标记
                with self.lock:
                    self.active_devices.discard(device_id)

    def shutdown(self):
        """关闭管理器"""
        self.running = False
        # 发送停止信号
        self.task_queue.put(None)

# 创建全局任务管理器实例
task_manager = TaskManager(max_concurrent=4)