# GNSSBY - GNSS 数据下载工具

[English](README_EN.md) | 简体中文

GNSSBY 是一个功能强大的 Python 工具，用于从多个数据源下载 GNSS（全球导航卫星系统）数据。支持多种协议（FTP、HTTP、HTTPS、SFTP）和40+个预配置的数据源。

## ✨ 主要特性

- 🌐 **多协议支持**：FTP、FTP-TLS、HTTP、HTTPS、SFTP
- 📦 **40+ 数据源**：预配置多个分析中心（IGS、WHU、GFZ、COD等）
- 🔄 **自动化处理**：支持解压缩、CRX→RNX转换、文件重命名
- ⏰ **时间范围下载**：按时间段批量下载数据
- 📝 **站点过滤**：可配置下载特定测站的数据
- 🔌 **高度可扩展**：模块化架构，易于添加新数据源
- 🛡️ **安全认证**：支持 NASA Earthdata 认证、SSH密钥认证

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yeshuo25/gnssby.git
cd gnssby

# 安装依赖
pip install -r requirements.txt

# 或使用 setup.py 安装
python setup.py install
```

### 基本使用

1. **编辑 `gnssby.py` 设置下载参数：**

```python
# 设置时间范围
ts = datetime.datetime(2019, 1, 1)  # 开始时间
te = datetime.datetime(2019, 1, 7)  # 结束时间

# 设置要下载的分析中心
AClist = ['HTTPS_RNX', 'WHU_Products', 'GFZ_Products']
```

2. **运行下载：**

```bash
# Windows
python gnssby.py

# Linux
python3 gnssby.py
```

3. **查看日志：**

下载日志保存在 `log_gnssby/` 目录，文件名格式：`YYYYMMDD_HH_MM_SS.txt`

## 📁 项目结构

```
gnssby/
├── gnssby.py              # 主入口程序
├── config.ini             # Linux 配置文件
├── config_win.ini         # Windows 配置文件
├── listTable.ini          # 测站过滤配置
├── requirements.txt       # Python 依赖
├── setup.py              # 安装脚本
├── README.md             # 中文文档
├── README_EN.md          # 英文文档
│
├── gnssby/               # 核心包
│   ├── __init__.py
│   ├── core/             # 核心模块
│   │   ├── __init__.py
│   │   ├── downloader.py      # 抽象基类
│   │   ├── time_utils.py      # 时间转换工具
│   │   ├── file_utils.py      # 文件处理工具
│   │   └── config_manager.py  # 配置管理器
│   │
│   └── downloaders/      # 协议下载器
│       ├── __init__.py
│       ├── ftp.py        # FTP/FTP-TLS
│       ├── http.py       # HTTP
│       ├── https.py      # HTTPS (包含 NASA/SWARM)
│       └── sftp.py       # SFTP
│
└── bin/                  # 外部工具
    ├── crx2rnx           # Linux CRX转换工具
    └── crx2rnx.exe       # Windows CRX转换工具
