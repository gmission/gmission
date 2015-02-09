# -*- coding:utf8 -*-

__author__ = 'chenzhao'

import sys
import json
import time
from datetime import datetime, timedelta

import threading

import os.path
import requests
import logging
from logging.handlers import RotatingFileHandler
import gmail

url_root = 'http://docker-gmission:9090/'
url_root = 'http://lccpu3.cse.ust.hk/gmission/'
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


class AllMatch(set):  # Universal set - match everything
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
                       args=(), name="event", kwargs={}):
        self.mins = conv_to_set(min)
        self.hours= conv_to_set(hour)
        self.days = conv_to_set(day)
        self.months = conv_to_set(month)
        self.dow = conv_to_set(dow)
        self.action = action
        self.name = name
        self.args = args
        self.kwargs = kwargs
        print 'new event:', name , 'mins:', min, 'hours:', hour, 'action:', action.__name__
        sys.stdout.flush()

    def matchtime(self, t):
        """Return True if this event should trigger at the specified datetime"""
        return ((t.minute     in self.mins) and
                (t.hour       in self.hours) and
                (t.day        in self.days) and
                (t.month      in self.months) and
                (t.weekday()  in self.dow))

    def check(self, t):
        print 'checking', self.mins, self.hours, t.minute, t.hour
        if self.matchtime(t):
            a_new_thread = threading.Thread(target=self.action)
            a_new_thread.start()
            print self.name, 'matched, running in a new thread ', a_new_thread.ident


def report_error(msg):
    gmail.send_many('gmission cron job error!', msg, ['chenzhao.sg@gmail.com'])
    # gmail.send_many('gmission cron job error!', msg, ['chenzhao.sg@gmail.com', 'haidaoxiaofei@gmail.com'])
    pass


class CronTab(object):
    def __init__(self, *events):
        self.events = events

    def run(self):
        while datetime.now().second > 50:  # make sure there is enough time
            time.sleep(1)
        print 'Cron begin at', datetime.now()
        while 1:
            current_minute = datetime(*datetime.now().timetuple()[:5])
            print 'check for', current_minute
            for e in self.events:
                try:
                    e.check(current_minute)
                except Exception as e:
                    print 'cron failed', repr(e)
                    sys.stdout.flush()
                    report_error('Exception when running jobs: ' + repr(e))
                    raise e
            now = datetime.now()
            next_minute = current_minute + timedelta(minutes=1)
            print 'now:', now
            print 'next minute:', next_minute
            if now > next_minute:
                print 'weird'
                report_error('Too long to start new jobs!')
                return
            else:
                seconds_to_sleep = (next_minute - now).seconds + 10
                print 'sleep until next minute', seconds_to_sleep
                time.sleep(seconds_to_sleep)  # make sure sleep to the next minute



def gen_taking_picture():
    logger.info("generating taking_picture:")

    lon, lat = 114.274277, 22.340725
    location = dict(name='HKUST Firebird', longitude=lon, latitude=lat)
    new_task = dict(type='image', brief='Take a picture of the Firebird!',
                    credit=10, required_answer_count=5, requester_id=1, location=location)
    r = rest_post('task', new_task)
    r.json()


def gen_canteen_menus():
    logger.info("generating canteen_menus tasks:")
    lon, lat = 114.275063, 22.340898
    location = dict(name='Canteen LG7', longitude=lon, latitude=lat)
    new_task = dict(type='mix', brief="What's the menu of LG7 today?",
                    credit=10, required_answer_count=5, requester_id=1, location=location)
    rest_post('task', new_task)

    lon, lat = 114.275288, 22.340284
    location = dict(name='Canteen LG1', longitude=lon, latitude=lat)
    new_task = dict(type='mix', brief="What's the menu of LG1 today?",
                    credit=10, required_answer_count=5, requester_id=1, location=location)
    rest_post('task', new_task)



