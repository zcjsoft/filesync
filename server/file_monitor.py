import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileMonitor:
    def __init__(self, monitor_dir, event_callback):
        """初始化文件监控器"""
        self.monitor_dir = monitor_dir
        self.event_callback = event_callback
        self.observer = None
        self.running = False
    
    def start(self):
        """启动文件监控"""
        if self.running:
            return
        
        # 创建事件处理器
        event_handler = FileMonitorHandler(self.event_callback, self.monitor_dir)
        
        # 创建并启动观察者
        self.observer = Observer()
        self.observer.schedule(event_handler, self.monitor_dir, recursive=True)
        self.observer.start()
        self.running = True
        print(f"File monitor started on {self.monitor_dir}")
    
    def stop(self):
        """停止文件监控"""
        if not self.running:
            return
        
        self.running = False
        self.observer.stop()
        self.observer.join()
        print("File monitor stopped")

class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, callback, root_dir):
        """初始化事件处理器"""
        self.callback = callback
        self.root_dir = root_dir
        self.last_event_time = {}
    
    def on_any_event(self, event):
        """处理所有文件系统事件"""
        # 忽略目录事件
        if event.is_directory:
            return
        
        # 忽略临时文件和隐藏文件
        filename = os.path.basename(event.src_path)
        if filename.startswith('.') or filename.endswith('.tmp'):
            return
        
        # 防抖处理：同一文件短时间内的多次事件只处理一次
        current_time = time.time()
        if event.src_path in self.last_event_time:
            if current_time - self.last_event_time[event.src_path] < 0.5:
                return
        self.last_event_time[event.src_path] = current_time
        
        # 处理不同类型的事件
        event_type = ''
        
        if event.event_type == 'created':
            event_type = 'CREATE'
        elif event.event_type == 'modified':
            event_type = 'MODIFY'
        elif event.event_type == 'deleted':
            event_type = 'DELETE'
        elif event.event_type == 'moved':
            event_type = 'RENAME'
            old_path = event.src_path
            new_path = event.dest_path
            self.callback(event_type, old_path, new_path)
            return
        
        # 发送事件通知
        self.callback(event_type, event.src_path)
