# -*- coding: utf-8 -*-
__author__ = 'chenzhao'
import datetime

import dateutil
import dateutil.tz

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
    if task.type in ('image', 'video'):
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


K_IN_KNN = 3
def assign_task_to_knn_workers(task):
    """:type task:Task"""
    location = task.location
    print 'assign_task_to_knn_workers: location', location
    lo, la = location.longitude, location.latitude
    # users = [u for u in get_nearest_n_users(lo, la, K_IN_KNN+1) if u.id!=task.requester_id][:K_IN_KNN]
    users = [u for u in User.query.all() if u.id!=task.requester_id]
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


def assign_global_request_to_workers(request):
    location = request.location
    users = [u for u in get_nearest_n_users(location.longitude, location.latitude, K_IN_KNN) if u!=request.requester]
    # users = [u for u in get_nearest_n_users(lo, la, K_IN_KNN) if u!=request.requester]
    send_request_messages('global request assign', request, users)
    pass


def find_similar_img():
    return 'test sample answer'
    pass


def try_answer_with_similar_img(task_request):
    answer_type = IndoorTaskAnswer if isinstance(task_request, IndoorTaskRequest) else GlobalTaskAnswer
    similar = find_similar_img(task_request.task.image_att)
    if similar:
        answer = answer_type(type='text', value=similar)
        db.session.add(answer)
    db.session.commit()
    pass


def try_answer_indoor_with_similar_questions(task_request):
    print 'try_answer_indoor_with_similar_questions', 'task_request', task_request.id
    similar_finder = User.query.get(2)
    print 'similar_finder', similar_finder
    similar_requests = IndoorTaskRequest.query.filter_by(task_id=task_request.task_id).all()
    for similar_request in similar_requests:
        print 'similar request:', similar_request.id
        if similar_request.end_time > datetime.datetime.now() - datetime.timedelta(seconds=60*10):
            for answer in similar_request.answers:
                if answer.worker.id != similar_finder.id:
                    auto_answer = IndoorTaskAnswer(type=answer.type,
                                                   value=answer.value,
                                                   location=answer.location,
                                                   option=answer.option,
                                                   request=task_request,
                                                   worker=similar_finder)
                    db.session.add(auto_answer)
                    print 'similar answer added', answer.id
            db.session.commit()


def try_answer_global_with_similar_questions(task_request):
    print 'try_answer_global_with_similar_questions', 'task_request', task_request.id
    similar_finder = User.query.get(2)
    print 'similar_finder', similar_finder
    similar_requests = GlobalTaskRequest.query.filter_by(task_id=task_request.task_id).all()
    for similar_request in similar_requests:
        print 'similar request:', similar_request.id
        if similar_request.end_time > datetime.datetime.now() - datetime.timedelta(seconds=60*10):
            for answer in similar_request.answers:
                if answer.worker.id != similar_finder.id:
                    auto_answer = GlobalTaskAnswer(type=answer.type,
                                                   value=answer.value,
                                                   location=answer.location,
                                                   option=answer.option,
                                                   request=task_request,
                                                   worker=similar_finder)
                    db.session.add(auto_answer)
                    print 'similar answer added', answer.id
            db.session.commit()



def create_global_with_new_task(j):
    location_paras = dict(map(lambda k:(k, j.get(k, '')), ['name', 'longitude', 'latitude']))
    location = GlobalLocation(**location_paras)
    db.session.add(location)
    db.session.flush()

    task_paras = dict(map(lambda k:(k, j.get(k, '')), ['brief', 'type', 'image_att']))
    task_paras['creator_id'] = j['requester_id']
    task_paras['location_id'] = location.id
    task = get_or_create(GlobalTask, **task_paras)
    db.session.add(task)

    request_paras = dict(map(lambda k:(k, j.get(k, '')), ['credit', 'requester_id', 'required_answer_count']))
    request_paras['task'] = task
    now = datetime.datetime.now()
    request_paras['begin_time'] = local_datetime(j.get('begin_time', now))
    request_paras['end_time'] = local_datetime(j.get('end_time', now+datetime.timedelta(days=1)))
    request_paras['location_id'] = location.id
    request_paras['status'] = 'open'
    task_request = GlobalTaskRequest(**request_paras)
    db.session.add(task_request)

    db.session.commit()

    if task.image_att:
        try_answer_with_similar_img(task_request)

    try_answer_global_with_similar_questions(task_request)

    assign_global_request_to_workers(task_request)
    return task_request


def create_indoor_with_new_task(j):
    task_paras = dict(map(lambda k:(k, j.get(k, '')), ['brief', 'type', 'location_id', 'image_att']))
    task_paras['creator_id'] = j['requester_id']
    task = get_or_create(IndoorTask, **task_paras)
    db.session.add(task)

    request_paras = dict(map(lambda k:(k, j.get(k, '')), ['credit', 'requester_id', 'location_id', 'required_answer_count']))
    request_paras['task'] = task
    request_paras['begin_time'] = local_datetime(j['begin_time'])
    request_paras['end_time'] = local_datetime(j['end_time'])
    request_paras['status'] = 'open'
    task_request = IndoorTaskRequest(**request_paras)
    db.session.add(task_request)

    db.session.commit()

    if task.image_att:
        try_answer_with_similar_img(task_request)

    assign_indoor_request_to_workers(task_request)

    try_answer_indoor_with_similar_questions(task_request)

    return task_request



if __name__=='__main__':
    check_expired()
