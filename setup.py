#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for GNSSBY.
"""

from setuptools import setup, find_packages
import os

# Read README
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

# Read version
version = '2.0.0'

setup(
    name='gnssby',
    version=version,
    description='GNSS Data Downloader - Download GNSS data from multiple sources',
    long_description=read_file('README.md') if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    author='GNSSBY Team',
    author_email='gnssby@gmail.com',
    url='https://github.com/yeshuo25/gnssby',
    license='LICENSE',

    packages=find_packages(),
    python_requires='>=3.6',

    install_requires=[
        'requests>=2.25.0',
        'paramiko>=2.7.0',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],

    keywords='gnss gps data downloader ftp http https sftp rinex',

    entry_points={
        'console_scripts': [
            'gnssby=gnssby:main',
        ],
    },

    include_package_data=True,
    zip_safe=False,
)