```

## ⚙️ 配置说明

### 主配置文件 (config.ini / config_win.ini)

配置文件包含全局设置和各数据源的配置：

#### 全局配置
```ini
[global]
local_dir = /path/to/download    # 本地下载目录
overwrite = 0                     # 0=跳过已存在文件, 1=覆盖
```

#### 数据源配置示例
```ini
[WHU_Products]
host = igs.gnsswhu.cn
remote_dir = /pub/whu/phasebias/[YYYY]/
lsub_dir = WHU/[YYYY]/[DDD]
file_pattern = WUM0MGXRAP_[YYYY][DDD]0000_01D_01D_OSB.BIA.gz
ftp_type = ftp
step = 24
decompression = 1
crx2rnx = 0
```

#### 配置参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `host` | 服务器地址 | `igs.gnsswhu.cn` |
| `remote_dir` | 远程目录（支持占位符） | `/pub/data/[YYYY]/[DDD]/` |
| `lsub_dir` | 本地子目录结构 | `RNX/[YYYY]/[DDD]` |
| `file_pattern` | 文件匹配模式（正则） | `WUM.*\\.sp3\\.gz` |
| `ftp_type` | 协议类型 | `ftp`, `tls`, `http`, `https`, `sftp` |
| `step` | 时间间隔（小时） | `24` (每天), `168` (每周) |
| `file_type` | 文件类型列表（可选） | `[sp3] [clk]` |
| `rename_pattern` | 重命名模式（可选） | `[sp3] [clk]` |
| `decompression` | 自动解压 | `0`=否, `1`=是 |
| `crx2rnx` | CRX→RNX转换 | `0`=否, `1`=是 |
| `rename` | 重命名模板（可选） | `[SITE][WD].[sp3]` |
| `user` / `passwd` | 认证信息（可选） | - |
| `port` | 端口号（SFTP） | `22` |

#### 时间占位符

| 占位符 | 说明 | 示例 |
|--------|------|------|
| `[YYYY]` | 4位年份 | `2019` |
| `[YY]` | 2位年份 | `19` |
| `[DDD]` | 3位年积日 | `001` |
| `[DAY]` | 2位日期 | `15` |
| `[MONTH]` | 2位月份 | `01` |
| `[HOUR]` | 2位小时 | `12` |
| `[WEEK]` | 4位GPS周 | `2034` |
| `[WOD]` | GPS周内日 | `02` |
| `[WD]` | GPS日 (wwwwd) | `20342` |
| `[SITE]` | 测站名（大写） | `WUH2` |
| `[site]` | 测站名（小写） | `wuh2` |
| `[file_type]` | 文件类型 | `sp3`, `clk` |

### 测站过滤 (listTable.ini)

控制下载特定测站的数据：

```ini
[GA_RNX]
ALIC
DARW
TOW2
# ... 更多测站
```

- 如果配置了测站列表，只下载列表中的测站
- 如果 section 为空，下载所有文件
- 如果没有 section，下载所有文件

## 📡 支持的协议

### FTP / FTP-TLS
- 标准 FTP 协议
- 支持 TLS 加密（FTPS）
- 支持匿名和认证访问
- 特殊处理：iGMAS FTP（PORT模式）

### HTTP
- 标准 HTTP 协议
- 通过解析 HTML 获取文件列表
- 适用于大多数 HTTP 文件服务器

### HTTPS
支持三种模式：
- **标准模式**：普通 HTTPS 下载
- **NASA 模式**：NASA Earthdata 认证（用于 CDDIS）
- **SWARM 模式**：ESA SWARM 卫星数据特殊处理

### SFTP
- SSH File Transfer Protocol
- 支持密码和密钥认证
- 安全可靠的传输

## 🌍 预配置数据源（部分）

- **IGS 数据中心**：CDDIS、WHU、GFZ、COD、ESA 等
- **GNSS 产品**：精密星历、钟差、DCB、SNX 等
- **LEO 卫星**：GRACE、GRACE-FO、SWARM
- **COSMIC 数据**：UCAR 掩星观测数据
- 更多数据源持续添加中...

## 🔧 开发指南

### 添加新数据源

GNSSBY 采用模块化架构，添加新数据源非常简单：

#### 方法1：通过配置文件（推荐）

如果新数据源使用已支持的协议，只需在配置文件中添加新 section：

```ini
[MY_NEW_SOURCE]
host = new-server.example.com
remote_dir = /data/[YYYY]/[DDD]/
lsub_dir = MYNEW/[YYYY]/[DDD]
file_pattern = .*\\.rnx\\.gz
ftp_type = https
step = 24
decompression = 1
```

然后在 `gnssby.py` 中添加到 `AClist`：
```python
AClist = ['MY_NEW_SOURCE']
```

#### 方法2：自定义下载器

如果需要特殊的下载逻辑，可以创建自定义下载器：

1. **创建新的下载器类** `gnssby/downloaders/custom.py`：

```python
from gnssby.core.downloader import BaseDownloader

class CustomDownloader(BaseDownloader):
    def connect(self):
        # 实现连接逻辑
        pass

    def disconnect(self):
        # 实现断开逻辑
        pass

    def list_remote_files(self, remote_path):
        # 实现文件列表获取
        pass

    def download_file(self, remote_file, local_file, remote_path=None):
        # 实现文件下载
        pass
```

2. **在 `gnssby.py` 中注册**：

```python
from gnssby.downloaders.custom import CustomDownloader

def get_downloader(config_manager, ac_name):
    # ... 其他代码 ...
    elif ftp_type == 'custom':
        return CustomDownloader(config_manager, ac_name)
