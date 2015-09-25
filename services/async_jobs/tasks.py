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
