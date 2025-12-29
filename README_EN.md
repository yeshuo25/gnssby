# GNSSBY - GNSS Data Downloader

English | [简体中文](README.md)

GNSSBY is a powerful Python tool for downloading GNSS (Global Navigation Satellite System) data from multiple sources. Supports various protocols (FTP, HTTP, HTTPS, SFTP) and 40+ preconfigured data sources.

## ✨ Features

- 🌐 **Multi-Protocol Support**: FTP, FTP-TLS, HTTP, HTTPS, SFTP
- 📦 **40+ Data Sources**: Pre-configured analysis centers (IGS, WHU, GFZ, COD, etc.)
- 🔄 **Automated Processing**: Decompression, CRX→RNX conversion, file renaming
- ⏰ **Time Range Download**: Batch download by time period
- 📝 **Station Filtering**: Download specific stations' data
- 🔌 **Highly Extensible**: Modular architecture, easy to add new sources
- 🛡️ **Secure Authentication**: NASA Earthdata, SSH key authentication

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yeshuo25/gnssby.git
cd gnssby

# Install dependencies
pip install -r requirements.txt

# Or install via setup.py
python setup.py install
```

### Basic Usage

1. **Edit `gnssby.py` to set download parameters:**

```python
# Set time range
ts = datetime.datetime(2019, 1, 1)  # Start time
te = datetime.datetime(2019, 1, 7)  # End time

# Set analysis centers to download
AClist = ['HTTPS_RNX', 'WHU_Products', 'GFZ_Products']
```

2. **Run download:**

```bash
# Windows
python gnssby.py

# Linux
python3 gnssby.py
```

3. **Check logs:**

Download logs are saved in `log_gnssby/` directory with format: `YYYYMMDD_HH_MM_SS.txt`

## 📁 Project Structure

```
gnssby/
├── gnssby.py              # Main entry point
├── config.ini             # Linux configuration
├── config_win.ini         # Windows configuration
├── listTable.ini          # Station filter configuration
├── requirements.txt       # Python dependencies
├── setup.py              # Installation script
├── README.md             # Chinese documentation
├── README_EN.md          # English documentation
│
├── gnssby/               # Core package
│   ├── __init__.py
│   ├── core/             # Core modules
│   │   ├── __init__.py
│   │   ├── downloader.py      # Abstract base class
│   │   ├── time_utils.py      # Time conversion utilities
│   │   ├── file_utils.py      # File processing utilities
│   │   └── config_manager.py  # Configuration manager
│   │
│   └── downloaders/      # Protocol downloaders
│       ├── __init__.py
│       ├── ftp.py        # FTP/FTP-TLS
│       ├── http.py       # HTTP
│       ├── https.py      # HTTPS (NASA/SWARM support)
│       └── sftp.py       # SFTP
│
└── bin/                  # External tools
    ├── crx2rnx           # Linux CRX converter
    └── crx2rnx.exe       # Windows CRX converter
