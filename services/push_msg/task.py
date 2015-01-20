# -*- coding:utf8 -*-

__author__ = 'chenzhao'

import json
import random
import celery
import os.path
import requests
import logging
from logging.handlers import RotatingFileHandler



def make_push_msg_logger(logs_path):
    profiling_formatter = logging.Formatter('%(asctime)s %(message)s')
    profiling_log_file = os.path.join(logs_path, 'GMissionPushMsg.log')
    profiling_handler = RotatingFileHandler(profiling_log_file, maxBytes=10000000, backupCount=1)
    profiling_handler.setFormatter(profiling_formatter)
    logger = logging.getLogger('GMissionPushMsg')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(profiling_handler)
    return logger

CELERY_BROKER_URL = 'redis://docker-redis:6379/0'  # 'amqp://guest:guest@localhost:5672//'
celery_app = celery.Celery(broker=CELERY_BROKER_URL)
celery_app.conf.CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

# print 'CELERY_BROKER_URL', CELERY_BROKER_URL

logger = make_push_msg_logger(os.path.dirname(__file__))


def filter_datetime(message_dict):
    if 'valid_until' in message_dict:
        message_dict['valid_until'] = message_dict['valid_until'].isoformat().split('.')[0]

    if 'created_on' in message_dict:
        message_dict['created_on'] = message_dict['created_on'].isoformat().split('.')[0]


@celery_app.task()
def ios_push_task(app, alert, payload_dict, baidu_user_id):
    filter_datetime(payload_dict)
    logger.info('applying ios push task: %s', ','.join(map(repr, [app, alert, payload_dict, baidu_user_id])))
    message_dict = {"aps":{"alert":alert, "sound":"", "badge":0}, 'payload':payload_dict}

    push_by_php(app, 'ios', message_dict, baidu_user_id)

@celery_app.task()
def android_push_task(app, payload_dict, baidu_user_id):
    filter_datetime(payload_dict)
    logger.info('applying android push task: %s', ','.join(map(repr, [app, payload_dict, baidu_user_id])))
    push_by_php(app, 'android', payload_dict, baidu_user_id)


def push_by_php(app, platform, payload_dict, baidu_user_id):
    push_url = 'http://docker-php-push/baiduPush/push.php'

    params = dict(app=app, platform=platform, message=json.dumps(payload_dict), user_id=baidu_user_id)
    if platform=='android':
        msgkey = str(random.randint(10000000, 999999999))  # useful only if platform == 'android':
        params['message_key'] = msgkey
    elif platform=='ios':
        params['deploy_status'] = 'production'
    r = requests.get(push_url, params=params)
    print r.url
    if r.status_code != 200:
        logger.info('async push task failed: %s', ','.join(map(repr, [app, platform, payload_dict, baidu_user_id])))
    print r.text


def test():
    message_dict = {"aps":{"alert":"to ios", "sound":"", "badge":0}, "anotherfield":"somethingelse",
                    "adictfield":{'i':123, 's':'adf', 'b':True, 'f':123.4567}}

    baidu_user_id = '1036560747834284895'
    push_by_php('szww', 'android', message_dict, baidu_user_id)
    return
    baidu_user_id = '1044981726564561550'  # 943591357588735187
    baidu_user_id = '943591357588735187'
    baidu_user_id = '1036560747834284895'  # 943591357588735187
    push_by_php('szww', 'ios', message_dict, baidu_user_id)

    pass


if __name__=='__main__':
    test()
