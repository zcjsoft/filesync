# Python轻量化文件同步程序

一个基于Python开发的轻量化文件同步程序，支持实时监控、增量同步和跨平台使用。经过优化后，特别适合处理大量文件的同步场景。

## 功能特性

### 服务端功能
- 实时监控指定目录（包括所有子目录）的变动情况
- 当监控目录发生变动时，立即向已连接的客户端发送详细的变动信息
- 程序启动后，在控制台显示当前服务器IP连接地址、监控目录路径等基本运行信息
- 监控目录发生变动时，实时在控制台输出变动详情

### 客户端功能（优化版）
- **并发同步**：支持多线程并发同步，大幅提高大量文件同步效率
- **智能增量**：自动检测文件差异，只同步有变化的文件
- **进度显示**：实时显示同步进度和统计信息
- **错误恢复**：单个文件同步失败不影响其他文件同步
- **内存优化**：流式处理大文件，避免内存溢出问题
- 接收服务端发送的变动信息，并立即执行同步操作
- 确保客户端目标目录与服务端监控目录的文件结构和内容完全一致
- 支持完整复制目录结构和准确传输文件内容

### 配置与运行
- 服务端通过`server.ini`配置文件进行参数设置
- 客户端通过`client.ini`配置文件进行参数设置，支持并发线程数配置
- 支持通过命令行参数进行交互运行，无需图形用户界面(UI)
- 配置文件包含IP地址、端口号、监控/目标目录路径等必要参数

### 性能优化特性
- **高并发处理**：支持同时处理多个文件同步任务
- **智能文件比较**：基于修改时间和文件大小的高效差异检测
- **进度可视化**：实时显示同步进度，包括文件数量和大文件传输进度
- **资源管理**：可配置的并发线程数，避免系统资源过度消耗
- **容错机制**：完善的错误处理和恢复机制

### 兼容性要求
- 完全支持中文目录和中文文件名
- 完全支持包含空格的目录名和文件名
- 支持Windows、Linux、macOS等多种操作系统

### 性能要求（已优化）
- 程序满足轻量化要求，最小化内存占用和CPU资源消耗
- 同步操作高效执行，避免不必要的网络传输和磁盘I/O操作
- **支持大量文件同步**：经过优化，可高效处理数千个文件的同步场景
- **大文件处理**：流式传输大文件，支持GB级别文件的稳定同步
- **并发性能**：默认5个并发线程，可根据系统配置调整

## 技术栈

- **开发语言**：Python 3.8+
- **文件监控**：`watchdog` - 跨平台文件系统监控库
- **网络通信**：`socket` - Python标准库
- **配置管理**：`configparser` - Python标准库
- **文件操作**：`os`、`shutil`、`pathlib` - Python标准库

## 安装方法

### 1. 安装Python

