#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Project: youtube-dl-transcode-pipeline
# FilePath: /setup.py
# File: setup.py
# Created Date: Monday, May 25th 2020, 9:15:11 pm
# Author: Craig Bojko (craig@pixelventures.co.uk)
# -----
# Last Modified: Mon May 25 2020
# Modified By: Craig Bojko
# -----
# Copyright (c) 2020 Pixel Ventures Ltd.
# ------------------------------------
# <<licensetext>>
###


from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

# with open('LICENSE') as f:
#     license = f.read()

setup(
    name='youtube-dl-transcode-pipeline',
    version='1.0.0',
    description='Video transcoder service for merging Youtube Video and Audio assets and uploading to NAS server',
    long_description=readme,
    author='Pixel Ventures Ltd.',
    author_email='craig@pixelventures.co.uk',
    url='https://github.com/pixelventures/youtube-dl-transcoder-pipeline',
    # license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)