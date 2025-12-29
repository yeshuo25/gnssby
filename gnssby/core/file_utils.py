#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File utility functions for GNSSBY.
Handles file decompression, CRX conversion, and renaming.
"""

import os
import platform
import logging


def decompress_file(compressed_file):
    """
    Decompress various archive formats.

    Supported formats:
        Linux: .tar.gz, .tar, .tgz, .Z, .gz, .zip, .ZIP, .rar
        Windows: .gz

    Args:
        compressed_file (str): Path to compressed file

    Returns:
        str: Path to decompressed file

    Raises:
        SystemExit: If platform is unsupported or file format is unrecognized
    """
    system = platform.system()

    if system == "Linux":
        if compressed_file.endswith('.tar.gz') or \
           compressed_file.endswith('.tar') or \
           compressed_file.endswith('.tgz'):
            command = 'tar zxvf '
            root, ext = os.path.splitext(compressed_file)
            if ext in ['.gz', '.bz2']:
                decompressed_name, _ = os.path.splitext(root)
            else:
                decompressed_name = root

        elif compressed_file.endswith('.Z'):
            command = 'uncompress -dvf '
            decompressed_name, _ = os.path.splitext(compressed_file)

        elif compressed_file.endswith('.gz'):
            command = 'gunzip -dvf '
            decompressed_name, _ = os.path.splitext(compressed_file)

        elif compressed_file.endswith('.zip') or compressed_file.endswith('.ZIP'):
            command = 'unzip '
            decompressed_name, _ = os.path.splitext(compressed_file)

        elif compressed_file.endswith('.rar'):
            command = 'rar x '
            decompressed_name, _ = os.path.splitext(compressed_file)

        else:
            logging.error(f"decompress_file: Unrecognized file: {compressed_file}")
            logging.error("decompress_file: Please manually modify source code.")
            decompressed_name = ""

    elif system == "Windows":
        command = 'gzip -dvf '
        decompressed_name, _ = os.path.splitext(compressed_file)

    else:
        logging.error(f"decompress_file: System platform {system} is not supported!")
        logging.error("decompress_file: Please manually modify source code.")
        os._exit(1)

    logging.debug(f"decompress_file: command={command}{compressed_file}")
    logging.debug(f"decompress_file: decompressed file={decompressed_name}")
    os.system(command + compressed_file)

    return decompressed_name


def convert_crx2rnx(crx_file):
    """
    Convert Hatanaka compressed RINEX (CRX) to standard RINEX format.

    Args:
        crx_file (str): Path to CRX file (ends with 'd' or '.crx')

    Note:
        Requires crx2rnx binary in bin/ directory.
        Original CRX file will be deleted after conversion.
    """
    logging.debug(f'convert_crx2rnx: converting {crx_file}')

    # Determine path to crx2rnx binary
    # Assuming it's in bin/ relative to the project root
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    crx2rnx_path = os.path.join(script_dir, 'bin', 'crx2rnx')

    if platform.system() == "Windows":
        crx2rnx_path += '.exe'

    command = f'"{crx2rnx_path}" '
    os.system(command + crx_file)

    # Remove original CRX file
    if os.path.exists(crx_file):
        os.remove(crx_file)


def rename_file(old_path, new_path):
    """
    Rename or move a file.

    Args:
        old_path (str): Current file path
        new_path (str): New file path

    Note:
        Logs a warning if source file doesn't exist.
    """
    if not os.path.exists(old_path):
        logging.warning(f'rename_file: Source file does not exist: {old_path}')
        return

    os.rename(old_path, new_path)
    logging.debug(f'rename_file: {old_path} -> {new_path}')


def archive_process(config, ac_name, downloaded_file, epoch, file_type, station_name):
    """
    Post-process downloaded files: decompress, convert CRX, and rename.

    Processing pipeline:
        1. Decompress (if config['decompression'] == '1')
        2. Convert CRX to RNX (if config['crx2rnx'] == '1')
        3. Rename (if config['rename'] is specified)

    Args:
        config (ConfigParser): Configuration object
        ac_name (str): Analysis center name (config section)
        downloaded_file (str): Path to downloaded file
        epoch (datetime): Time epoch for placeholder replacement
        file_type (str): File type for placeholder replacement
        station_name (str): Station name for placeholder replacement

    Note:
        This function modifies files in place.
    """
    from gnssby.core.time_utils import replace_all_placeholders

    filepath, filename = os.path.split(downloaded_file)
    processed_file = downloaded_file

    # Step 1: Decompress
    if config.has_option(ac_name, 'decompression') and \
       config.get(ac_name, 'decompression') == '1':
        processed_file = decompress_file(downloaded_file)
        logging.debug(f'archive_process: Decompressed {downloaded_file} -> {processed_file}')

    # Step 2: Convert CRX to RNX
    if config.has_option(ac_name, 'crx2rnx') and \
       config.get(ac_name, 'crx2rnx') == '1':
        if processed_file.endswith('d'):
            new_file = processed_file[:-2] + 'o'
        elif processed_file.endswith('.crx'):
            new_file = processed_file[:-4] + '.rnx'
        else:
            logging.error(f'archive_process: crx2rnx - Unrecognized file {processed_file}')
            logging.error('archive_process: Deleting files')
            if os.path.exists(downloaded_file):
                os.remove(downloaded_file)
            if os.path.exists(processed_file):
                os.remove(processed_file)
            return

        if os.path.exists(new_file):
            os.remove(new_file)

        convert_crx2rnx(processed_file)
        processed_file = new_file
        logging.debug(f'archive_process: Converted CRX to RNX -> {processed_file}')

    # Step 3: Rename
    if config.has_option(ac_name, 'rename'):
        rename_template = config.get(ac_name, 'rename')
        new_name = replace_all_placeholders(
            rename_template,
            epoch,
            file_type,
            station_name
        )
        new_path = os.path.join(filepath, new_name)
        rename_file(processed_file, new_path)
        logging.debug(f'archive_process: Renamed {processed_file} -> {new_path}')
