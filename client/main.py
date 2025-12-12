import time
from config import Config
from tcp_client import TCPClient
from file_sync import FileSync

class FileSyncClient:
    def __init__(self):
        """初始化文件同步客户端"""
        # 加载配置
        self.config = Config()
        
        # 初始化文件同步器
        self.file_sync = FileSync(
            self.config.server_root, 
            self.config.target_dir,
            self.config.max_workers
        )
        
        # 初始化TCP客户端
        self.tcp_client = TCPClient(
            self.config.server_ip, 
            self.config.server_port, 
            self.handle_message
        )
    
    def handle_message(self, message):
        """处理来自服务端的消息"""
        self.file_sync.handle_message(message)
    
    def start(self):
        """启动客户端"""
        print("File Sync Client Starting...")
        
        # 显示客户端配置
        print("Client Configuration:")
        print(f"  Server IP: {self.config.server_ip}")
        print(f"  Server Port: {self.config.server_port}")
        print(f"  Target Directory: {self.config.target_dir}")
        print(f"  Server Root Directory: {self.config.server_root}")
        print(f"  Sync Mode: {self.config.sync_mode}")
        
        # 确保目标目录存在
        import os
        if not os.path.exists(self.config.target_dir):
            os.makedirs(self.config.target_dir)
            print(f"Created target directory: {self.config.target_dir}")
        
        # 根据同步模式执行不同的同步操作
        if self.config.sync_mode == 'full':
            print("\nPerforming full sync...")
            self.file_sync.full_sync()
        else:  # incremental mode
            print("\nPerforming incremental sync (diff compare)...")
            self.file_sync.compare_and_sync_diff()
        
        # 连接到服务端
        if self.tcp_client.connect():
            print("\nClient started successfully!")
            print("Press Ctrl+C to stop...")
            return True
        else:
            print("Failed to start client")
            return False
    
    def stop(self):
        """停止客户端"""
        print("\nStopping client...")
        
        # 断开与服务端的连接
        self.tcp_client.disconnect()
        
        print("Client stopped")

def main():
    """主函数"""
    client = FileSyncClient()
    
    try:
        if client.start():
            # 等待用户输入
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        client.stop()

if __name__ == "__main__":
    main()
