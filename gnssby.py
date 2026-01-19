#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNSSBY - GNSS Data Downloader
Main entry point for downloading GNSS data from various sources.

Usage:
    python gnssby.py

Configuration:
    Edit this file to set:
        - ts: Start time
        - te: End time
        - AClist: List of analysis centers to download from

    Configuration files:
        - config.ini (Linux) or config_win.ini (Windows)
        - listTable.ini (station filters)
"""

import sys
import os
import time
import datetime
import logging

from gnssby.core.config_manager import ConfigManager
from gnssby.downloaders.ftp import FTPDownloader
from gnssby.downloaders.http import HTTPDownloader
from gnssby.downloaders.https import HTTPSDownloader
from gnssby.downloaders.sftp import SFTPDownloader


# ==================== Configuration ====================
# Set your download time range
ts = datetime.datetime(2021, 8, 25)
te = datetime.datetime(2021, 8, 25)

# Set analysis centers to download
# Available AC types are defined in config.ini or config_win.ini
AClist = ['HTTPS_RNX', 'HTTPS_AC', 'HTTPS_ACs', 'HTTPS_BRDM']
AClist = ['WHU_SNX']
# AClist = ['grace-fo']
# AClist = ['swarm_RD']
# AClist = ['ucar_att2', 'ucar_clk2', 'ucar_RO2']
# ======================================================


def create_logger():
    """Create and configure logger."""
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%m/%d/%Y %H:%M:%S"

    # Create log directory
    if not os.path.exists("log_gnssby"):
        os.mkdir("log_gnssby")

    # Generate log filename
    timestr = datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S.txt")
    logname = os.path.join('log_gnssby', timestr)

    # Configure logging
    logging.basicConfig(
        filename=logname,
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format
    )

    # Also log to console
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(log_format, date_format))
    logging.getLogger().addHandler(console)

    logging.info("=" * 60)
    logging.info("GNSSBY - GNSS Data Downloader v2.0")
    logging.info("=" * 60)


def get_downloader(config_manager, ac_name):
    """
    Create appropriate downloader based on ftp_type in config.

    Args:
        config_manager (ConfigManager): Configuration manager
        ac_name (str): Analysis center name

    Returns:
        BaseDownloader: Appropriate downloader instance

    Raises:
        ValueError: If ftp_type is unsupported
    """
    if not config_manager.has_ac(ac_name):
        raise ValueError(f"AC '{ac_name}' not found in configuration")

    ftp_type = config_manager.config.get(ac_name, 'ftp_type')

    if ftp_type == 'ftp':
        return FTPDownloader(config_manager, ac_name, use_tls=False)

    elif ftp_type == 'tls':
        return FTPDownloader(config_manager, ac_name, use_tls=True)

    elif ftp_type == 'http':
        return HTTPDownloader(config_manager, ac_name)

    elif ftp_type == 'https':
        # Detect special HTTPS modes
        if 'swarm' in ac_name.lower():
            return HTTPSDownloader(config_manager, ac_name, mode='swarm')
        elif config_manager.config.has_option(ac_name, 'nasa_user'):
            return HTTPSDownloader(config_manager, ac_name, mode='nasa')
        else:
            return HTTPSDownloader(config_manager, ac_name, mode='standard')

    elif ftp_type == 'sftp':
        return SFTPDownloader(config_manager, ac_name)

    else:
        raise ValueError(f"Unsupported ftp_type: {ftp_type} for AC: {ac_name}")


def main():
    """Main function."""
    start_time = time.time()

    # Create logger
    create_logger()

    # Load configuration
    try:
        config_manager = ConfigManager()
        logging.info("Configuration loaded successfully")
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Log available ACs
    config_manager.log_available_acs()
    logging.info("")
    logging.info(f"Download time range: {ts} to {te}")
    logging.info(f"Analysis centers to download: {AClist}")
    logging.info("")

    # Process each AC in the list
    for ac_name in AClist:
        if not ac_name:  # Skip empty strings
            continue

        logging.info("=" * 60)
        logging.info(f"Processing AC: {ac_name}")
        logging.info("=" * 60)

        try:
            # Get AC configuration
            ac_config = config_manager.get_ac_config(ac_name)
            logging.debug(f"Host: {ac_config.get('host', 'N/A')}")
            logging.debug(f"Remote dir: {ac_config.get('remote_dir', 'N/A')}")
            logging.debug(f"File pattern: {ac_config.get('file_pattern', 'N/A')}")
            logging.debug(f"FTP type: {ac_config.get('ftp_type', 'N/A')}")

            # Create downloader
            downloader = get_downloader(config_manager, ac_name)

            # Start download
            downloader.download(ts, te)

            logging.info(f"Completed AC: {ac_name}")

        except Exception as e:
            logging.error(f"Error processing AC '{ac_name}': {e}")
            import traceback
            logging.debug(traceback.format_exc())
            continue

        logging.info("")

    # Summary
    end_time = time.time()
    elapsed = end_time - start_time

    logging.info("=" * 60)
    logging.info("All downloads completed")
    logging.info(f"Total time elapsed: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()