```

## ⚙️ Configuration

### Main Configuration (config.ini / config_win.ini)

Configuration files contain global settings and data source configurations:

#### Global Configuration
```ini
[global]
local_dir = /path/to/download    # Local download directory
overwrite = 0                     # 0=skip existing, 1=overwrite
```

#### Data Source Configuration Example
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

#### Configuration Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `host` | Server address | `igs.gnsswhu.cn` |
| `remote_dir` | Remote directory (with placeholders) | `/pub/data/[YYYY]/[DDD]/` |
| `lsub_dir` | Local subdirectory structure | `RNX/[YYYY]/[DDD]` |
| `file_pattern` | File matching pattern (regex) | `WUM.*\\.sp3\\.gz` |
| `ftp_type` | Protocol type | `ftp`, `tls`, `http`, `https`, `sftp` |
| `step` | Time interval (hours) | `24` (daily), `168` (weekly) |
| `file_type` | File type list (optional) | `[sp3] [clk]` |
| `rename_pattern` | Rename pattern (optional) | `[sp3] [clk]` |
| `decompression` | Auto decompress | `0`=no, `1`=yes |
| `crx2rnx` | CRX→RNX conversion | `0`=no, `1`=yes |
| `rename` | Rename template (optional) | `[SITE][WD].[sp3]` |
| `user` / `passwd` | Authentication (optional) | - |
| `port` | Port number (SFTP) | `22` |

#### Time Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `[YYYY]` | 4-digit year | `2019` |
| `[YY]` | 2-digit year | `19` |
| `[DDD]` | 3-digit day of year | `001` |
| `[DAY]` | 2-digit day | `15` |
| `[MONTH]` | 2-digit month | `01` |
| `[HOUR]` | 2-digit hour | `12` |
| `[WEEK]` | 4-digit GPS week | `2034` |
| `[WOD]` | GPS day of week | `02` |
| `[WD]` | GPS day (wwwwd) | `20342` |
| `[SITE]` | Station name (uppercase) | `WUH2` |
| `[site]` | Station name (lowercase) | `wuh2` |
| `[file_type]` | File type | `sp3`, `clk` |

### Station Filter (listTable.ini)

Control downloading specific stations:

```ini
[GA_RNX]
ALIC
DARW
TOW2
# ... more stations
```

- If station list configured, only download listed stations
- If section is empty, download all files
- If no section exists, download all files

## 📡 Supported Protocols

### FTP / FTP-TLS
- Standard FTP protocol
- TLS encryption support (FTPS)
- Anonymous and authenticated access
- Special handling: iGMAS FTP (PORT mode)

### HTTP
- Standard HTTP protocol
- File listing via HTML parsing
- Works with most HTTP file servers

### HTTPS
Supports three modes:
- **Standard Mode**: Regular HTTPS download
- **NASA Mode**: NASA Earthdata authentication (for CDDIS)
- **SWARM Mode**: ESA SWARM satellite data special handling

### SFTP
- SSH File Transfer Protocol
- Password and key authentication
- Secure and reliable transfer

## 🌍 Pre-configured Data Sources (Partial List)

- **IGS Data Centers**: CDDIS, WHU, GFZ, COD, ESA, etc.
- **GNSS Products**: Precise ephemeris, clock, DCB, SNX, etc.
- **LEO Satellites**: GRACE, GRACE-FO, SWARM
- **COSMIC Data**: UCAR radio occultation data
- More sources being added continuously...

## 🔧 Development Guide

### Adding New Data Sources

GNSSBY uses modular architecture, making it easy to add new sources:

#### Method 1: Via Configuration (Recommended)

If the new source uses supported protocols, just add a new section in config:

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

Then add to `AClist` in `gnssby.py`:
```python
AClist = ['MY_NEW_SOURCE']
```

#### Method 2: Custom Downloader

For special download logic, create a custom downloader:

1. **Create new downloader class** `gnssby/downloaders/custom.py`:

```python
from gnssby.core.downloader import BaseDownloader

class CustomDownloader(BaseDownloader):
    def connect(self):
        # Implement connection logic
        pass

    def disconnect(self):
        # Implement disconnection logic
        pass

    def list_remote_files(self, remote_path):
        # Implement file listing
        pass

    def download_file(self, remote_file, local_file, remote_path=None):
        # Implement file download
        pass
```

2. **Register in `gnssby.py`**:

```python
from gnssby.downloaders.custom import CustomDownloader

def get_downloader(config_manager, ac_name):
    # ... other code ...
    elif ftp_type == 'custom':
        return CustomDownloader(config_manager, ac_name)
```

### Architecture Overview

GNSSBY uses **Object-Oriented Design** and **Strategy Pattern**:

```
BaseDownloader (Abstract Base Class)
    ├── Common download logic (time loop, filtering, post-processing)
    ├── Abstract methods (connect, disconnect, list_files, download_file)
    └── Extensible interface
         ├── FTPDownloader      (FTP/TLS implementation)
         ├── HTTPDownloader     (HTTP implementation)
         ├── HTTPSDownloader    (HTTPS, multi-mode)
         ├── SFTPDownloader     (SFTP implementation)
         └── YourDownloader     (Your custom implementation)
