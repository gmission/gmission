__author__ = 'CHEN Zhao'


import time
from flask_app import app
from push_msg.task import push_msg_task


@app.route('/')
def index():
    return 'test services'


