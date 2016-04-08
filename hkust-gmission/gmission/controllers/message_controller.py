#!/usr/bin/env python
# encoding: utf-8
__author__ = 'rui'

from gmission.models import *
from gmission.flask_app import app, ROOT
import os, sys
logger = app.logger
push_msg_logger = app.push_msg_logger

service_path = os.path.join(ROOT, '../../services')
sys.path.append(service_path)
from async_jobs.tasks import ios_push_task, android_push_task


def push_message_async(message_obj):
    def apply_push_task_for_message(baidu_push_info, message_dict):
        if baidu_push_info.type == 'android':
            android_push_task.apply_async((message_dict, baidu_push_info.baidu_channel_id))
        elif baidu_push_info.type == 'ios':
            ios_push_task.apply_async((message_dict['content'],
                                       {'type': 'Message', 'id': message_dict['id']}, baidu_push_info.baidu_channel_id))
        push_msg_logger.info('sent to MQ %s %s', repr(message_dict), repr(baidu_push_info.baidu_channel_id))

    bindlist = BaiduPushInfo.query.filter(BaiduPushInfo.user_id == message_obj.receiver_id,
                                          BaiduPushInfo.is_valid == True).all()
    message_dict = dict(id=message_obj.id, type=message_obj.type, content=message_obj.content.encode('utf-8'),
                        att_type=message_obj.att_type, attachment=message_obj.attachment,
                        sender_id=message_obj.sender_id,
                        receiver_id=message_obj.receiver_id, status=message_obj.status)

    for info in bindlist:
        apply_push_task_for_message(info, message_dict)


def save_and_push_msg(msg, commit=True):
    db.session.add(msg)
    if commit:
        db.session.commit()
    else:
        db.session.flush()
    push_message_async(msg)


def send_request_messages(task, users):
    msg_type = 'task assignment'
    # msg_content = u'在"%s"有一个新任务!' % (task.location.name,)
    msg_content = u'New task: "%s"!' % (task.title,)

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


def send_answer_message(answer):
    hit = answer.hit
    m = Message(sender_id=answer.worker_id,
                receiver_id=hit.requester_id,
                type='new answer noti',
                # content=u'"%s"有新回答!' % (task.brief,),
                content=u'New answer received!',
                att_type=hit.__class__.__name__,
                attachment=hit.id)
    save_and_push_msg(m)