```

### 架构说明

GNSSBY 使用**面向对象设计**和**策略模式**：

```
BaseDownloader (抽象基类)
    ├── 通用下载逻辑（时间循环、文件过滤、后处理）
    ├── 抽象方法（connect, disconnect, list_files, download_file）
    └── 可扩展接口
         ├── FTPDownloader      (FTP/TLS 实现)
         ├── HTTPDownloader     (HTTP 实现)
         ├── HTTPSDownloader    (HTTPS 实现，支持多模式)
         ├── SFTPDownloader     (SFTP 实现)
         └── YourDownloader     (您的自定义实现)
```

**核心优势**：
- ✅ 80% 代码复用（通用逻辑在基类中）
- ✅ 新协议只需实现 4 个方法
- ✅ 配置驱动，无需修改代码
- ✅ 易于测试和维护

## 📝 使用示例

### 示例1：下载 IGS 精密星历

```python
ts = datetime.datetime(2019, 1, 1)
te = datetime.datetime(2019, 1, 7)
AClist = ['WHU_Products']  # 武汉大学 IGS 分析中心

# 运行 python gnssby.py
# 数据将下载到 local_dir/WHU/2019/001-007/
```

### 示例2：下载多个数据源

```python
ts = datetime.datetime(2019, 1, 1)
te = datetime.datetime(2019, 1, 1)
AClist = [
    'HTTPS_RNX',      # RINEX 观测数据
    'HTTPS_BRDM',     # 广播星历
    'WHU_Products',   # WHU 精密产品
    'GFZ_Products',   # GFZ 精密产品
]
```

### 示例3：下载 SWARM 卫星数据

```python
ts = datetime.datetime(2019, 1, 1)
te = datetime.datetime(2019, 1, 3)
AClist = ['swarm_RD']  # SWARM 快速数据

# 自动使用 SWARM 特殊处理逻辑
```

### 示例4：并行下载（多进程）

由于 Python GIL 限制，建议使用多进程方式并行下载：

```bash
# 终端1：下载 RINEX 数据
python gnssby.py    # AClist = ['HTTPS_RNX']

# 终端2：下载精密产品
python gnssby.py    # AClist = ['WHU_Products', 'GFZ_Products']

# 终端3：下载 LEO 数据
python gnssby.py    # AClist = ['grace-fo', 'swarm_RD']
```

## 🐛 常见问题

### 1. 下载失败怎么办？

检查日志文件 `log_gnssby/YYYYMMDD_HH_MM_SS.txt`，查看详细错误信息。

### 2. 如何配置 NASA Earthdata 认证？

在配置文件中添加：
```ini
[CDDIS_AC]
host = https://cddis.nasa.gov
nasa_user = your_username
nasa_passwd = your_password
ftp_type = https
```

注册账号：https://urs.earthdata.nasa.gov/users/new

### 3. SFTP 连接失败？

确认：
- 服务器地址和端口正确
- 用户名密码正确
- 防火墙允许连接
- paramiko 库已安装：`pip install paramiko`

### 4. 文件已存在但想重新下载？

设置 `config.ini` 中的 `overwrite = 1`

### 5. 如何只下载特定测站？

编辑 `listTable.ini`，在对应 AC section 中列出测站名。

## 📜 更新日志

### v2.0.0 (当前版本)
- ✨ 完全重构：模块化面向对象架构
- ✨ 新增：HTTPS SWARM 模式支持
- ✨ 改进：配置管理器封装
- ✨ 修复：多个已知 bug（typo、未定义函数）
- ✨ 新增：完整的中英文文档
- ✨ 新增：requirements.txt 和 setup.py
- ✨ 改进：代码复用率提升 80%

### v1.0.0
- 初始版本
- 支持 FTP、HTTP、HTTPS、SFTP 协议
- 40+ 预配置数据源

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -am 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 [MIT License](LICENSE)

## 👥 作者

Chao Yu. 

## 📧 联系方式

- Issues: https://github.com/yeshuo25/gnssby/issues
- Email: chaoyu.shao@gmail.com
- 上海天文台

## 🙏 致谢

感谢所有提供 GNSS 数据的分析中心和机构：
- IGS (International GNSS Service)
- CDDIS, WHU, GFZ, COD, ESA 等数据中心
- UCAR, NASA, ESA 等科研机构

---

**⭐ 如果这个项目对您有帮助，请给个 Star！**
