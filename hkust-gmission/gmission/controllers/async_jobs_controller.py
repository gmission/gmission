#!/usr/bin/env python
# encoding: utf-8
__author__ = 'rui'

from gmission.config import is_production
from gmission.models import *
from gmission.flask_app import app, ROOT
import sys
import os.path
import user_controller
service_path = os.path.join(ROOT, '../../services')
sys.path.append(service_path)
from async_jobs.tasks import send_email

logger = app.logger
push_msg_logger = app.push_msg_logger


def send_reg_email_async(user):
    subject = "Email confirmation for gMission"
    body = """Thank you for signing up to use gMission!

Please take a moment to verify your email address by clicking the link below.

http://lccpu3.cse.ust.hk/gmission-dev/user/email_verify/%s

If clicking the link doesn't work, copy and paste the link into your browser's address bar.

If you didn't initiate this request, please ignore it.

If you need further assistance, please visit us at http://gmissionhkust.com.

Cheers,
GMission team from HKUST """ % (user_controller.generate_user_auth_hashid(user.id),)
    send_email.apply_async((subject, body, user.email))
    push_msg_logger.info('sent to MQ %s', repr(user.email))





def send_view_ply_email_async(user_id, hit_id, filename):
    user = User.query.get(user_id)
    subject = "Links of the Requested 3D Reconstruction Model from gMission"
    body = """
You can view the 3D model from the URL below:

http://lccpu4.cse.ust.hk/gmission/d3/view/<hit_id>/<filename>

If you want to download the model, please visit the URL below:

http://lccpu4.cse.ust.hk/gmission/d3/ply/<hit_id>/<filename>

If clicking the link doesn't work, copy and paste the link into your browser's address bar. We recommend Chrome, Firefox and Safari.

If you didn't initiate this request, please ignore it.

If you need further assistance, please visit us at http://gmissionhkust.com.

Cheers,
GMission team from HKUST """
    body = body.replace('<hit_id>', hit_id).replace('<filename>', filename)

    send_email.apply_async((subject, body, user.email))
    push_msg_logger.info('sent to MQ %s', repr(user.email))