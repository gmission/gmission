# -*- coding:utf8 -*-

__author__ = 'chenzhao'

from datetime import datetime, timedelta
import sys
import json
import time
import os.path
import requests
import logging
from logging.handlers import RotatingFileHandler

url_root = 'http://docker-gmission:9090'

# PWD = os.path.dirname(__file__)
# test_lib_path = os.path.join(os.path.abspath(PWD), '../../hkust-gmission/test')
# sys.path.append(test_lib_path)

# from unit_test import *


def post(urlpath, **kw):
    url = url_root+urlpath
    json_data = json.dumps(kw)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    # http_debug('POST', url, json_data)
    resp = requests.post(url, data=json_data, headers=headers)
    # http_debug('Response:', resp.status_code, resp.content[:60], '...')
    return resp

def rest_post(name, obj_dict):
    return post('rest/'+name, **obj_dict)


def make_cron_logger(logs_path):
    profiling_formatter = logging.Formatter('%(asctime)s %(message)s')
    profiling_log_file = os.path.join(logs_path, 'GMissionCron.log')
    profiling_handler = RotatingFileHandler(profiling_log_file, maxBytes=10000000, backupCount=1)
    profiling_handler.setFormatter(profiling_formatter)
    logger = logging.getLogger('GMissionCron')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(profiling_handler)
    return logger

logger = make_cron_logger(os.path.dirname(__file__))


class AllMatch(set): # Universal set - match everything
    def __contains__(self, item):
        return True

allMatch = AllMatch()


def conv_to_set(obj):  # Allow single integer to be provided
    if isinstance(obj, (int,long)):
        return set([obj])  # Single item
    if not isinstance(obj, set):
        obj = set(obj)
    return obj


# The actual Event class
class Event(object):
    def __init__(self, action, min=allMatch, hour=allMatch,
                       day=allMatch, month=allMatch, dow=allMatch,
                       args=(), kwargs={}):
        self.mins = conv_to_set(min)
        self.hours= conv_to_set(hour)
        self.days = conv_to_set(day)
        self.months = conv_to_set(month)
        self.dow = conv_to_set(dow)
        self.action = action
        self.args = args
        self.kwargs = kwargs
        print 'new event:', 'mins:', min, 'hours:', hour, 'action:', action.__name__
        sys.stdout.flush()

    def matchtime(self, t):
        """Return True if this event should trigger at the specified datetime"""
        return ((t.minute     in self.mins) and
                (t.hour       in self.hours) and
                (t.day        in self.days) and
                (t.month      in self.months) and
                (t.weekday()  in self.dow))

    def check(self, t):
        if self.matchtime(t):
            self.action(*self.args, **self.kwargs)


class CronTab(object):
    def __init__(self, *events):
        self.events = events

    def run(self):
        t = datetime(*datetime.now().timetuple()[:5])
        while 1:
            for e in self.events:
                e.check(t)

            t += timedelta(minutes=1)
            while datetime.now() < t:
                time.sleep((t - datetime.now()).seconds)


def gen_taking_picture():
    logger.info("generating taking_picture:")
    print "generating taking_picture tasks:"
    sys.stdout.flush()
    user = dict(email='scheduler@gmission.com', password='1234567', name='a mysterious person')
    rest_post('user', user)
    u = post('user/login', **user).json()

    lon, lat = 114.274277, 22.340725
    bound = dict(left_top_longitude=lon-1,
                 left_top_latitude=lat-1,
                 right_bottom_longitude=lon+1,
                 right_bottom_latitude=lat+1)
    location = dict(name='HKUST', longitude=lon, latitude=lat, bound=bound)
    new_task = dict(type='mix',
                    brief='Take a picture here!',
                    credit=10,
                    required_answer_count=5,
                    requester_id=u['id'],
                    location=location)
    r = rest_post('task', new_task)
    task_j = r.json()
    assert task_j['id'] and task_j['begin_time'] and task_j['end_time'] and task_j['location_id']
    assert task_j['status'] == 'open'
    assert task_j['type'] == new_task['type']
    assert task_j['credit'] == new_task['credit']
    assert task_j['requester_id'] == new_task['requester_id']


def gen_canteen_menus():
    logger.info("generating canteen_menus tasks:")
    print "generating canteen_menus tasks:"
    sys.stdout.flush()
    user = dict(email='scheduler@gmission.com', password='1234567', name='a mysterious person')
    rest_post('user', user)
    u = post('user/login', **user).json()

    lon, lat = 114.274277, 22.340725
    bound = dict(left_top_longitude=lon-1,
                 left_top_latitude=lat-1,
                 right_bottom_longitude=lon+1,
                 right_bottom_latitude=lat+1)
    location = dict(name='Canteen LG7', longitude=lon, latitude=lat, bound=bound)
    new_task = dict(type='mix',
                    brief="What's the menu today?",
                    credit=10,
                    required_answer_count=5,
                    requester_id=u['id'],
                    location=location)
    r = rest_post('task', new_task)
    task_j = r.json()
    assert task_j['id'] and task_j['begin_time'] and task_j['end_time'] and task_j['location_id']
    assert task_j['status'] == 'open'
    assert task_j['type'] == new_task['type']
    assert task_j['credit'] == new_task['credit']
    assert task_j['requester_id'] == new_task['requester_id']


def run():
    c = CronTab(
        Event(gen_taking_picture, min=[0, 30], hour=range(10, 19)),
        Event(gen_canteen_menus, min=[0], hour=[11, 17]),
    )
    c.run()
    pass


if __name__ == '__main__':
    while True:
        print 'cron start'
        sys.stdout.flush()
        try:
            run()
        except Exception as e:
            print 'cron failed', e
            sys.stdout.flush()
