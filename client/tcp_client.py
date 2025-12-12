import socket
import threading
import time

class TCPClient:
    def __init__(self, server_ip, server_port, message_callback):
        """初始化TCP客户端"""
        self.server_ip = server_ip
        self.server_port = server_port
        self.message_callback = message_callback
        self.client_socket = None
        self.running = False
        self.receive_thread = None
        self.reconnect_thread = None
        self.is_connected = False
    
    def connect(self):
        """连接到服务端"""
        if self.running:
            return False
        
        self.running = True
        
        # 启动连接线程
        self.reconnect_thread = threading.Thread(target=self._reconnect_loop)
        self.reconnect_thread.daemon = True
        self.reconnect_thread.start()
        
        return True
    
    def disconnect(self):
        """断开与服务端的连接"""
        self.running = False
        
        # 关闭客户端套接字
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception as e:
                print(f"Error closing client socket: {e}")
        
        # 等待线程结束
        if self.receive_thread:
            self.receive_thread.join(1)
        if self.reconnect_thread:
            self.reconnect_thread.join(1)
        
        self.is_connected = False
        print("Disconnected from server")
    
    def _reconnect_loop(self):
        """重连循环：如果连接断开，自动重连"""
        while self.running:
            try:
                # 创建TCP套接字
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.settimeout(5)
                
                # 连接到服务端
                print(f"Connecting to server {self.server_ip}:{self.server_port}...")
                self.client_socket.connect((self.server_ip, self.server_port))
                self.is_connected = True
                print(f"Connected to server {self.server_ip}:{self.server_port}")
                
                # 启动接收线程
                self.receive_thread = threading.Thread(target=self._receive_messages)
                self.receive_thread.daemon = True
                self.receive_thread.start()
                
                # 连接成功，等待接收线程结束
                self.receive_thread.join()
            except Exception as e:
                if self.running:
                    print(f"Connection error: {e}")
                    self.is_connected = False
                    
                    # 重连延迟
                    print("Retrying in 3 seconds...")
                    time.sleep(3)
            
            # 重置接收线程
            self.receive_thread = None
    
    def _receive_messages(self):
        """接收服务端消息"""
        while self.running and self.is_connected:
            try:
                # 设置超时，方便退出循环
                self.client_socket.settimeout(1)
                
                # 接收数据
                buffer = b''
                while b'\n' not in buffer:
                    data = self.client_socket.recv(1024)
                    if not data:
                        raise Exception("Connection closed by server")
                    buffer += data
                
                # 处理接收到的消息
                messages = buffer.split(b'\n')
                for message in messages:
                    if message:
                        message_str = message.decode('utf-8')
                        self.message_callback(message_str)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Receive error: {e}")
                break
        
        # 连接断开
        self.is_connected = False
        
        # 关闭套接字
        try:
            self.client_socket.close()
        except Exception as e:
            print(f"Error closing client socket: {e}")
    
    def send(self, message):
        """发送消息到服务端"""
        if not self.is_connected:
            return False
        
        try:
            if not message.endswith('\n'):
                message += '\n'
            self.client_socket.sendall(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
