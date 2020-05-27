#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Project: transcoder_pipeline
# FilePath: /main.py
# File: main.py
# Created Date: Saturday, May 23rd 2020, 7:45:17 pm
# Author: Craig Bojko (craig@pixelventures.co.uk)
# -----
# Last Modified: Wed May 27 2020
# Modified By: Craig Bojko
# -----
# Copyright (c) 2020 Pixel Ventures Ltd.
# ------------------------------------
# <<licensetext>>
###

import os
import json
import boto3
import progressbar
import ffmpeg
import logging
import time
import threading

from concurrent.futures import ThreadPoolExecutor
from string import Template
from termcolor import colored
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

from .custom_json_encoder import CustomEncoder

ROOT_PATH = os.getcwd()
PROGRESS = [
    'ready',
    'in_progress',
    'transcoding',
    'uploading',
    'done'
]

FORMAT = "%(asctime)-15s: %(message)s"
LONG_FORMAT = '%(asctime)-15s %(clientIp)s %(user)-8s %(message)s'
LOG_EXTRA = { 'clientIp': '...', 'user': '...' }
logging.basicConfig(
    format=FORMAT,
    level=logging.INFO,
    datefmt="%H:%M:%S"
)
console = logging.getLogger('console')
console_handler = logging.StreamHandler()
console_handler.setFormatter(FORMAT)

s3_lock = threading.Lock()
ffmpeg_lock = threading.Lock()

def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which
    return which(name) is not None

def log(msg='', *args, type='info'):
    items = []
    items.append(msg)
    for arg in args:
        items.append(colored(arg, 'cyan'))
    logStr = ("\n\t\t").join(items)

    formatter = logging.Formatter(LONG_FORMAT)
    formatter.datefmt = "%H:%M:%S"
    console_handler.setFormatter(formatter)

    def info(): console.info(logStr, extra=LOG_EXTRA)
    def debug(): console.debug(logStr, extra=LOG_EXTRA,)
    def warning(): console.warning(logStr, extra=LOG_EXTRA,)
    def error(): console.error(logStr, extra=LOG_EXTRA,)

    options = {
        'info': info,
        'debug': debug,
        'warning': warning,
        'error': error
    }
    options[type]()


def main():
    log('Running Module at Path: ', ROOT_PATH)
    if is_tool('ffmpeg'):
        log(colored('FFMPEG installed', 'green'))
    else:
        log(colored('FFMPEG NOT installed', 'red'))


    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2') # , endpoint_url='http://localhost:8000')
    table = dynamodb.Table('youtube-dl-transcode-jobs-test')

    try:
        # response = table.query(
        #     KeyConditionExpression=Key('jobId').eq('1'),
        #     ProjectionExpression='#id, #status, #keys, #bucket, #assetId',
        #     ExpressionAttributeNames={
        #         '#id': 'jobId',
        #         '#assetId': 'assetId',
        #         '#status': 'status',
        #         '#keys': 'keys',
        #         '#bucket': 'bucket'
        #     }
        # )

        response = table.scan(
            FilterExpression=Key('status').eq(PROGRESS[0]),
            ProjectionExpression='#id, #status, #keys, #bucket, #assetId',
            ExpressionAttributeNames={
                '#id': 'jobId',
                '#assetId': 'assetId',
                '#status': 'status',
                '#keys': 'keys',
                '#bucket': 'bucket'
            }
        )
        # print(json.dumps(response, indent=2, cls=CustomEncoder))

        template = Template(' - Job ID: $id\n\t\t - Name: $assetId\n\t\t - Status: $status')
        for item in response['Items']:
            str = colored(template.substitute(
                id=item['jobId'],
                status=item['status'],
                assetId=item['assetId']
            ), 'green')
            log('Asset:', str)

        with ThreadPoolExecutor(max_workers=2) as executor:
            # executor.map(lambda item: pipeline(table, item), response['Items'])
            for item in response['Items']:
              executor.submit(pipeline, table, item)

        time.sleep(1)
    except ClientError as error:
        log(error.response['Error']['Message'], [], type='error')


def pipeline(table, item):
    log('Pipeline Job: ' + colored(item['jobId'], 'cyan'))
    # updateDynamoDbRecordStatus(table, item, PROGRESS[1])
    # fetchAssetsFromS3(item)
    # transcode(item)
    log('Pipeline Job ' + colored(item['jobId'], 'cyan') + ': ' + colored('Finished', 'green'))


def updateDynamoDbRecordStatus(dbTable, record, newStatus):
    update_response = dbTable.update_item(
        Key={ 'jobId': record['jobId'] },
        UpdateExpression="set #status = :s",
        ExpressionAttributeNames={ '#status': 'status' },
        ExpressionAttributeValues={ ':s': newStatus },
        ReturnValues="ALL_NEW"
    )
    log('Updated Asset Status: ', colored(update_response['Attributes']['jobId'], 'green'), ':', colored(update_response['Attributes']['status'], 'green'))


def fetchAssetsFromS3(asset):
    # _lock.acquire()

    with s3_lock:
        log(f"{asset['jobId']} acquired lock")
        s3 = boto3.client('s3')
        try:
            for item in asset['keys']:
                # Get metadata and content size of item
                metaResponse = s3.head_object(Bucket=asset['bucket'], Key=item)
                contentSize = metaResponse['ContentLength']

                # create progressbar and start it
                progress = progressbar.progressbar.ProgressBar(maxval=contentSize)
                progress.start()

                # Progressbar updater
                def download_progress(chunk):
                    progress.update(progress.currval + chunk)

                # Download the object
                log('Downloading item: ', item)
                with open(ROOT_PATH + '/workspace/' + item, 'wb') as f:
                    s3.download_fileobj(asset['bucket'], item, f, Callback=download_progress)

                # Finish progress and log
                progress.finish()
                log('Item Downloaded to workspace: ', item)
                log(f"{asset['jobId']} releasing lock")
                # _lock.release()
        except ClientError as error:
            log(colored(f"Error fetching Asset Item: {asset} =>\n{error.response['Error']['Message']}", 'red'))


def transcode(asset):
    try:
        with ffmpeg_lock:
            log(colored(f"Transcoding {asset['jobId']}...", 'yellow'))
            input_video = ffmpeg.input(ROOT_PATH + '/workspace/' + asset['keys'][0])
            input_audio = ffmpeg.input(ROOT_PATH + '/workspace/' + asset['keys'][1])
            ffmpeg \
                .concat(input_video, input_audio, v=1, a=1) \
                .output(ROOT_PATH + '/workspace/' + asset['assetId'] + '.mp4') \
                .run()
            log(colored(f"Transcoding Done: {asset['jobId']}...", 'yellow'))
    except Exception as error:
        log(colored(f"Error transcoding Asset Job: {asset['jobId']} =>\n{error}", 'red'))
