#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration manager for GNSSBY.
Handles loading and parsing of configuration files.
"""

import os
import platform
import configparser
import logging
import re


class ConfigManager:
    """
    Manage GNSSBY configuration files.

    Attributes:
        config: Main configuration (config.ini or config_win.ini)
        table: Station filter configuration (listTable.ini)
    """

    def __init__(self, config_file=None, table_file='listTable.ini'):
        """
        Initialize configuration manager.

        Args:
            config_file (str, optional): Path to main config file.
                                        If None, auto-detect based on platform.
            table_file (str, optional): Path to station filter file.
                                       Defaults to 'listTable.ini'.
        """
        self.config = configparser.ConfigParser()
        self.table = configparser.ConfigParser(allow_no_value=True)

        # Auto-detect config file based on platform
        if config_file is None:
            if platform.system() == "Linux":
                config_file = 'config.ini'
            elif platform.system() == "Windows":
                config_file = 'config_win.ini'
            else:
                logging.error(f"Unsupported platform: {platform.system()}")
                logging.error("Please manually specify config_file parameter")
                raise SystemExit(1)

        # Check if config file exists
        if not os.path.exists(config_file):
            logging.error(f"Config file does not exist: {config_file}")
            raise FileNotFoundError(f"Config file not found: {config_file}")

        # Load configurations
        self.config.read(config_file, encoding='utf-8')
        logging.info(f"Loaded configuration from: {config_file}")

        if os.path.exists(table_file):
            self.table.read(table_file, encoding='utf-8')
            logging.info(f"Loaded station filter from: {table_file}")
        else:
            logging.warning(f"Station filter file not found: {table_file}")

    def get_ac_list(self):
        """
        Get list of all available analysis centers from config.

        Returns:
            list: List of AC section names (excluding 'global')
        """
        sections = self.config.sections()
        # Exclude 'global' section
        return [sec for sec in sections if sec != 'global']

    def get_global_option(self, option, default=None):
        """
        Get option from [global] section.

        Args:
            option (str): Option name
            default: Default value if option doesn't exist

        Returns:
            str or default: Option value or default
        """
        if self.config.has_option('global', option):
            return self.config.get('global', option)
        return default

    def get_local_dir(self):
        """Get local download directory from global config."""
        return self.get_global_option('local_dir', './')

    def get_overwrite_flag(self):
        """
        Get overwrite flag from global config.

        Returns:
            bool: True if overwrite is enabled, False otherwise
        """
        overwrite = self.get_global_option('overwrite', '0')
        return overwrite == '1'

    def get_time_interval(self, ac_name):
        """
        Get time interval (step) for an AC.

        Args:
            ac_name (str): Analysis center name

        Returns:
            int: Time interval in hours (default: 24)
        """
        if self.config.has_option(ac_name, 'step'):
            return int(self.config.get(ac_name, 'step'))
        return 24

    def get_file_types(self, ac_name):
        """
        Extract file types from [file_type] placeholder.

        Args:
            ac_name (str): Analysis center name

        Returns:
            list: List of file types, or [''] if not specified

        Example:
            If file_type = "[sp3] [clk]", returns ['sp3', 'clk']
        """
        if self.config.has_option(ac_name, 'file_type'):
            file_type_str = self.config.get(ac_name, 'file_type')
            # Extract patterns between [ ]
            pattern = re.compile(r'\[(.*?)\]', re.S)
            types = re.findall(pattern, file_type_str)
            return types if types else ['']
        return ['']

    def get_rename_patterns(self, ac_name):
        """
        Extract rename patterns from [rename_pattern] placeholder.

        Args:
            ac_name (str): Analysis center name

        Returns:
            list: List of rename patterns, or [''] if not specified

        Raises:
            ValueError: If number of patterns doesn't match file_types
        """
        file_types = self.get_file_types(ac_name)

        if self.config.has_option(ac_name, 'rename_pattern'):
            rename_str = self.config.get(ac_name, 'rename_pattern')
            pattern = re.compile(r'\[(.*?)\]', re.S)
            patterns = re.findall(pattern, rename_str)

            if len(patterns) != len(file_types):
                raise ValueError(
                    f"{ac_name}: Number of [file_type] ({len(file_types)}) "
                    f"doesn't match [rename_pattern] ({len(patterns)})"
                )
            return patterns
        else:
            # Return empty strings for each file type
            return [''] * len(file_types)

    def get_station_filter(self, ac_name):
        """
        Get station filter list for an AC.

        Args:
            ac_name (str): Analysis center name

        Returns:
            list or None: List of station names to download, or None if no filter

        Note:
            If filter exists but is empty, downloads all stations.
            If filter has entries, only downloads listed stations.
        """
        if self.table.has_section(ac_name):
            options = self.table.options(ac_name)
            if len(options) == 0:
                return None  # No filter, download all
            return [opt.upper() for opt in options]
        return None  # No filter section, download all

    def has_ac(self, ac_name):
        """
        Check if AC exists in config.

        Args:
            ac_name (str): Analysis center name

        Returns:
            bool: True if AC section exists
        """
        return self.config.has_section(ac_name)

    def get_ac_config(self, ac_name):
        """
        Get full configuration dict for an AC.

        Args:
            ac_name (str): Analysis center name

        Returns:
            dict: Configuration dictionary

        Raises:
            ValueError: If AC section doesn't exist
        """
        if not self.has_ac(ac_name):
            raise ValueError(f"AC section '{ac_name}' not found in config")

        return dict(self.config.items(ac_name))

    def log_available_acs(self):
        """Log all available AC configurations."""
        ac_list = self.get_ac_list()
        logging.debug("************* Available AC Configurations *************")
        logging.debug(f"Total: {len(ac_list)} analysis centers")
        for ac in ac_list:
            logging.debug(f"  - {ac}")
        logging.debug("*******************************************************")
