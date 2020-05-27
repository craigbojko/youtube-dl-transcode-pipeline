#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Project: custom_json_encoder
# FilePath: /customJsonEncoder.py
# File: customJsonEncoder.py
# Created Date: Saturday, May 23rd 2020, 9:33:09 pm
# Author: Craig Bojko (craig@pixelventures.co.uk)
# -----
# Last Modified: Sun May 24 2020
# Modified By: Craig Bojko
# -----
# Copyright (c) 2020 Pixel Ventures Ltd.
# ------------------------------------
# <<licensetext>>
###

import json
import decimal

# Helper class to convert a DynamoDB item to JSON.
class CustomEncoder(json.JSONEncoder):
    def default(self, item):
        if isinstance(item, decimal.Decimal):
            if item % 1 > 0: return float(item)
            else: return int(item)
        return super(CustomEncoder, self).default(item)
