# -*- coding: utf-8 -*-
__author__ = 'chenzhao'

import datetime, time
from gmission.controllers.geo_controller import geo_distance
import math
import dateutil
import dateutil.tz
import errno
import os
from sets import Set
from gmission.controllers.payment_controller import pay_image, pay_choice
from gmission.models import *
import subprocess


def refresh_task_status():
    check_expired()
    check_enough_answer()
    pass


def check_expired():
    print 'check_expired'
    expired_requests = HIT.query.filter_by(status='open') \
        .filter(HIT.end_time <= datetime.datetime.now()).all()
    for expired_request in expired_requests:
        # print 'close expired', expired_request.id, expired_request.task.title
        close_task_and_pay_workers(expired_request)
        # fail_related_assignment(expired_request)


def check_enough_answer():
    print 'check_enough_answer'
    for request in HIT.query.filter_by(status='open').all():
        if len(request.answers) >= request.required_answer_count:
            # print 'close enough answer', request.id, request.task.title
            close_task_and_pay_workers(request)


def close_task_and_pay_workers(task):
    if task.type in ('image', 'video', 'mix'):
        pay_image(task)
    else:  # text multiple choice
        # pay_choice(task)
        pass
    task.status = 'closed'
    db.session.commit()


def assign_task_to_workers(task):
    # assign_task_to_all_nearby_workers(task)
    pass

#
# def assign_task_to_knn_workers(task, k_in_knn=10):
#     """:type task:Task"""
#     location = task.location
#     print 'assign_task_to_knn_workers: location', location
#     lo, la = location.longitude, location.latitude
#     users = [u for u in get_nearest_n_users(lo, la, k_in_knn + 1) if u.id != task.requester_id][:k_in_knn]
#     # users = [u for u in User.query.all() if u.id!=task.requester_id]
#     # send_request_messages(task, users)


def query_online_users():
    ten_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
    online_users = User.query.join(UserLastPosition) \
        .filter(UserLastPosition.user_id == User.id) \
        .filter(UserLastPosition.last_updated >= ten_minutes_ago).all()
    return online_users


# def assign_task_to_all_nearby_workers(task):
#     location = task.location
#     print 'assign_task_to_all_nearby_workers: location', location
#     lo, la = location.longitude, location.latitude
#     users = [u for u in get_nearby_users(lo, la) if u != task.requester]
#     # send_request_messages(task, users)
#     pass


def local_datetime(dt_string):
    if isinstance(dt_string, datetime.datetime):
        return dt_string
    dt = dateutil.parser.parse(dt_string)
    if dt.tzinfo:
        dt = dt.astimezone(dateutil.tz.tzlocal())
    return dt

if __name__ == '__main__':
    check_expired()
