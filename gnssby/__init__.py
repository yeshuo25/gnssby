#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNSSBY - GNSS Data Downloader
A Python tool for downloading GNSS data from various sources (FTP/HTTP/HTTPS/SFTP).
"""

__version__ = '2.0.0'
__author__ = 'GNSSBY Team'

from gnssby.downloaders import (
    FTPDownloader,
    HTTPDownloader,
    HTTPSDownloader,
)

__all__ = [
    'FTPDownloader',
    'HTTPDownloader',
    'HTTPSDownloader',
]

# SFTP downloader requires paramiko (optional dependency)
try:
    from gnssby.downloaders import SFTPDownloader
    __all__.append('SFTPDownloader')
except (ImportError, AttributeError):
    SFTPDownloader = None
