#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FTP downloader for GNSSBY.
Supports both FTP and FTP-TLS protocols.
"""

import logging
from ftplib import FTP, FTP_TLS

from gnssby.core.downloader import BaseDownloader


class FTPDownloader(BaseDownloader):
    """
    FTP/FTP-TLS protocol downloader.

    Supports:
        - Plain FTP
        - FTP with TLS encryption (explicit FTPS)
    """

    def __init__(self, config_manager, ac_name, use_tls=False):
        """
        Initialize FTP downloader.

        Args:
            config_manager (ConfigManager): Configuration manager instance
            ac_name (str): Analysis center name
            use_tls (bool, optional): Use FTP-TLS if True. Defaults to False.
        """
        super().__init__(config_manager, ac_name)
        self.use_tls = use_tls
        self.ftp = None

    def connect(self):
        """Establish FTP connection."""
        try:
            if self.use_tls:
                logging.debug(f"Connecting to {self.host} via FTP-TLS")
                self.ftp = FTP_TLS(host=self.host)
            else:
                logging.debug(f"Connecting to {self.host} via FTP")
                self.ftp = FTP(host=self.host)

            # Login
            if self.user and self.passwd:
                logging.debug(f"Logging in as {self.user}")
                self.ftp.login(user=self.user, passwd=self.passwd)
            else:
                logging.debug("Logging in anonymously")
                if self.use_tls:
                    self.ftp.login(user='anonymous', passwd='gnssby@gmail.com')
                else:
                    self.ftp.login()

            # Special handling for iGMAS FTP (port mode)
            if 'iGMAS' in self.ac_name:
                logging.debug("Detected iGMAS FTP - using PORT mode")
                self.ftp.set_pasv(False)

            # Secure data connection for FTP-TLS
            if self.use_tls:
                self.ftp.prot_p()

            logging.info(f"Connected to {self.host}")

        except Exception as e:
            logging.error(f"Failed to connect to {self.host}: {e}")
            raise

    def disconnect(self):
        """Close FTP connection."""
        if self.ftp:
            try:
                self.ftp.quit()
                logging.debug("Disconnected from FTP server")
            except Exception as e:
                logging.warning(f"Error during disconnect: {e}")

    def list_remote_files(self, remote_path):
        """
        List files in remote FTP directory.

        Args:
            remote_path (str): Remote directory path

        Returns:
            list: List of file names

        Raises:
            Exception: If directory navigation fails
        """
        try:
            self.ftp.cwd(remote_path)
            file_list = self.ftp.nlst()
            return file_list
        except Exception as e:
            logging.error(f"Failed to list files in {remote_path}: {e}")
            raise

    def download_file(self, remote_file, local_file, remote_path=None):
        """
        Download a single file via FTP.

        Args:
            remote_file (str): Remote file name
            local_file (str): Local file path
            remote_path (str, optional): Remote directory (not used, FTP already in directory)

        Returns:
            bool: True if download successful
        """
        try:
            with open(local_file, 'wb') as f:
                self.ftp.retrbinary('RETR ' + remote_file, f.write)
            return True
        except Exception as e:
            logging.error(f"Failed to download {remote_file}: {e}")
            return False
