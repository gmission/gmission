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

url_root = 'http://docker-gmission:9090/'
# url_root = 'http://hkust-gmission.cloudapp.net:9090/'#;'http://192.168.59.106:9090/'


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
        # print 'checking', self.mins, self.hours, t.minute, t.hour
        if self.matchtime(t):
            self.action(*self.args, **self.kwargs)


class CronTab(object):
    def __init__(self, *events):
        self.events = events

    def run(self):
        t = datetime(*datetime.now().timetuple()[:5])
        while 1:
            for e in self.events:
                try:
                    e.check(t)
                except Exception as e:
                    print 'cron failed', repr(e)
                    sys.stdout.flush()
            t += timedelta(minutes=1)
            while datetime.now() < t:
                time.sleep((t - datetime.now()).seconds)


def gen_taking_picture():
    logger.info("generating taking_picture:")

    lon, lat = 114.274277, 22.340725
    location = dict(name='HKUST Firebird', longitude=lon, latitude=lat)
    new_task = dict(type='mix', brief='Take a picture of the Firebird!',
                    credit=10, required_answer_count=5, requester_id=1, location=location)
    r = rest_post('task', new_task)
    r.json()


def gen_canteen_menus():
    logger.info("generating canteen_menus tasks:")
    lon, lat = 114.274277, 22.340725
    location = dict(name='Canteen LG7', longitude=lon, latitude=lat)
    new_task = dict(type='mix', brief="What's the menu of LG7 today?",
                    credit=10, required_answer_count=5, requester_id=1, location=location)
    rest_post('task', new_task)

    location = dict(name='Canteen LG1', longitude=lon, latitude=lat)
    new_task = dict(type='mix', brief="What's the menu of LG1 today?",
                    credit=10, required_answer_count=5, requester_id=1, location=location)
    rest_post('task', new_task)


def run():
    c = CronTab(
        Event(gen_taking_picture, min=[0, 30], hour=range(10, 23)),
        Event(gen_canteen_menus, min=[0], hour=[11, 17]),
    )
    c.run()
    pass


if __name__ == '__main__':
    print 'cron start'
    sys.stdout.flush()
    run()
