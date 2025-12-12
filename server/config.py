import configparser
import os

class Config:
    def __init__(self, config_file='server.ini'):
        self.config_file = config_file
        self.monitor_dir = ''
        self.bind_ip = ''
        self.port = 0
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
            self.monitor_dir = config.get('Server', 'MonitorDir', fallback='D:/source')
            self.bind_ip = config.get('Server', 'BindIP', fallback='0.0.0.0')
            self.port = config.getint('Server', 'Port', fallback=8080)
        except Exception as e:
            print(f"Error loading config: {e}")
            self.set_default_config()
    
    def set_default_config(self):
        """设置默认配置"""
        self.monitor_dir = 'D:/source'
        self.bind_ip = '0.0.0.0'
        self.port = 8080
        
        # 保存默认配置到文件
        config = configparser.ConfigParser()
        config['Server'] = {
            'MonitorDir': self.monitor_dir,
            'BindIP': self.bind_ip,
            'Port': str(self.port)
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        
        print(f"Default config saved to {self.config_file}")
