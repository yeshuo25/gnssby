#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFTP downloader for GNSSBY.
"""

import logging
import paramiko

from gnssby.core.downloader import BaseDownloader


class SFTPDownloader(BaseDownloader):
    """
    SFTP/SSH protocol downloader.

    Uses paramiko library for SFTP connections.
    """

    def __init__(self, config_manager, ac_name):
        """
        Initialize SFTP downloader.

        Args:
            config_manager (ConfigManager): Configuration manager instance
            ac_name (str): Analysis center name
        """
        super().__init__(config_manager, ac_name)
        self.transport = None
        self.sftp = None

        # Get SFTP port (default 22)
        self.port = 22
        if self.config.has_option(ac_name, 'port'):
            self.port = int(self.config.get(ac_name, 'port'))

    def connect(self):
        """Establish SFTP connection."""
        try:
            logging.debug(f"Connecting to {self.host}:{self.port} via SFTP")

            # Create transport
            self.transport = paramiko.Transport((self.host, self.port))

            # Connect with credentials
            if self.user and self.passwd:
                logging.debug(f"Logging in as {self.user}")
                self.transport.connect(username=self.user, password=self.passwd)
            else:
                logging.debug("Logging in anonymously")
                self.transport.connect(username='anonymous', password='gnssby@gmail.com')

            # Create SFTP client
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)

            logging.info(f"Connected to {self.host} via SFTP")

        except Exception as e:
            logging.error(f"Failed to connect to {self.host}: {e}")
            raise

    def disconnect(self):
        """Close SFTP connection."""
        if self.sftp:
            try:
                self.sftp.close()
                logging.debug("SFTP client closed")
            except Exception as e:
                logging.warning(f"Error closing SFTP client: {e}")

        if self.transport:
            try:
                self.transport.close()
                logging.debug("SFTP transport closed")
            except Exception as e:
                logging.warning(f"Error closing SFTP transport: {e}")

    def list_remote_files(self, remote_path):
        """
        List files in remote SFTP directory.

        Args:
            remote_path (str): Remote directory path

        Returns:
            list: List of file names

        Raises:
            Exception: If directory navigation fails
        """
        try:
            self.sftp.chdir(remote_path)
            file_list = self.sftp.listdir()
            return file_list
        except Exception as e:
            logging.error(f"Failed to list files in {remote_path}: {e}")
            raise

    def download_file(self, remote_file, local_file, remote_path=None):
        """
        Download a single file via SFTP.

        Args:
            remote_file (str): Remote file name
            local_file (str): Local file path
            remote_path (str, optional): Remote directory (SFTP already in directory)

        Returns:
            bool: True if download successful
        """
        try:
            self.sftp.get(remote_file, local_file)
            return True
        except Exception as e:
            logging.error(f"Failed to download {remote_file}: {e}")
            return False
