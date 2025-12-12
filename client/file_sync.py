import os
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import queue

class FileSync:
    def __init__(self, server_root, target_dir, max_workers=5):
        """初始化文件同步器"""
        self.server_root = server_root
        self.target_dir = target_dir
        self.max_workers = max_workers
        
        # 同步统计信息
        self.sync_stats = {
            'total_files': 0,
            'synced_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'start_time': None,
            'end_time': None
        }
        
        # 确保目标目录存在
        os.makedirs(self.target_dir, exist_ok=True)
    
    def _get_all_files(self, directory):
        """高效获取目录下的所有文件列表"""
        file_list = []
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_list.append(file_path)
        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")
        return file_list
    
    def _sync_file_worker(self, file_path, operation="create"):
        """单个文件同步的工作函数"""
        try:
            if operation == "create":
                result = self.sync_create(file_path)
            else:
                result = self.sync_modify(file_path)
            
            if result:
                return (file_path, True, None)
            else:
                return (file_path, False, "Sync operation failed")
        except Exception as e:
            return (file_path, False, str(e))
    
    def _update_progress(self, current, total, operation="Syncing"):
        """更新进度显示"""
        if total > 0:
            percentage = (current / total) * 100
            print(f"\r{operation}: {current}/{total} ({percentage:.1f}%)", end="", flush=True)
    
    def full_sync(self):
        """执行全量同步：将服务端监控目录的所有文件同步到客户端目标目录"""
        print(f"Starting full sync from {self.server_root} to {self.target_dir}")
        
        # 重置统计信息
        self.sync_stats = {
            'total_files': 0,
            'synced_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'start_time': time.time(),
            'end_time': None
        }
        
        try:
            # 获取所有文件列表
            print("Scanning files...")
            all_files = self._get_all_files(self.server_root)
            self.sync_stats['total_files'] = len(all_files)
            
            if not all_files:
                print("No files found to sync")
                return True
            
            print(f"Found {len(all_files)} files to sync")
            print("Starting concurrent sync...")
            
            # 使用线程池进行并发同步
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交所有同步任务
                future_to_file = {
                    executor.submit(self._sync_file_worker, file_path, "create"): file_path 
                    for file_path in all_files
                }
                
                # 处理完成的任务
                completed = 0
                for future in as_completed(future_to_file):
                    file_path, success, error = future.result()
                    completed += 1
                    
                    if success:
                        self.sync_stats['synced_files'] += 1
                    else:
                        self.sync_stats['failed_files'] += 1
                        print(f"\nFailed to sync {file_path}: {error}")
                    
                    # 更新进度
                    self._update_progress(completed, len(all_files), "Full sync")
            
            # 完成进度显示
            print()
            self.sync_stats['end_time'] = time.time()
            
            # 显示同步结果
            duration = self.sync_stats['end_time'] - self.sync_stats['start_time']
            print(f"Full sync completed in {duration:.2f} seconds")
            print(f"Results: {self.sync_stats['synced_files']} synced, "
                  f"{self.sync_stats['failed_files']} failed")
            
            return self.sync_stats['failed_files'] == 0
        except Exception as e:
            print(f"\nFailed to perform full sync: {e}")
            return False
    
    def _need_sync(self, server_path, target_path):
        """检查文件是否需要同步"""
        try:
            # 如果目标文件不存在，需要同步
            if not os.path.exists(target_path):
                return True
            
            # 比较文件的修改时间和大小
            server_stat = os.stat(server_path)
            target_stat = os.stat(target_path)
            
            # 如果修改时间或大小不同，需要同步
            if server_stat.st_mtime != target_stat.st_mtime or server_stat.st_size != target_stat.st_size:
                return True
            
            return False
        except Exception as e:
            # 如果无法获取文件状态，认为需要同步
            print(f"Error checking sync need for {server_path}: {e}")
            return True
    
    def compare_and_sync_diff(self):
        """执行差异对比和增量同步：只同步服务端和客户端有差异的文件"""
        print(f"Starting incremental sync (diff compare) from {self.server_root} to {self.target_dir}")
        
        # 重置统计信息
        self.sync_stats = {
            'total_files': 0,
            'synced_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'start_time': time.time(),
            'end_time': None
        }
        
        try:
            # 获取所有文件列表
            print("Scanning files for differences...")
            all_files = self._get_all_files(self.server_root)
            self.sync_stats['total_files'] = len(all_files)
            
            if not all_files:
                print("No files found to sync")
                return True
            
            print(f"Found {len(all_files)} files to check")
            
            # 筛选需要同步的文件
            files_to_sync = []
            for file_path in all_files:
                target_path = self.get_target_path(file_path)
                if self._need_sync(file_path, target_path):
                    files_to_sync.append(file_path)
                else:
                    self.sync_stats['skipped_files'] += 1
            
            print(f"{len(files_to_sync)} files need synchronization")
            
            if not files_to_sync:
                print("All files are up to date")
                return True
            
            print("Starting incremental sync...")
            
            # 使用线程池进行并发同步
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交所有同步任务
                future_to_file = {
                    executor.submit(self._sync_file_worker, file_path, "modify"): file_path 
                    for file_path in files_to_sync
                }
                
                # 处理完成的任务
                completed = 0
                for future in as_completed(future_to_file):
                    file_path, success, error = future.result()
                    completed += 1
                    
                    if success:
                        self.sync_stats['synced_files'] += 1
                    else:
                        self.sync_stats['failed_files'] += 1
                        print(f"\nFailed to sync {file_path}: {error}")
                    
                    # 更新进度
                    self._update_progress(completed, len(files_to_sync), "Incremental sync")
            
            # 完成进度显示
            print()
            self.sync_stats['end_time'] = time.time()
            
            # 显示同步结果
            duration = self.sync_stats['end_time'] - self.sync_stats['start_time']
            print(f"Incremental sync completed in {duration:.2f} seconds")
            print(f"Results: {self.sync_stats['synced_files']} synced, "
                  f"{self.sync_stats['failed_files']} failed, "
                  f"{self.sync_stats['skipped_files']} skipped")
            
            return self.sync_stats['failed_files'] == 0
        except Exception as e:
            print(f"\nFailed to perform incremental sync: {e}")
            return False
    
    def get_target_path(self, server_path):
        """根据服务端路径计算客户端目标路径"""
        # 移除服务端根目录前缀
        if server_path.startswith(self.server_root):
            relative_path = server_path[len(self.server_root):]
            # 确保相对路径不包含前导斜杠
            if relative_path.startswith('\\') or relative_path.startswith('/'):
                relative_path = relative_path[1:]
        else:
            # 如果路径不包含服务端根目录，直接使用文件名
            relative_path = os.path.basename(server_path)
        
        # 构建目标路径
        target_path = os.path.join(self.target_dir, relative_path)
        
        return target_path
    
    def _copy_file_with_progress(self, src, dst, buffer_size=8192):
        """带进度显示的文件复制，避免大文件内存问题"""
        try:
            file_size = os.path.getsize(src)
            copied = 0
            
            with open(src, 'rb') as src_file:
                with open(dst, 'wb') as dst_file:
                    while True:
                        buffer = src_file.read(buffer_size)
                        if not buffer:
                            break
                        dst_file.write(buffer)
                        copied += len(buffer)
                        
                        # 显示大文件复制进度
                        if file_size > 1024 * 1024:  # 大于1MB的文件显示进度
                            percentage = (copied / file_size) * 100
                            print(f"\rCopying {os.path.basename(src)}: {copied/1024/1024:.1f}MB/{file_size/1024/1024:.1f}MB ({percentage:.1f}%)", 
                                  end="", flush=True)
            
            # 复制完成后恢复文件时间戳
            shutil.copystat(src, dst)
            
            if file_size > 1024 * 1024:
                print()  # 换行
            
            return True
        except Exception as e:
            print(f"\nError copying file {src}: {e}")
            return False
    
    def sync_create(self, server_path):
        """同步文件创建事件"""
        target_path = self.get_target_path(server_path)
        
        try:
            # 确保目标目录存在
            target_dir = os.path.dirname(target_path)
            os.makedirs(target_dir, exist_ok=True)
            
            # 检查源文件是否存在
            if not os.path.exists(server_path):
                print(f"Source file not found: {server_path}")
                return False
            
            # 使用优化的文件复制方法
            if self._copy_file_with_progress(server_path, target_path):
                print(f"Created: {target_path}")
                return True
            else:
                return False
        except Exception as e:
            print(f"Failed to create {target_path}: {e}")
            return False
    
    def sync_modify(self, server_path):
        """同步文件修改事件"""
        target_path = self.get_target_path(server_path)
        
        try:
            # 检查源文件是否存在
            if not os.path.exists(server_path):
                print(f"Source file not found: {server_path}")
                return False
            
            # 确保目标目录存在
            target_dir = os.path.dirname(target_path)
            os.makedirs(target_dir, exist_ok=True)
            
            # 使用优化的文件复制方法
            if self._copy_file_with_progress(server_path, target_path):
                print(f"Modified: {target_path}")
                return True
            else:
                return False
        except Exception as e:
            print(f"Failed to modify {target_path}: {e}")
            return False
    
    def sync_delete(self, server_path):
        """同步文件删除事件"""
        target_path = self.get_target_path(server_path)
        
        try:
            # 检查目标文件是否存在
            if not os.path.exists(target_path):
                return True  # 文件已不存在，无需处理
            
            # 删除文件
            if os.path.isfile(target_path):
                os.remove(target_path)
                print(f"Deleted: {target_path}")
            elif os.path.isdir(target_path):
                shutil.rmtree(target_path)
                print(f"Deleted directory: {target_path}")
            
            return True
        except Exception as e:
            print(f"Failed to delete {target_path}: {e}")
            return False
    
    def sync_rename(self, old_server_path, new_server_path):
        """同步文件重命名事件"""
        old_target_path = self.get_target_path(old_server_path)
        new_target_path = self.get_target_path(new_server_path)
        
        try:
            # 检查目标文件是否存在
            if not os.path.exists(old_target_path):
                # 如果旧文件不存在，可能是重命名前的文件创建事件还未同步，
                # 直接创建新文件
                return self.sync_create(new_server_path)
            
            # 确保新目标目录存在
            new_target_dir = os.path.dirname(new_target_path)
            os.makedirs(new_target_dir, exist_ok=True)
            
            # 重命名文件
            os.rename(old_target_path, new_target_path)
            print(f"Renamed: {old_target_path} -> {new_target_path}")
            return True
        except Exception as e:
            print(f"Failed to rename {old_target_path} to {new_target_path}: {e}")
            
            # 重命名失败，尝试删除旧文件并创建新文件
            try:
                self.sync_delete(old_server_path)
                return self.sync_create(new_server_path)
            except Exception as fallback_e:
                print(f"Fallback failed: {fallback_e}")
                return False
    
    def handle_message(self, message):
        """处理来自服务端的消息"""
        try:
            # 解析消息格式：事件类型|文件路径|可选旧文件路径
            parts = message.split('|')
            if len(parts) < 2:
                print(f"Invalid message format: {message}")
                return False
            
            event_type = parts[0]
            file_path = parts[1]
            old_file_path = parts[2] if len(parts) > 2 else None
            
            # 处理不同类型的事件
            if event_type == 'CREATE':
                return self.sync_create(file_path)
            elif event_type == 'MODIFY':
                return self.sync_modify(file_path)
            elif event_type == 'DELETE':
                return self.sync_delete(file_path)
            elif event_type == 'RENAME' and old_file_path:
                return self.sync_rename(old_file_path, file_path)
            else:
                print(f"Unknown event type: {event_type}")
                return False
        except Exception as e:
            print(f"Error handling message '{message}': {e}")
            return False
