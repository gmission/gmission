# -*- coding: utf-8 -*-


__author__ = 'chenzhao'

from gmission.config import is_production
from gmission.models import *
from gmission.flask_app import app, ROOT
import sys
import os.path
service_path = os.path.join(ROOT, '../../services')
sys.path.append(service_path)
from push_msg.task import ios_push_task, android_push_task, send_email

import itertools


logger = app.logger
push_msg_logger = app.push_msg_logger


def send_reg_email_async(user):
    subject = "Welcome to GMission!"
    body = """Hi %s,

Welcome to GMission. Remember to check our website: http://gmissionhkust.com for updates :)

Best regards,
GMission team from HKUST """ % (user.name, )
    send_email.apply_async((subject, body, user.email))
    push_msg_logger.info('sent to MQ %s', repr(user.email))


def get_baidu_infos_of_location(location):
    P = UserLastPosition
    b = location.bound
    """
    @type b LocationBound
    """
    user_ids = [u.user_id for u in P.query.filter(P.latitude>b.left_top_latitude, P.latitude<b.right_bottom_latitude,
                           P.longitude>b.left_top_longitude, P.longitude<b.right_bottom_longitude).all()]

    print location, user_ids

    baidu_users = BaiduPushInfo.query.filter(BaiduPushInfo.is_valid == True, BaiduPushInfo.user_id.in_(user_ids) ).all()
    return baidu_users


def get_baidu_infos_of_locations(locations):
    testing_location = Location.query.filter_by(name=u'世界之窗').first()
    if testing_location in locations:
        return BaiduPushInfo.query.filter(BaiduPushInfo.is_valid == True).all()
    return set(list(itertools.chain(*[get_baidu_infos_of_location(location) for location in locations])))


def push_notice_async(notice):

    def apply_push_task_for_notice(baidu_push_info, notice_dict):
        # if is_production():
        if baidu_push_info.type=='android':
            android_push_task.apply_async(('szww', notice_dict, baidu_push_info.baidu_user_id))
        elif baidu_push_info.type=='ios':
            ios_push_task.apply_async(('szww', notice_dict['title'], notice_dict, baidu_push_info.baidu_user_id))
        push_msg_logger.info('send to MQ %s %s', repr(notice_dict), repr(baidu_push_info.baidu_user_id))


    baidu_infos = get_baidu_infos_of_locations(notice.locations)
    print notice.locations, baidu_infos
    dict_fields = ['id','type','title','content','attachment_id','sender_id','valid_until','created_on']
    notice_dict = dict( [(field, getattr(notice, field)) for field in dict_fields] )
    notice_dict['location_ids'] = [id for id in notice.location_ids]

    for info in baidu_infos:
        apply_push_task_for_notice(info, notice_dict)


def push_user_async(user):

    def apply_push_task_for_user(baidu_push_info, user_dict):
        # if is_production():
        if baidu_push_info.type=='android':
            android_push_task.apply_async(('szww', user_dict, baidu_push_info.baidu_user_id))
        elif baidu_push_info.type=='ios':
            ios_push_task.apply_async(('szww', 'user', user_dict, baidu_push_info.baidu_user_id))
        # print 'send to MQ', repr(user_dict), repr(baidu_push_info)
        push_msg_logger.info('send to MQ %s %s', repr(user_dict), repr(baidu_push_info.baidu_user_id))

    bindlist = BaiduPushInfo.query.filter(BaiduPushInfo.user_id == user.id,
                                          BaiduPushInfo.is_valid == True).all()
    user_dict = dict(id=user.id, name=user.name.encode('utf-8'), email=user.email.encode('utf-8'),
                credit=user.credit, created_on=user.created_on,
             device_info_id=user.device_info_id, profile_id=user.profile_id)

    for info in bindlist:
        apply_push_task_for_user(info, user_dict)


