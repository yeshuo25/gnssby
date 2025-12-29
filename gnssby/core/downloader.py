#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abstract base class for GNSSBY downloaders.
"""

import os
import datetime
import re
import logging
from abc import ABC, abstractmethod

from gnssby.core.time_utils import replace_all_placeholders
from gnssby.core.file_utils import archive_process


class BaseDownloader(ABC):
    """
    Abstract base class for protocol-specific downloaders.

    All downloaders must implement:
        - connect()
        - disconnect()
        - list_remote_files()
        - download_file()
    """

    def __init__(self, config_manager, ac_name):
        """
        Initialize downloader.

        Args:
            config_manager (ConfigManager): Configuration manager instance
            ac_name (str): Analysis center name
        """
        self.config_manager = config_manager
        self.ac_name = ac_name
        self.config = config_manager.config
        self.table = config_manager.table

        # Validate AC exists
        if not self.config.has_section(ac_name):
            raise ValueError(f"AC '{ac_name}' not found in configuration")

        # Get AC configuration
        self.host = self.config.get(ac_name, 'host')
        self.remote_dir = self.config.get(ac_name, 'remote_dir')
        self.file_pattern = self.config.get(ac_name, 'file_pattern')
        self.lsub_dir = self.config.get(ac_name, 'lsub_dir')

        # Get optional parameters
        self.user = self.config.get(ac_name, 'user') if self.config.has_option(ac_name, 'user') else None
        self.passwd = self.config.get(ac_name, 'passwd') if self.config.has_option(ac_name, 'passwd') else None

        # Get time interval and file types
        self.time_interval = self.config_manager.get_time_interval(ac_name)
        self.file_types = self.config_manager.get_file_types(ac_name)
        self.rename_patterns = self.config_manager.get_rename_patterns(ac_name)

        # Get station filter
        self.station_filter = self.config_manager.get_station_filter(ac_name)

        logging.debug(f"Initialized {self.__class__.__name__} for {ac_name}")
        logging.debug(f"  Host: {self.host}")
        logging.debug(f"  Remote dir: {self.remote_dir}")
        logging.debug(f"  File pattern: {self.file_pattern}")

    @abstractmethod
    def connect(self):
        """Establish connection to remote server."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close connection to remote server."""
        pass

    @abstractmethod
    def list_remote_files(self, remote_path):
        """
        List files in remote directory.

        Args:
            remote_path (str): Remote directory path

        Returns:
            list: List of file names
        """
        pass

    @abstractmethod
    def download_file(self, remote_file, local_file):
        """
        Download a single file.

        Args:
            remote_file (str): Remote file path/name
            local_file (str): Local file path

        Returns:
            bool: True if download successful
        """
        pass

    def prepare_local_directory(self, epoch, file_type=''):
        """
        Prepare local directory for downloads.

        Args:
            epoch (datetime): Time epoch
            file_type (str, optional): File type for placeholder replacement

        Returns:
            str: Local directory path (with trailing /)
        """
        local_base = self.config_manager.get_local_dir()
        local_path = os.path.join(local_base, self.lsub_dir)

        # Replace placeholders
        local_dir = replace_all_placeholders(local_path, epoch, file_type)

        # Create directory if it doesn't exist
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
            logging.debug(f"Created local directory: {local_dir}")

        return local_dir + os.sep

    def should_download_station(self, filename):
        """
        Check if file should be downloaded based on station filter.

        Args:
            filename (str): File name

        Returns:
            tuple: (should_download: bool, station_name: str)
        """
        # No filter - download all files
        if self.station_filter is None:
            # Extract first 4 characters as default station name
            station_name = filename[:4] if len(filename) >= 4 else filename
            return True, station_name

        # Filter exists - check station name
        if len(self.station_filter) == 0:
            # Empty filter - download all
            station_name = filename[:4] if len(filename) >= 4 else filename
            return True, station_name

        # Determine station name length from first filter entry
        name_length = len(self.station_filter[0])
        station_name = filename[:name_length]

        # Check if station is in filter (case-insensitive)
        if station_name.upper() in [s.upper() for s in self.station_filter]:
            return True, station_name

        return False, station_name

    def should_skip_existing(self, local_file):
        """
        Check if existing file should be skipped.

        Args:
            local_file (str): Local file path

        Returns:
            bool: True if should skip download
        """
        overwrite = self.config_manager.get_overwrite_flag()

        if not overwrite and os.path.exists(local_file):
            logging.warning(f"{local_file} already exists, skipping (overwrite=0)")
            return True

        return False

    def download(self, start_time, end_time):
        """
        Main download method - iterates through time epochs.

        Args:
            start_time (datetime): Start time
            end_time (datetime): End time
        """
        logging.info(f"Starting download for {self.ac_name}")
        logging.info(f"Time range: {start_time} to {end_time}")

        # Connect to server
        self.connect()

        try:
            epoch = start_time
            while epoch <= end_time:
                logging.debug(f"Processing epoch: {epoch.strftime('%Y-%m-%d %H:%M:%S')}")

                # Iterate through file types for directories
                for i_type_dir, file_type in enumerate(self.file_types):
                    # Only iterate if [file_type] placeholder in remote_dir
                    if '[file_type]' not in self.remote_dir and i_type_dir > 0:
                        break

                    self._download_epoch_type(epoch, file_type, i_type_dir)

                # Move to next epoch
                epoch = epoch + datetime.timedelta(hours=self.time_interval)

        finally:
            # Always disconnect
            self.disconnect()

        logging.info(f"Download completed for {self.ac_name}")

    def _download_epoch_type(self, epoch, file_type, type_index):
        """
        Download files for a specific epoch and file type.

        Args:
            epoch (datetime): Time epoch
            file_type (str): File type
            type_index (int): Index in file_types list
        """
        # Prepare local directory
        local_dir = self.prepare_local_directory(epoch, file_type)

        # Get remote directory
        remote_path = replace_all_placeholders(
            self.remote_dir,
            epoch,
            file_type
        )

        logging.debug(f"Remote path: {remote_path}")
        logging.debug(f"Local dir: {local_dir}")

        # List remote files
        try:
            remote_files = self.list_remote_files(remote_path)
        except Exception as e:
            logging.error(f"Failed to list remote files in {remote_path}: {e}")
            return

        # Iterate through file types for file patterns
        for i_type_file, file_type_pattern in enumerate(self.file_types):
            # Only iterate if [file_type] placeholder in file_pattern
            if '[file_type]' not in self.file_pattern and i_type_file > 0:
                break

            # Get file pattern
            pattern = replace_all_placeholders(
                self.file_pattern,
                epoch,
                file_type_pattern
            )

            # Match files
            matched_files = [f for f in remote_files if re.match(pattern, f)]

            logging.debug(f"Pattern: {pattern}, Matched: {len(matched_files)} files")

            # Download matched files
            for filename in matched_files:
                self._download_single_file(
                    filename,
                    remote_path,
                    local_dir,
                    epoch,
                    i_type_file
                )

    def _download_single_file(self, filename, remote_path, local_dir, epoch, type_index):
        """
        Download a single file with station filtering and post-processing.

        Args:
            filename (str): File name
            remote_path (str): Remote directory path
            local_dir (str): Local directory path
            epoch (datetime): Time epoch
            type_index (int): Index in file_types/rename_patterns list
        """
        # Check station filter
        should_download, station_name = self.should_download_station(filename)
        if not should_download:
            logging.debug(f"Skipping {filename} (not in station filter)")
            return

        # Check if file already exists
        local_file = os.path.join(local_dir, filename)
        if self.should_skip_existing(local_file):
            return

        # Download file
        logging.info(f"Downloading {filename} ...")
        try:
            success = self.download_file(filename, local_file, remote_path)
            if success:
                logging.info(f"Downloaded {filename} successfully")

                # Post-process: decompress, convert, rename
                rename_pattern = self.rename_patterns[type_index] if type_index < len(self.rename_patterns) else ''
                archive_process(
                    self.config,
                    self.ac_name,
                    local_file,
                    epoch,
                    rename_pattern,
                    station_name
                )
            else:
                logging.error(f"Failed to download {filename}")
        except Exception as e:
            logging.error(f"Error downloading {filename}: {e}")
