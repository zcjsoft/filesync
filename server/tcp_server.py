import socket
import threading
import time

class TCPServer:
    def __init__(self, host, port):
        """初始化TCP服务器"""
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.clients_lock = threading.Lock()
        self.running = False
        self.server_thread = None
    
    def start(self):
        """启动TCP服务器"""
        if self.running:
            return False
        
        try:
            # 创建TCP套接字
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # 绑定地址和端口
            self.server_socket.bind((self.host, self.port))
            
            # 开始监听
            self.server_socket.listen(5)
            self.running = True
            
            # 启动服务器线程
            self.server_thread = threading.Thread(target=self._accept_clients)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            print(f"TCP Server started on {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to start TCP server: {e}")
            return False
    
    def stop(self):
        """停止TCP服务器"""
        if not self.running:
            return
        
        self.running = False
        
        # 关闭所有客户端连接
        with self.clients_lock:
            for client in self.clients:
                try:
                    client.close()
                except Exception as e:
                    print(f"Error closing client: {e}")
            self.clients.clear()
        
        # 关闭服务器套接字
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                print(f"Error closing server socket: {e}")
        
        # 等待服务器线程结束
        if self.server_thread:
            self.server_thread.join(1)
        
        print("TCP Server stopped")
    
    def _accept_clients(self):
        """接受客户端连接"""
        while self.running:
            try:
                # 设置超时，方便退出循环
                self.server_socket.settimeout(1)
                client_socket, client_addr = self.server_socket.accept()
                
                # 添加客户端到列表
                with self.clients_lock:
                    self.clients.append(client_socket)
                
                print(f"Client connected: {client_addr}")
                
                # 启动客户端处理线程
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_addr)
                )
                client_thread.daemon = True
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error accepting client: {e}")
                break
    
    def _handle_client(self, client_socket, client_addr):
        """处理单个客户端连接"""
        while self.running:
            try:
                # 设置超时，方便退出循环
                client_socket.settimeout(1)
                
                # 接收客户端消息（实际上客户端不需要发送消息）
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                # 这里可以处理客户端消息（如果需要）
                # print(f"Received from {client_addr}: {data.decode()}")
            except socket.timeout:
                continue
            except Exception as e:
                break
        
        # 客户端断开连接
        with self.clients_lock:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
        
        try:
            client_socket.close()
        except Exception as e:
            print(f"Error closing client socket: {e}")
        
        print(f"Client disconnected: {client_addr}")
    
    def broadcast(self, message):
        """向所有客户端广播消息"""
        if not self.running:
            return
        
        # 确保消息以换行符结尾
        if not message.endswith('\n'):
            message += '\n'
        
        # 发送消息给所有客户端
        with self.clients_lock:
            for client in self.clients:
                try:
                    client.sendall(message.encode('utf-8'))
                except Exception as e:
                    print(f"Error broadcasting to client: {e}")
                    # 移除无法发送消息的客户端
                    self.clients.remove(client)
    
    def get_client_count(self):
        """获取当前连接的客户端数量"""
        with self.clients_lock:
            return len(self.clients)
