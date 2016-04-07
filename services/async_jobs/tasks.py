#!/usr/bin/env python
# encoding: utf-8
__author__ = 'rui'

import json
import random
import celery
import os.path
import requests
import logging
import gmail
from logging.handlers import RotatingFileHandler

push_key = ('OLYzDQA0lCtvhxR8VKPoE19D', 'rUsfEY9sHrqpzqFVENqmoSyffpKMyUSc')


def make_celery_logger(logs_path):
    profiling_formatter = logging.Formatter('%(asctime)s %(message)s')
    profiling_log_file = os.path.join(logs_path, 'GMissionAsyncJobs.log')
    profiling_handler = RotatingFileHandler(profiling_log_file, maxBytes=10000000, backupCount=1)
    profiling_handler.setFormatter(profiling_formatter)
    logger = logging.getLogger('GMissionAsyncJobsLog')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(profiling_handler)
    return logger


def filter_datetime(message_dict):
    if 'valid_until' in message_dict:
        message_dict['valid_until'] = message_dict['valid_until'].isoformat().split('.')[0]

    if 'created_on' in message_dict:
        message_dict['created_on'] = message_dict['created_on'].isoformat().split('.')[0]


CELERY_BROKER_URL = 'redis://docker-redis:6379/0'  # 'amqp://guest:guest@localhost:5672//'
celery_app = celery.Celery(broker=CELERY_BROKER_URL)
celery_app.conf.CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

logger = make_celery_logger(os.path.dirname(__file__))
logger.info('async tasks reloading...')


@celery_app.task()
def send_email(subject, body, receiver):
    logger.info('send email [%s] to : %s' % (subject, receiver,))
    gmail.send(subject, body, receiver)


def filter_datetime(message_dict):
    if 'valid_until' in message_dict:
        message_dict['valid_until'] = message_dict['valid_until'].isoformat().split('.')[0]

    if 'created_on' in message_dict:
        message_dict['created_on'] = message_dict['created_on'].isoformat().split('.')[0]


@celery_app.task()
def ios_push_task(alert, payload_dict, baidu_channel_id):
    filter_datetime(payload_dict)
    logger.info('applying ios push task: %s', ','.join(map(repr, [alert, payload_dict, baidu_channel_id])))
    message_dict = {"aps": {"alert": alert, "sound": "default", "badge": 1}, 'payload': payload_dict}

    push_by_php('ios', message_dict, baidu_channel_id)
    #logger.info('applying ios push task: %s done', ','.join(map(repr, [alert, payload_dict, baidu_channel_id])))


@celery_app.task()
def android_push_task(payload_dict, baidu_channel_id):
    filter_datetime(payload_dict)
    logger.info('applying android push task: %s', ','.join(map(repr, [payload_dict, baidu_channel_id])))
    push_by_php('android', payload_dict, baidu_channel_id)
    #logger.info('applying android push task: %s done', ','.join(map(repr, [payload_dict, baidu_channel_id])))


def push_by_php(platform, payload_dict, baidu_channel_id):
    app = 'gmission'
    push_url = 'http://docker-php-push/push.php'

    params = dict(app=app, platform=platform, message=json.dumps(payload_dict), channel_id=baidu_channel_id)
    if platform=='ios':
        params['deploy_status'] = 'both' #'production' # 'developing'

    r = requests.get(push_url, params=params)
    print r.url
    if r.status_code != 200:
        logger.info('async push task failed: %s', ','.join(map(repr, [app, platform, payload_dict, baidu_channel_id])))
    else:
        logger.info('async push task succeeded: %s', ','.join(map(repr, [app, platform, payload_dict, baidu_channel_id])))
    print r.text
