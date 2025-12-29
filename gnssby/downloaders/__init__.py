#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Protocol-specific downloaders for GNSSBY.
"""

from gnssby.downloaders.ftp import FTPDownloader
from gnssby.downloaders.http import HTTPDownloader
from gnssby.downloaders.https import HTTPSDownloader

__all__ = [
    'FTPDownloader',
    'HTTPDownloader',
    'HTTPSDownloader',
]

# SFTP downloader requires paramiko (optional dependency)
try:
    from gnssby.downloaders.sftp import SFTPDownloader
    __all__.append('SFTPDownloader')
except ImportError:
    SFTPDownloader = None
