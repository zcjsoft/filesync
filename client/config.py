import configparser
import os

class Config:
    def __init__(self, config_file='client.ini'):
        self.config_file = config_file
        self.server_ip = ''
        self.server_port = 0
        self.target_dir = ''
        self.server_root = ''
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        config = configparser.ConfigParser()
        
        # 读取配置文件
        if os.path.exists(self.config_file):
            config.read(self.config_file, encoding='utf-8')
        else:
            # 如果配置文件不存在，使用默认配置
            self.set_default_config()
            return
        
        # 解析配置
        try:
            self.server_ip = config.get('Client', 'ServerIP', fallback='127.0.0.1')
            self.server_port = config.getint('Client', 'ServerPort', fallback=8080)
            self.target_dir = config.get('Client', 'TargetDir', fallback='D:/target')
            self.server_root = config.get('Client', 'ServerRoot', fallback='D:/source')
            self.sync_mode = config.get('Client', 'SyncMode', fallback='incremental')
            self.max_workers = config.getint('Client', 'MaxWorkers', fallback=5)
        except Exception as e:
            print(f"Error loading config: {e}")
            self.set_default_config()
    
    def set_default_config(self):
        """设置默认配置"""
        self.server_ip = '127.0.0.1'
        self.server_port = 8080
        self.target_dir = 'D:/target'
        self.server_root = 'D:/source'
        self.sync_mode = 'incremental'  # 同步模式：incremental（增量）或 full（全量）
        self.max_workers = 5  # 并发工作线程数
        
        # 保存默认配置到文件
        config = configparser.ConfigParser()
        config['Client'] = {
            'ServerIP': self.server_ip,
            'ServerPort': str(self.server_port),
            'TargetDir': self.target_dir,
            'ServerRoot': self.server_root,
            'SyncMode': self.sync_mode,
            'MaxWorkers': str(self.max_workers)
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        
        print(f"Default config saved to {self.config_file}")
