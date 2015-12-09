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
from baidu_push import Channel
from logging.handlers import RotatingFileHandler

push_key = ('LQpGHpuTYA0lkjQj6zY3ZVfB', 'kkwpcFMTsKhdECYMbEOl7NF1hG2OGd4x')


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
def ios_push_task(alert, payload_dict, baidu_user_id):
    filter_datetime(payload_dict)
    logger.info('applying ios push task: %s', ','.join(map(repr, [alert, payload_dict, baidu_user_id])))
    message_dict = {"aps": {"alert": alert, "sound": "default", "badge": 1}, 'payload': payload_dict, 'app_name': app}

    push_by_native('ios', message_dict, baidu_user_id)
    logger.info('applying ios push task: %s done', ','.join(map(repr, [alert, payload_dict, baidu_user_id])))


@celery_app.task()
def android_push_task(payload_dict, baidu_user_id):
    filter_datetime(payload_dict)
    logger.info('applying android push task: %s', ','.join(map(repr, [payload_dict, baidu_user_id])))
    push_by_native('android', payload_dict, baidu_user_id)
    logger.info('applying android push task: %s done', ','.join(map(repr, [payload_dict, baidu_user_id])))


def push_by_native(platform, payload_dict, baidu_user_id):
    (api_key, secret_key) = push_key
    c = Channel(api_key, secret_key)
    push_by_native_inner(c, platform, payload_dict, baidu_user_id)


def push_by_native_inner(channel, platform, payload_dict, baidu_user_id):
    optional = dict()
    message_key = str(random.randint(10000000, 999999999))  # useful only if platform == 'android':
    if platform == 'ios':
        optional[Channel.DEVICE_TYPE] = Channel.DEVICE_IOS
        optional[Channel.MESSAGE_TYPE] = Channel.PUSH_NOTIFICATION
        optional['deploy_status'] = 2
    else:
        optional[Channel.DEVICE_TYPE] = Channel.DEVICE_ANDRIOD
        optional[Channel.MESSAGE_TYPE] = Channel.PUSH_MESSAGE

    optional[Channel.USER_ID] = baidu_user_id
    ret = channel.pushMessage(Channel.PUSH_TO_USER, payload_dict, message_key, optional)
    if ret:
        logger.info('async push task success: %s',
                    ','.join(map(repr, [platform, payload_dict, baidu_user_id])))
    else:
        logger.info('async push task failed: %s',
                    ','.join(map(repr, [platform, payload_dict, baidu_user_id])))
