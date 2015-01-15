__author__ = 'CHEN Zhao'

import os.path
from flask import Blueprint, jsonify, request, render_template

from gmission.controllers.task_controller import create_indoor_with_new_task, create_global_with_new_task
from gmission.controllers.location_controller import create_new_gps_location, query_indoor, indoor_nearby_user_count, global_nearby_user_count
from gmission.controllers.message_controller import set_message_status


portal_blueprint = Blueprint('portal', __name__, template_folder=os.path.join('templates', 'portal'))


@portal_blueprint.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


