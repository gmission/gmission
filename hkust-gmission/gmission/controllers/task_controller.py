# -*- coding: utf-8 -*-
__author__ = 'chenzhao'
import datetime, time

import math
import dateutil
import dateutil.tz
from sets import Set
from gmission.controllers.payment_controller import pay_image, pay_choice
from gmission.controllers.message_controller import send_request_messages
from gmission.models import *


def refresh_task_status():
    check_expired()
    check_enough_answer()
    pass


def check_expired():
    print 'check_expired'
    expired_requests = Task.query.filter_by(status='open') \
        .filter(Task.end_time <= datetime.datetime.now()).all()
    for expired_request in expired_requests:
        # print 'close expired', expired_request.id, expired_request.task.brief
        close_task_and_pay_workers(expired_request)


def check_enough_answer():
    print 'check_enough_answer'
    for request in Task.query.filter_by(status='open').all():
        if len(request.answers) >= request.required_answer_count:
            # print 'close enough answer', request.id, request.task.brief
            close_task_and_pay_workers(request)


def close_task_and_pay_workers(task):
    if task.type in ('image', 'video', 'mix'):
        pay_image(task)
    else:  # text multiple choice
        # pay_choice(task)
        pass
    task.status = 'closed'
    delete_related_messages(task)
    db.session.commit()


def delete_related_messages(task):
    Message.query.filter_by(att_type=task.__class__.__name__,
                            attachment=task.id).update({'status': 'deleted'}, synchronize_session=False)
    db.session.commit()


def assign_task_to_workers(task):
    assign_task_to_knn_workers(task)
    pass

def get_current_profile(user):
    traces = PositionTrace.query.order_by(PositionTrace.created_on.desc()).filter(PositionTrace.user_id==user.id).limit(20)


    worker_profile = WorkerProfile(x=0,
                                   y=0,
                                   min_angle=0,
                                   max_angle=0,
                                   velocity=0,
                                   reliability=1,
                                   worker=user)


    end_point, traces = traces[0], traces[1:]
    min_angle = 0
    max_angle = 0
    last_point = end_point
    velocities = Set()

    for index, t in enumerate(traces):
        arrivalAngle = geo_angle(t.longitude, t.latitude, end_point.longitude, end_point.latitude)
        if arrivalAngle > max_angle and arrivalAngle > min_angle:
            max_angle = arrivalAngle
        if arrivalAngle < max_angle and arrivalAngle < min_angle:
            min_angle = arrivalAngle

        velocity = 0.001

        distance = geo_distance(t.longitude, t.latitude, last_point.longitude, last_point.latitude)
        time_interval = time.mktime(last_point.created_on.timetuple()) - time.mktime(t.created_on.timetuple())
        if time_interval != 0:
            velocity = distance / time_interval
        last_point = t
        velocities.add(velocity)

    min_angle = min_angle + math.pi
    max_angle = max_angle + math.pi

    if min_angle > math.pi * 2:
        max_angle = max_angle - 2 * math.pi
        min_angle = min_angle - 2 * math.pi


    worker_profile.max_angle = max_angle
    worker_profile.min_angle = min_angle
    worker_profile.velocity = float((max(velocities) + min(velocities))/2)

    # user_traces = [(t.longitude, t.latitude, t.created_on) for t in traces]
    return [worker_profile.velocity, velocities]

def geo_angle(startPointLong, startPointLati, endPointLong, endPointLati):
    angle = math.atan2(endPointLati - startPointLati, endPointLong - startPointLong)
    if angle < 0:
        angle = angle + 2 * math.pi
    return angle



K_IN_KNN = 10
def assign_task_to_knn_workers(task):
    """:type task:Task"""
    location = task.location
    print 'assign_task_to_knn_workers: location', location
    lo, la = location.longitude, location.latitude
    users = [u for u in get_nearest_n_users(lo, la, K_IN_KNN+1) if u.id!=task.requester_id][:K_IN_KNN]
    # users = [u for u in User.query.all() if u.id!=task.requester_id]
    send_request_messages(task, users)


def assign_task_to_all_nearby_workers(task):
    location = task.location
    print 'assign_task_to_all_nearby_workers: location', location
    lo, la = location.longitude, location.latitude
    users = [u for u in get_nearby_users(lo, la) if u!=task.requester]
    send_request_messages(task, users)
    pass


def local_datetime(dt_string):
    if isinstance(dt_string, datetime.datetime):
        return dt_string
    dt = dateutil.parser.parse(dt_string)
    if dt.tzinfo:
        dt = dt.astimezone(dateutil.tz.tzlocal())
    return dt



def geo_distance(long1, lati1, long2, lati2):
    return (long1-long2)**2+(lati1-lati2)**2
    pass


# 1km is about 0.01, 1m is 0.00001
def get_nearest_n_users(longitude, latitude, n, r=0.00001):
    P = UserLastPosition

    in_rect = (P.longitude>=longitude-r) & (P.longitude<=longitude+r) \
                   & (P.latitude>=latitude-r) & (P.latitude<=latitude+r)
    c = P.query.filter(in_rect).count()

    print 'KNN', n, r, c

    if c<n and r<0.1:
        return get_nearest_n_users(longitude, latitude, n, r*2)

    ps = sorted(P.query.filter(in_rect).all(), key=lambda p: geo_distance(p.longitude, p.latitude, longitude, latitude))
    return [p.user for p in ps[:n]]


def get_nearby_users(longitude, latitude):
    r = 0.05
    P = UserLastPosition

    in_rect = (P.longitude>=longitude-r) & (P.longitude<=longitude+r) \
              & (P.latitude>=latitude-r) & (P.latitude<=latitude+r)
    c = P.query.filter(in_rect).count()

    print 'user in 5km bound:', c

    # ps = sorted(P.query.filter(in_rect).all(), key=lambda p: geo_distance(p.longitude, p.latitude, longitude, latitude))
    return [p.user for p in P.query.filter(in_rect).all()]


if __name__=='__main__':
    check_expired()