def push_message_async(message_obj):
    bindlist = BaiduPushInfo.query.filter(BaiduPushInfo.user_id == message_obj.receiver_id,
                                          BaiduPushInfo.is_valid == True).all()
    android_message_dict = dict(id=message_obj.id, type=message_obj.type, content=message_obj.content.encode('utf-8'),
                att_type=message_obj.att_type, attachment=message_obj.attachment, sender_id=message_obj.sender_id,
             receiver_id=message_obj.receiver_id, status=message_obj.status)

    ios_alert = android_message_dict['content']
    ios_message_dict = dict(type=message_obj.type, att=message_obj.attachment)
    for info in bindlist:
        if info.type == 'android':
            android_push_task.apply_async(('gmissionhkust', android_message_dict, info.baidu_user_id))
            push_msg_logger.info('sent to MQ %s %s', repr(android_message_dict), repr(info.baidu_user_id))
        elif info.type == 'ios':
            ios_push_task.apply_async(('gmissionhkust', ios_alert, ios_message_dict, info.baidu_user_id))
            push_msg_logger.info('sent to MQ %s %s', repr(ios_message_dict), repr(info.baidu_user_id))


def save_and_push_msg(msg, commit=True):
    db.session.add(msg)
    if commit:
        db.session.commit()
    else:
        db.session.flush()
    push_message_async(msg)


# def send_request_messages(task, users):
#     msg_type = 'task assignment'
#     # scheduler = User.query.get(1)
#     msg_content = u'在"%s"有一个新任务!' % (task.location.name,)
#     # msg_content = u'There is a new task at "%s"!' % (task.location.name,)
#
#     for user in users:
#         m = Message(type=msg_type,
#                     content=msg_content,
#                     att_type=task.__class__.__name__,
#                     attachment=task.id,
#                     sender=task.requester,
#                     receiver=user,
#                     status='new')
#         save_and_push_msg(m, False)
#     db.session.commit()
def send_request_messages(task, users):
    msg_type = 'task assignment'
    # scheduler = User.query.get(1)
    msg_content_template = '{t.brief} ({t.location.name})'
    #msg_content = u'在"%s"有一个新任务!' % (task.location.name,)
    msg_content = msg_content_template.format(t=task)
    # msg_content = u'There is a new task at "%s"!' % (task.location.name,)

    for user in users:
        m = Message(type=msg_type,
                    content=msg_content,
                    att_type=task.__class__.__name__,
                    attachment=task.id,
                    sender=task.requester,
                    receiver=user,
                    status='new')
        save_and_push_msg(m, False)
    db.session.commit()
def save_and_push_temporal_task_msg(task, worker_prifile):
    msg_type = 'temporal task assignment'
    m = Message(type=msg_type,
                content=str(worker_prifile.id) + ";" + str(worker_prifile.latitude) + ";" + str(worker_prifile.longitude),
                att_type='TemporalTask',
                attachment=task.id,
                sender=task.requester,
                receiver_id=worker_prifile.worker_id,
                status='new')
    db.session.add(m)
    db.session.commit()


def send_user_info(user):
    print 'update user info via push :', user.id, user.name
    push_user_async(user)


def send_answer_comment_message(sender_id, receiver_id, answer_id, ans):
    m = Message(sender_id=sender_id,
                receiver_id=receiver_id,
                type='new comment noti',
                content=u'"%s"有新评论!'%(ans.task.brief, ),
                # content=u'New comment!',
                att_type='Answer',
                attachment=answer_id)
    save_and_push_msg(m)


def send_answer_message(answer):
    print 'answer', answer.id
    task = answer.task
    m = Message(sender_id=answer.worker_id,
                receiver_id=task.requester_id,
                type='new answer noti',
                content=u'A new answer for your task(%s).' % (task.brief, ),
                # content=u'New Answer!',
                att_type=task.__class__.__name__,
                attachment=task.id)
    save_and_push_msg(m)


def set_message_status(j):
    status = j['status']
    for_all = j.get('for_all', False)
    receiver_id = j['receiver_id']  # necessary for user validation, TODO
    if for_all:
        Message.query.filter(Message.receiver_id == receiver_id) \
            .update({'status': status}, synchronize_session=False)
    else:
        message_ids = j.get('message_ids', None)
        Message.query.filter(Message.id.in_(message_ids)) \
            .update({'status': status}, synchronize_session=False)
    db.session.commit()
    return


def main():
    from gmission.app import app

    set_message_status({'receiver_id': 2, 'for_all': True, 'status': 'delivered'})
    set_message_status({'receiver_id': 2, 'message_ids': [1, 2, 3, 4, 5, 10, 11], 'status': 'read'})
    pass


if __name__ == '__main__':
    main()