```

**Core Advantages**:
- ✅ 80% code reuse (common logic in base class)
- ✅ New protocols only need 4 methods
- ✅ Configuration-driven, no code modification needed
- ✅ Easy to test and maintain

## 📝 Usage Examples

### Example 1: Download IGS Precise Ephemeris

```python
ts = datetime.datetime(2019, 1, 1)
te = datetime.datetime(2019, 1, 7)
AClist = ['WHU_Products']  # Wuhan University IGS AC

# Run: python gnssby.py
# Data will be downloaded to local_dir/WHU/2019/001-007/
```

### Example 2: Multiple Data Sources

```python
ts = datetime.datetime(2019, 1, 1)
te = datetime.datetime(2019, 1, 1)
AClist = [
    'HTTPS_RNX',      # RINEX observation data
    'HTTPS_BRDM',     # Broadcast ephemeris
    'WHU_Products',   # WHU precise products
    'GFZ_Products',   # GFZ precise products
]
```

### Example 3: SWARM Satellite Data

```python
ts = datetime.datetime(2019, 1, 1)
te = datetime.datetime(2019, 1, 3)
AClist = ['swarm_RD']  # SWARM rapid data

# Automatically uses SWARM special handling
```

### Example 4: Parallel Download (Multi-process)

Due to Python GIL limitations, use multi-process approach:

```bash
# Terminal 1: Download RINEX
python gnssby.py    # AClist = ['HTTPS_RNX']

# Terminal 2: Download precise products
python gnssby.py    # AClist = ['WHU_Products', 'GFZ_Products']

# Terminal 3: Download LEO data
python gnssby.py    # AClist = ['grace-fo', 'swarm_RD']
```

## 🐛 Troubleshooting

### 1. Download Failure?

Check log file `log_gnssby/YYYYMMDD_HH_MM_SS.txt` for detailed error information.

### 2. Configure NASA Earthdata Authentication?

Add to configuration file:
```ini
[CDDIS_AC]
host = https://cddis.nasa.gov
nasa_user = your_username
nasa_passwd = your_password
ftp_type = https
```

Register account: https://urs.earthdata.nasa.gov/users/new

### 3. SFTP Connection Failed?

Verify:
- Server address and port are correct
- Username and password are correct
- Firewall allows connection
- paramiko is installed: `pip install paramiko`

### 4. Re-download Existing Files?

Set `overwrite = 1` in `config.ini`

### 5. Download Specific Stations Only?

Edit `listTable.ini`, list station names in corresponding AC section.

## 📜 Changelog

### v2.0.0 (Current)
- ✨ Complete refactor: Modular OOP architecture
- ✨ New: HTTPS SWARM mode support
- ✨ Improved: Configuration manager encapsulation
- ✨ Fixed: Multiple known bugs (typo, undefined functions)
- ✨ New: Complete bilingual documentation
- ✨ New: requirements.txt and setup.py
- ✨ Improved: 80% increase in code reuse

### v1.0.0
- Initial release
- Support FTP, HTTP, HTTPS, SFTP protocols
- 40+ pre-configured data sources

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork this repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add some feature'`
4. Push branch: `git push origin feature/your-feature`
5. Submit Pull Request

## 📄 License

This project is licensed under [MIT License](LICENSE)

## 👥 Authors

GNSSBY Team

## 📧 Contact

- Issues: https://github.com/yeshuo25/gnssby/issues
- Email: gnssby@gmail.com

## 🙏 Acknowledgments

Thanks to all analysis centers and organizations providing GNSS data:
- IGS (International GNSS Service)
- Data centers: CDDIS, WHU, GFZ, COD, ESA, etc.
- Research institutions: UCAR, NASA, ESA, etc.

---

**⭐ If this project helps you, please give it a Star!**
