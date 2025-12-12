import os
import sys
from config import Config
from file_monitor import FileMonitor
from tcp_server import TCPServer

class FileSyncServer:
    def __init__(self):
        """初始化文件同步服务端"""
        # 加载配置
        self.config = Config()
        
        # 初始化TCP服务器
        self.tcp_server = TCPServer(self.config.bind_ip, self.config.port)
        
        # 初始化文件监控器
        self.file_monitor = FileMonitor(
            self.config.monitor_dir, 
            self.handle_file_event
        )
    
    def handle_file_event(self, event_type, file_path, new_file_path=None):
        """处理文件事件并广播给客户端"""
        # 格式化事件信息
        timestamp = ""  # 可以添加时间戳
        print(f"[{timestamp}] {event_type}: {file_path}")
        
        if event_type == 'RENAME' and new_file_path:
            print(f"  -> {new_file_path}")
            # 构造重命名事件消息
            message = f"{event_type}|{file_path}|{new_file_path}"
        else:
            # 构造其他事件消息
            message = f"{event_type}|{file_path}"
        
        # 向所有客户端广播消息
        self.tcp_server.broadcast(message)
    
    def start(self):
        """启动服务端"""
        print("File Sync Server Starting...")
        
        # 显示服务器配置
        print("Server Configuration:")
        print(f"  Monitor Directory: {self.config.monitor_dir}")
        print(f"  Bind IP: {self.config.bind_ip}")
        print(f"  Port: {self.config.port}")
        
        # 确保监控目录存在
        if not os.path.exists(self.config.monitor_dir):
            os.makedirs(self.config.monitor_dir)
            print(f"Created monitor directory: {self.config.monitor_dir}")
        
        # 启动TCP服务器
        if not self.tcp_server.start():
            print("Failed to start TCP server")
            return False
        
        # 启动文件监控器
        self.file_monitor.start()
        
        print("\nServer started successfully!")
        print("Press Ctrl+C to stop...")
        return True
    
    def stop(self):
        """停止服务端"""
        print("\nStopping server...")
        
        # 停止文件监控器
        self.file_monitor.stop()
        
        # 停止TCP服务器
        self.tcp_server.stop()
        
        print("Server stopped")

def main():
    """主函数"""
    server = FileSyncServer()
    
    try:
        if server.start():
            # 等待用户输入
            while True:
                import time
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()

if __name__ == "__main__":
    main()
