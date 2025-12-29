#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTPS downloader for GNSSBY.
Supports NASA Earthdata authentication and SWARM special handling.
"""

import logging
import re
import os
import time
import requests

from gnssby.core.downloader import BaseDownloader
from gnssby.core.time_utils import replace_time_placeholders


class SessionWithHeaderRedirection(requests.Session):
    """
    Custom session class for NASA Earthdata authentication.

    Reference:
        https://urs.earthdata.nasa.gov/documentation/for_users/data_access/python
    """

    AUTH_HOST = 'urs.earthdata.nasa.gov'

    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)

    def rebuild_auth(self, prepared_request, response):
        """
        Override to keep headers when redirected to/from NASA auth host.

        Args:
            prepared_request: The prepared request
            response: The response that triggered the redirect
        """
        headers = prepared_request.headers
        url = prepared_request.url

        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)

            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != self.AUTH_HOST and \
                    original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']


class HTTPSDownloader(BaseDownloader):
    """
    HTTPS protocol downloader.

    Supports:
        - Standard HTTPS
        - NASA Earthdata authentication (CDDIS)
        - SWARM special file listing from .txt files
    """

    def __init__(self, config_manager, ac_name, mode='standard'):
        """
        Initialize HTTPS downloader.

        Args:
            config_manager (ConfigManager): Configuration manager instance
            ac_name (str): Analysis center name
            mode (str): Download mode - 'standard', 'nasa', or 'swarm'
        """
        super().__init__(config_manager, ac_name)
        self.mode = mode
        self.session = None

        # Detect mode from config if not specified
        if mode == 'standard':
            # Check if NASA credentials are in config
            if self.config.has_option(ac_name, 'nasa_user') and \
               self.config.has_option(ac_name, 'nasa_passwd'):
                self.mode = 'nasa'
            # Check if SWARM mode is needed (can be detected from ac_name or config)
            elif 'swarm' in ac_name.lower():
                self.mode = 'swarm'

    def connect(self):
        """Establish HTTPS session."""
        if self.mode == 'nasa':
            # NASA Earthdata authentication
            username = self.config.get(self.ac_name, 'nasa_user', fallback=self.user)
            password = self.config.get(self.ac_name, 'nasa_passwd', fallback=self.passwd)

            if not username or not password:
                logging.warning("NASA credentials not found, using standard HTTPS")
                self.session = requests.Session()
            else:
                logging.debug(f"Creating NASA Earthdata session for user: {username}")
                self.session = SessionWithHeaderRedirection(username, password)

        elif self.mode == 'swarm':
            # SWARM mode uses standard session with custom headers
            self.session = requests.Session()
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://swarm-diss.eo.esa.int/"
            })
            logging.debug("Created SWARM HTTPS session")

        else:
            # Standard HTTPS
            self.session = requests.Session()
            logging.debug("Created standard HTTPS session")

    def disconnect(self):
        """Close HTTPS session."""
        if self.session:
            self.session.close()
            logging.debug("HTTPS session closed")

    def list_remote_files(self, remote_path):
        """
        List files in remote HTTPS directory.

        Behavior depends on mode:
            - standard/nasa: Parse HTML for file links
            - swarm: Read file list from .txt file

        Args:
            remote_path (str): Remote directory URL

        Returns:
            list: List of file names
        """
        if self.mode == 'swarm':
            return self._list_swarm_files(remote_path)
        elif self.mode == 'nasa':
            return self._list_nasa_files(remote_path)
        else:
            return self._list_standard_files(remote_path)

    def _list_standard_files(self, remote_path):
        """List files via standard HTTPS by parsing HTML."""
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

            logging.debug(f"Found {len(file_list)} files")
            return file_list

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to list files from {url}: {e}")
            raise

    def _list_nasa_files(self, remote_path):
        """List files from NASA CDDIS server."""
        try:
            url = self.host + remote_path
            logging.debug(f"Fetching NASA file list from {url}")

            # NASA CDDIS uses ?list endpoint
            response = self.session.get(url + "*?list", stream=True, timeout=30)

            if response.status_code != requests.codes.ok:
                logging.error(f"NASA server returned status code: {response.status_code}")
                raise Exception(f"HTTP {response.status_code}")

            # Parse response
            lines = response.text.split('\n')
            file_list = []

            for line in lines:
                line = line.strip()
                # Skip comments and empty lines
                if line.startswith("#") or line == "":
                    continue

                # Parse "filename size" format
                parts = line.split()
                if len(parts) >= 1:
                    filename = parts[0]
                    # Exclude metadata files
                    if filename not in ["MD5SUMS", "SHA512SUMS", "index.html"]:
                        file_list.append(filename)

            logging.debug(f"Found {len(file_list)} files from NASA")
            return file_list

        except Exception as e:
            logging.error(f"Failed to list NASA files from {url}: {e}")
            raise

    def _list_swarm_files(self, remote_path):
        """
        List files from SWARM server using .txt file list.

        SWARM structure:
            Remote path: /Level1b/Latest_baselines/MAGx_LR/2019/01/SW_OPER_MAGx_LR_1B_20190101T000000_20190101T235959_0702_20190101000000
            List file: /Level1b/Latest_baselines/MAGx_LR/2019/01/SW_OPER_MAGx_LR_1B_20190101T000000_20190101T235959_0702_20190101000000.txt
        """
        try:
            # Parse SWARM path structure
            http_path_parts = remote_path.strip('/').split('/')

            if len(http_path_parts) < 7:
                logging.error(f"Unexpected SWARM path structure: {remote_path}")
                return []

            # Adjust path (remove leading character from 4th component)
            if len(http_path_parts[3]) > 0:
                http_path_parts[3] = http_path_parts[3][1:]

            # Build list directory and file URL
            list_dir = '/'.join(http_path_parts[:6])
            list_filename = http_path_parts[6] + '.txt'
            list_url = self.host + '/' + list_dir + '/' + list_filename

            logging.debug(f"Fetching SWARM file list from {list_url}")

            response = self.session.get(list_url, timeout=30)
            if response.status_code != 200:
                logging.error(f"Failed to get SWARM file list. Status: {response.status_code}")
                return []

            # Parse file list
            lines = response.text.splitlines()
            file_list = [line.strip() for line in lines if line.strip()]

            logging.debug(f"Found {len(file_list)} files from SWARM list")
            return file_list

        except Exception as e:
            logging.error(f"Failed to list SWARM files: {e}")
            return []

    def download_file(self, remote_file, local_file, remote_path=None):
        """
        Download a single file via HTTPS.

        Args:
            remote_file (str): Remote file name
            local_file (str): Local file path
            remote_path (str, optional): Remote directory URL

        Returns:
            bool: True if download successful
        """
        try:
            # Build full URL
            if self.mode == 'swarm' and remote_path:
                # SWARM: reconstruct proper URL from path
                url = self._build_swarm_url(remote_path, remote_file)
            elif remote_path:
                url = self.host + remote_path + '/' + remote_file
            else:
                url = self.host + '/' + remote_file

            logging.debug(f"Downloading from {url}")

            # Download with retry for SWARM
            max_attempts = 3 if self.mode == 'swarm' else 1
            for attempt in range(1, max_attempts + 1):
                try:
                    response = self.session.get(url, stream=True, timeout=120)
                    response.raise_for_status()

                    # Write to file
                    with open(local_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024*1024):
                            if chunk:
                                f.write(chunk)

                    return True

                except requests.exceptions.RequestException as e:
                    if attempt < max_attempts:
                        logging.warning(f"Attempt {attempt} failed, retrying... ({e})")
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise

        except Exception as e:
            logging.error(f"Failed to download {remote_file}: {e}")
            return False

    def _build_swarm_url(self, remote_path, filename):
        """Build download URL for SWARM files."""
        http_path_parts = remote_path.strip('/').split('/')

        if len(http_path_parts) >= 7:
            # Adjust path structure
            if len(http_path_parts[3]) > 0:
                http_path_parts[3] = http_path_parts[3][1:]
            list_dir = '/'.join(http_path_parts[:6])
            return self.host + '/' + list_dir + '/' + filename
        else:
            # Fallback to simple concatenation
            return self.host + remote_path + '/' + filename