确保你的系统中已安装Python 3.8或更高版本。你可以从[Python官网](https://www.python.org/)下载并安装。

### 2. 安装依赖库

使用pip安装项目所需的依赖库：

```bash
pip install -r requirements.txt
```

## 配置文件说明

### 服务端配置文件（server.ini）

```ini
[Server]
MonitorDir = D:/source      # 要监控的目录
BindIP = 0.0.0.0            # 绑定的IP地址，0.0.0.0表示监听所有网卡
Port = 8080                 # 服务端监听的端口
```

### 客户端配置文件（client.ini）

```ini
[Client]
ServerIP = 127.0.0.1        # 服务端IP地址
ServerPort = 8080           # 服务端端口
TargetDir = D:/target        # 客户端同步目标目录
ServerRoot = D:/source       # 服务端的根目录，用于计算相对路径
SyncMode = incremental       # 同步模式：incremental（增量）或 full（全量）
MaxWorkers = 5              # 并发工作线程数（1-20，根据系统性能调整）
```

**配置说明：**
- **SyncMode**: 
  - `incremental`（默认）：只同步有变化的文件，适合日常使用
  - `full`：全量同步所有文件，适合首次同步或需要强制更新的场景
- **MaxWorkers**: 并发线程数，建议根据CPU核心数设置，默认5适合大多数场景

## 使用方法

### 启动服务端

```bash
cd server
python main.py
```

### 启动客户端

```bash
cd client
python main.py
```

### 同步模式说明

#### 1. 增量同步模式（默认）
- 自动检测文件差异，只同步有变化的文件
- 显示扫描进度和差异文件数量
- 适合日常使用，节省时间和资源

**输出示例：**
```
Starting incremental sync (diff compare) from D:/source to D:/target
Scanning files for differences...
Found 1500 files to check
250 files need synchronization
Starting incremental sync...
Incremental sync: 125/250 (50.0%)
Incremental sync completed in 45.23 seconds
Results: 248 synced, 2 failed, 1250 skipped
```

#### 2. 全量同步模式
- 强制同步所有文件，无论是否有变化
- 适合首次同步或需要强制更新的场景
- 显示详细的同步进度和统计信息

**输出示例：**
```
Starting full sync from D:/source to D:/target
Scanning files...
Found 1500 files to sync
Starting concurrent sync...
Full sync: 750/1500 (50.0%)
Full sync completed in 120.45 seconds
Results: 1498 synced, 2 failed
```

#### 3. 大文件同步
- 对于大于1MB的文件，显示详细的传输进度
- 流式传输避免内存问题
- 支持GB级别大文件的稳定同步

**输出示例：**
```
Copying large_file.zip: 125.3MB/512.0MB (24.5%)
Copying large_file.zip: 256.0MB/512.0MB (50.0%)
Copying large_file.zip: 512.0MB/512.0MB (100.0%)
Modified: D:/target/large_file.zip
```

## 项目结构

```
file_sync/
├── server/                 # 服务端代码
│   ├── main.py             # 服务端入口
│   ├── file_monitor.py     # 文件监控模块
│   ├── tcp_server.py       # TCP服务器模块
│   └── config.py           # 配置管理模块
├── client/                 # 客户端代码
│   ├── main.py             # 客户端入口
│   ├── tcp_client.py       # TCP客户端模块
│   ├── file_sync.py        # 文件同步模块
│   └── config.py           # 配置管理模块
├── server.ini              # 服务端配置文件
├── client.ini              # 客户端配置文件
├── requirements.txt        # 依赖库列表
└── README.md               # 项目说明文档
```

## 通信协议

服务端和客户端之间使用简单的文本协议进行通信，每行一条命令：

- 格式：`操作类型|文件路径|可选参数`
- 操作类型：CREATE, MODIFY, DELETE, RENAME
- 示例：
  - 创建文件：`CREATE|D:/source/file.txt`
  - 修改文件：`MODIFY|D:/source/file.txt`
  - 删除文件：`DELETE|D:/source/file.txt`
  - 重命名文件：`RENAME|D:/source/old.txt|D:/source/new.txt`

## 注意事项

1. 确保服务端和客户端的配置文件中的路径格式正确，特别是在Windows系统中，路径分隔符使用`/`或`\\`均可。
2. 确保服务端和客户端的`ServerRoot`配置项一致，否则可能导致路径计算错误。
3. 对于大文件同步，可能需要较长时间，请耐心等待。
4. 如果客户端连接断开，客户端会自动尝试重连，无需手动干预。
5. 建议在首次使用时，确保目标目录为空，以避免文件冲突。

## 故障排除

### 常见问题

1. **服务端无法启动**：
   - 检查端口是否被占用
   - 检查监控目录是否存在且有读写权限
   - 检查配置文件格式是否正确

2. **客户端无法连接到服务端**：
   - 检查服务端是否已启动
   - 检查服务端IP和端口是否配置正确
   - 检查网络连接是否正常
   - 检查防火墙设置，确保端口开放

3. **文件同步失败**：
   - 检查源文件是否存在且有读写权限
   - 检查目标目录是否有读写权限
   - 检查文件路径是否包含特殊字符

### 性能优化建议

1. **调整并发线程数**：
   - 对于CPU密集型系统，建议设置 `MaxWorkers = CPU核心数`
   - 对于I/O密集型系统，建议设置 `MaxWorkers = CPU核心数 * 2`
   - 默认值5适合大多数场景，可根据实际性能调整

2. **处理大量文件**：
   - 首次同步建议使用全量模式
   - 日常同步使用增量模式提高效率
   - 定期清理不需要同步的文件，减少扫描时间

3. **大文件优化**：
   - 程序已优化大文件处理，无需额外配置
   - 对于超大文件（>10GB），建议单独处理
   - 确保磁盘有足够空间存储同步文件

4. **内存管理**：
   - 程序使用流式传输，内存占用稳定
   - 如果遇到内存问题，可降低 `MaxWorkers` 值
   - 确保系统有足够内存处理文件操作

## 扩展建议

1. 添加文件校验功能，确保同步的文件内容一致性
2. 实现断点续传功能，提高大文件同步效率
3. 添加日志持久化功能，方便查看历史同步记录
4. 实现Web管理界面，方便远程配置和监控
5. 添加用户认证机制，提高安全性

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request，共同改进项目。

## 联系方式

如有问题或建议，请通过GitHub Issues联系我们。
