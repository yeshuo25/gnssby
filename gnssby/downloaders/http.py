#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP downloader for GNSSBY.
"""

import logging
import re
import requests

from gnssby.core.downloader import BaseDownloader


class HTTPDownloader(BaseDownloader):
    """
    HTTP protocol downloader.

    Uses requests library to download files via HTTP.
    """

    def __init__(self, config_manager, ac_name):
        """
        Initialize HTTP downloader.

        Args:
            config_manager (ConfigManager): Configuration manager instance
            ac_name (str): Analysis center name
        """
        super().__init__(config_manager, ac_name)
        self.session = None

    def connect(self):
        """Establish HTTP session."""
        self.session = requests.Session()
        logging.debug("HTTP session created")

    def disconnect(self):
        """Close HTTP session."""
        if self.session:
            self.session.close()
            logging.debug("HTTP session closed")

    def list_remote_files(self, remote_path):
        """
        List files in remote HTTP directory by parsing HTML.

        Args:
            remote_path (str): Remote directory URL

        Returns:
            list: List of file names

        Raises:
            Exception: If HTTP request fails
        """
        try:
            url = self.host + remote_path
            logging.debug(f"Fetching file list from {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Parse HTML for links
            html_text = response.text
            pattern = r'<a.*?href="(.*?)">'
            sub_urls = re.findall(pattern, html_text)

            # Remove duplicates
            file_list = list(set(sub_urls))

            logging.debug(f"Found {len(file_list)} files in {url}")
            return file_list

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to list files from {url}: {e}")
            raise

    def download_file(self, remote_file, local_file, remote_path=None):
        """
        Download a single file via HTTP.

        Args:
            remote_file (str): Remote file name
            local_file (str): Local file path
            remote_path (str, optional): Remote directory URL

        Returns:
            bool: True if download successful
        """
        try:
            if remote_path:
                url = self.host + remote_path + '/' + remote_file
            else:
                url = self.host + '/' + remote_file

            logging.debug(f"Downloading from {url}")

            response = self.session.get(url, stream=True, timeout=120)
            response.raise_for_status()

            # Write to file
            with open(local_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            return True

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to download {remote_file}: {e}")
            return False
