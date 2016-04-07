__author__ = 'haidaoxiaofei'

import os, sys
import random
from gmission.flask_app import app, ROOT
from flask import Blueprint,  jsonify, request, redirect, url_for, send_from_directory, render_template

service_path = os.path.join(ROOT, '../../services')
sys.path.append(service_path)
from async_jobs.tasks import ios_push_task, android_push_task

test_blueprint = Blueprint('test', __name__, template_folder='templates')

TEST_USER_CHANNEL_ID = '3954298542610496812'

@test_blueprint.route('/test_android_message/<message>')
def send_message_android(message):
    android_push_task.apply_async((message, TEST_USER_CHANNEL_ID))
    return 'good'