def gen_testing_tasks():
    current_time = datetime.now().isoformat().split('.')[0]
    a_quarter_later = (datetime.now() + timedelta(minutes=15)).isoformat().split('.')[0]
    lon, lat =  22.335292, 114.264655
    lon, lat = lat,lon
    location = dict(name='Tower B Carpark', longitude=lon, latitude=lat)
    new_task = dict(type='image', brief="take a photo at Tower B Carpark", begin_time=current_time,
                    end_time=a_quarter_later,
                    credit=10, required_answer_count=1000, requester_id=1, location=location, beta=0.3)
    rest_post('task', new_task)


    lon, lat =  22.334439, 114.263126
    lon, lat = lat,lon
    location = dict(name='Tennis Court ABC', longitude=lon, latitude=lat)
    new_task = dict(type='image', brief="take a photo at Tennis Court ABC",begin_time=current_time,
                    end_time=a_quarter_later,
                    credit=10, required_answer_count=1000, requester_id=1, location=location, beta=0.3)
    rest_post('task', new_task)

    lon, lat =  22.333295, 114.262863
    lon, lat = lat,lon
    location = dict(name='South Gate Bus Stop', longitude=lon, latitude=lat)
    new_task = dict(type='image', brief="take a photo at South Gate Bus Stop",begin_time=current_time,
                    end_time=a_quarter_later,
                    credit=10, required_answer_count=1000, requester_id=1, location=location, beta=0.3)
    rest_post('task', new_task)

    lon, lat = 22.334982, 114.263845
    lon, lat = lat,lon
    location = dict(name='Garden new Lift32', longitude=lon, latitude=lat)
    new_task = dict(type='image', brief="take a photo at Garden new Lift32",begin_time=current_time,
                    end_time=a_quarter_later,
                    credit=10, required_answer_count=1000, requester_id=1, location=location, beta=1)
    rest_post('task', new_task)

    lon, lat =  22.335841, 114.263714
    lon, lat = lat,lon

    location = dict(name='Engineering Commons', longitude=lon, latitude=lat)
    new_task = dict(type='image', brief="take a photo at Engineering Commons",begin_time=current_time,
                    end_time=a_quarter_later,
                    credit=10, required_answer_count=1000, requester_id=1, location=location, beta=0.5)
    rest_post('task', new_task)


def gen_firebird_tasks():
    current_time = datetime.now().isoformat().split('.')[0]
    a_quarter_later = (datetime.now() + timedelta(minutes=15)).isoformat().split('.')[0]
    lon, lat = 22.337507, 114.262970
    lon, lat = lat,lon
    location = dict(name='FireBird', longitude=lon, latitude=lat)
    new_task = dict(type='image', brief="take a photo at FireBird", begin_time=current_time,
                    end_time=a_quarter_later,
                    credit=10, required_answer_count=1000, requester_id=1, location=location, beta=0.9)
    rest_post('task', new_task)


    lon, lat = 22.337029, 114.263367
    lon, lat = lat,lon
    location = dict(name='Hang Seng Bank', longitude=lon, latitude=lat)
    new_task = dict(type='image', brief="take a photo at Hang Seng Bank",begin_time=current_time,
                    end_time=a_quarter_later,
                    credit=10, required_answer_count=1000, requester_id=1, location=location, beta=0.2)
    rest_post('task', new_task)

    lon, lat = 22.337942, 114.263176
    lon, lat = lat,lon
    location = dict(name='Bank of East Asia', longitude=lon, latitude=lat)
    new_task = dict(type='image', brief="take a photo at Bank of East Asia",begin_time=current_time,
                    end_time=a_quarter_later,
                    credit=10, required_answer_count=1000, requester_id=1, location=location, beta=0.2)
    rest_post('task', new_task)

    lon, lat = 22.338631, 114.262025
    lon, lat = lat,lon
    location = dict(name='North Bus Stop', longitude=lon, latitude=lat)
    new_task = dict(type='image', brief="take a photo at North Bus Stop",begin_time=current_time,
                    end_time=a_quarter_later,
                    credit=10, required_answer_count=1000, requester_id=1, location=location, beta=0.1)
    rest_post('task', new_task)

    lon, lat = 22.338424, 114.263010
    lon, lat = lat,lon
    location = dict(name='Under Ground Car Park', longitude=lon, latitude=lat)
    new_task = dict(type='image', brief="take a photo at Under Ground Car Park",begin_time=current_time,
                    end_time=a_quarter_later,
                    credit=10, required_answer_count=1000, requester_id=1, location=location, beta=0.3)
    rest_post('task', new_task)

def run():
    c = CronTab(
        # Event(gen_taking_picture, name='firebird', min=[0, 30], hour=range(10, 23)),
        # Event(gen_canteen_menus, name='menu', min=[0, 49], hour=[11, 17]),
        Event(gen_testing_tasks, name='testing', min=[5, 20, 35, 50], hour=range(13, 19)),
        # Event(call_assign, name='call testing', min=range(0,61,4), hour=range(15, 19)),
    )
    c.run()
    pass


def runTimes(minute, total_times, target):
    runned_times = 0
    while runned_times<total_times:
        target()
        t = threading.Thread(target=target)
        t.run()
        time.sleep(60.0*minute)



if __name__ == '__main__':
    print 'cron start'
    # runTimes(0.5, 10, call_assign)
    # runTimes(0.5, 10, call_assign)
    # gen_testing_tasks()
    # sys.stdout.flush()
    gen_firebird_tasks()
    # run()
