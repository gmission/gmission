__author__ = 'CHEN Zhao'

from flask import Blueprint, jsonify, request

from gmission.controllers.task_controller import create_indoor_with_new_task, create_global_with_new_task
from gmission.controllers.location_controller import create_new_gps_location, query_indoor, indoor_nearby_user_count, global_nearby_user_count
from gmission.controllers.message_controller import set_message_status


shortcut_blueprint = Blueprint('shortcut', __name__, template_folder='templates')


@shortcut_blueprint.route('/indoor_nearby_user_count', methods=['GET', 'POST'])
def _indoor_nearby_user_count():
    location_id = request.args.get('location_id')
    if not location_id:
        return jsonify(count=0)
    r = indoor_nearby_user_count(location_id)
    return jsonify(count=r)

@shortcut_blueprint.route('/global_nearby_user_count', methods=['GET', 'POST'])
def _global_nearby_user_count():
    location_id = request.args.get('location_id')
    if not location_id:
        return jsonify(count=0)
    r = global_nearby_user_count(location_id)
    return jsonify(count=r)

@shortcut_blueprint.route('/request_new_global_task', methods=['POST'])
def request_new_global_task():
    j = request.json
    r = create_global_with_new_task(j)
    return jsonify(res=True)


@shortcut_blueprint.route('/request_new_indoor_task', methods=['POST'])
def request_new_indoor_task():
    j = request.json
    r = create_indoor_with_new_task(j)
    return jsonify(res=True)


@shortcut_blueprint.route('/set_message_status', methods=['POST'])
def set_message_status_():
    j = request.json
    r = set_message_status(j)
    return jsonify(res=True, data=r)


@shortcut_blueprint.route('/query_indoor_location', methods=['GET'])
def query_indoor_location():
    j = request.json
    if not j:
        return jsonify(res=False)
    r = query_indoor(j)
    return jsonify(res=True, location=r)

#
# @shortcut_blueprint.route('/new_gps_location', methods=['POST'])
# def new_gps_location():
#     j = request.json
#     r = create_new_gps_location(j['longitude'], j['latitude'], j['name'])  # TODO
#     return jsonify(res=True, location_id=1234)


# @shortcut_blueprint.route('/answer')
# def answer_request():
    # j = request.json
    # task_paras = dict(map(lambda k:(k, j[k]), ['brief', 'type', 'location_id']))
    # return jsonify(res=True)

#
# s = '2014-02-17T14:36:29.526Z'
# d = dateutil.parser.parse(s)
# print type(d)
# print d.astimezone(dateutil.tz.tzlocal())