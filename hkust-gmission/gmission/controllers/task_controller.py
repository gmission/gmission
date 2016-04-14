# -*- coding: utf-8 -*-
__author__ = 'chenzhao'

from gmission.controllers.message_controller import send_request_messages, send_request_message
import dateutil
import dateutil.tz, dateutil.parser
from gmission.controllers.payment_controller import pay_image, pay_choice
from gmission.controllers.geo_controller import get_nearest_n_users, get_nearest_n_users_from_index
from gmission.models import *
import time
import requests
from gmission.config import index_server


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
    # assign_task_to_all_possible_workers(task)
    assign_task_to_knn_workers(task, k_in_knn=5000)
    pass


def assign_task_to_knn_workers(task, k_in_knn=10):
    """:type task:Task"""
    location = task.location
    print 'assign_task_to_knn_workers: location', location
    lo, la = location.coordinate.longitude, location.coordinate.latitude

    t = time.time()
    for iter in range(100):
        users_index = [u for u in get_nearest_n_users_from_index(lo, la, k_in_knn + 1, 0.01, use_rtree=True) if
                       u.id != task.requester_id][:k_in_knn]
    print('rtree assign task cost: %s' % (time.time() - t))

    t = time.time()
    for iter in range(100):
        users = [u for u in get_nearest_n_users_from_index(lo, la, k_in_knn + 1, 0.01, use_rtree=False) if
                 u.id != task.requester_id][:k_in_knn]
    print('linear assign task cost: %s' % (time.time() - t))

    print 'index:', len(users_index), 'naive:', len(users)
    user_id = [u.id for u in users]
    for user in users_index:
        if user.id not in user_id:
            print 'not in: ', user.id
        else:
            user_id.remove(user.id)
    print 'remain:', user_id
    # users = [u for u in User.query.all() if u.id!=task.requester_id]
    print 'assigned worker number: ', len(users)
    send_request_messages(task, users)


def assign_task_to_all_possible_workers(task):
    users = [u for u in User.query.all() if u != task.requester]
    send_request_messages(task, users)


def assign_all_tasks_by_algorithm(method, current_time):
    headers = {'content-type': 'application/json', 'accept': 'application/json'}
    matches = requests.post(
        url=index_server.server_addr + '/Index/actions/assignment/' + method + '/' + str(current_time),
        headers=headers).json()
    for match in matches:
        # print match, match[u'taskId'], match[u'workerId']
        task = HIT.query.filter(HIT.id == match[u'taskId']).first()
        worker = User.query.filter(User.id == match[u'workerId']).first()
        if task is not None and worker is not None:
            send_request_message(task, worker)
    return matches


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
#     send_request_messages(task, users)
#     pass


def credit_process(task):
    user = task.requester
    credit = task.credit
    user.credit -= credit
    db.session.commit()


def local_datetime(dt_string):
    if isinstance(dt_string, datetime.datetime):
        return dt_string
    dt = dateutil.parser.parse(dt_string)
    if dt.tzinfo:
        dt = dt.astimezone(dateutil.tz.tzlocal())
    return dt


def push_worker_to_campaign_user(answer):
    if answer is None:
        return
    if answer.hit.campaign is None:
        return
    users = CampaignUser.query.filter(CampaignUser.campaign_id == answer.hit.campaign_id).filter(
        CampaignUser.user_id == answer.worker_id).all()
    if len(users) > 0:
        return
    role = get_or_create(CampaignRole, name='participant', description='participant')
    campaignuser = get_or_create(CampaignUser, user_id=answer.worker_id, campaign_id=answer.hit.campaign_id,
                                 role_id=role.id)
    db.session.commit()
    return


if __name__ == '__main__':
    check_expired()
