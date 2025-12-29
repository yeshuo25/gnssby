#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Time utility functions for GNSSBY.
Handles time conversions and placeholder replacements.
"""

import datetime


def datetime2doy(epotime):
    """
    Convert datetime to day of year (DOY).

    Args:
        epotime (datetime): Input datetime object

    Returns:
        int: Day of year (1-366)

    Example:
        >>> datetime2doy(datetime.datetime(2019, 1, 15))
        15
    """
    year = epotime.year
    year_origin = datetime.datetime(year, 1, 1, 0, 0, 0)
    return (epotime - year_origin).days + 1


def datetime2gpst(epotime, weekday):
    """
    Convert datetime to GPS time (week and day of week).

    Args:
        epotime (datetime): Input datetime object
        weekday (list): Output list [gps_week, day_of_week]

    Note:
        GPS time starts from 1980-01-06 00:00:00 UTC
        weekday is modified in place

    Example:
        >>> weekday = []
        >>> datetime2gpst(datetime.datetime(2019, 1, 1), weekday)
        >>> print(weekday)  # [2034, 2]
    """
    delt_days = (epotime - datetime.datetime(1980, 1, 6, 0, 0, 0)).days
    weekday.append(int(delt_days / 7))
    weekday.append(int(delt_days - weekday[0] * 7))


def replace_time_placeholders(input_string, epotime):
    """
    Replace time placeholders in a string with actual time values.

    Supported placeholders:
        [YYYY] - 4-digit year (e.g., 2019)
        [YY]   - 2-digit year (e.g., 19)
        [DDD]  - 3-digit day of year (e.g., 001)
        [DAY]  - 2-digit day of month (e.g., 15)
        [MONTH]- 2-digit month (e.g., 01)
        [HOUR] - 2-digit hour (e.g., 12)
        [WEEK] - 4-digit GPS week (e.g., 2034)
        [WOD]  - 2-digit GPS day of week (e.g., 02)
        [WD]   - 5-digit GPS day format [wwwwd] (e.g., 20342)

    Args:
        input_string (str): String with time placeholders
        epotime (datetime): Time to use for replacement

    Returns:
        str: String with placeholders replaced

    Example:
        >>> replace_time_placeholders('[YYYY]/[DDD]', datetime.datetime(2019, 1, 15))
        '2019/015'
    """
    result = input_string
    weekday = []
    datetime2gpst(epotime, weekday)

    # Year placeholders
    if '[YYYY]' in result:
        result = result.replace('[YYYY]', str(epotime.year).zfill(4))

    if '[YY]' in result:
        result = result.replace('[YY]', str(epotime.year % 1000).zfill(2))

    # Day placeholders
    if '[DDD]' in result:
        result = result.replace('[DDD]', str(datetime2doy(epotime)).zfill(3))

    if '[DAY]' in result:
        result = result.replace('[DAY]', str(epotime.day).zfill(2))

    # Month placeholder
    if '[MONTH]' in result:
        result = result.replace('[MONTH]', str(epotime.month).zfill(2))

    # Hour placeholder
    if '[HOUR]' in result:
        result = result.replace('[HOUR]', str(epotime.hour).zfill(2))

    # GPS week placeholders
    if '[WEEK]' in result:
        result = result.replace('[WEEK]', str(weekday[0]).zfill(4))

    if '[WOD]' in result:
        result = result.replace('[WOD]', str(weekday[1]).zfill(2))

    if '[WD]' in result:
        result = result.replace('[WD]', str(weekday[0] * 10 + weekday[1]).zfill(5))

    # Replace wildcard character
    result = result.replace('?', '.')

    return result


def replace_type_placeholder(input_string, file_type):
    """
    Replace [file_type] and [rename_pattern] placeholders in a string.

    Args:
        input_string (str): String with type placeholders
        file_type (str): File type to replace with

    Returns:
        str: String with placeholders replaced

    Example:
        >>> replace_type_placeholder('WUM*.[file_type].gz', 'sp3')
        'WUM*.sp3.gz'
    """
    result = input_string

    if '[file_type]' in result:
        result = result.replace('[file_type]', file_type)

    if '[rename_pattern]' in result:
        result = result.replace('[rename_pattern]', file_type)

    return result


def replace_site_placeholder(input_string, site_string):
    """
    Replace [SITE] and [site] placeholders with station name.

    Args:
        input_string (str): String with site placeholders
        site_string (str): Station name to replace with

    Returns:
        str: String with placeholders replaced

    Example:
        >>> replace_site_placeholder('[SITE][WD].sp3', 'wuh2')
        'WUH220342.sp3'
    """
    if not site_string:
        return input_string

    result = input_string

    if '[SITE]' in result:
        result = result.replace('[SITE]', site_string.upper())

    if '[site]' in result:
        result = result.replace('[site]', site_string.lower())

    return result


def replace_all_placeholders(input_string, epotime, file_type='', site_string=''):
    """
    Replace all placeholders (time, type, site) in a string.

    Args:
        input_string (str): String with placeholders
        epotime (datetime): Time to use for replacement
        file_type (str, optional): File type to replace with
        site_string (str, optional): Station name to replace with

    Returns:
        str: String with all placeholders replaced

    Example:
        >>> replace_all_placeholders('[YYYY]/[site][DDD].[file_type]',
        ...                          datetime.datetime(2019, 1, 15), 'rnx', 'wuh2')
        '2019/wuh2015.rnx'
    """
    result = replace_time_placeholders(input_string, epotime)
    if file_type:
        result = replace_type_placeholder(result, file_type)
    if site_string:
        result = replace_site_placeholder(result, site_string)
    return result
