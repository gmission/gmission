__author__ = 'CHEN Zhao'

from flask import Blueprint, jsonify, request

from gmission.controllers.message_controller import set_message_status


shortcut_blueprint = Blueprint('shortcut', __name__, template_folder='templates')


@shortcut_blueprint.route('/set_message_status', methods=['POST'])
def set_message_status_():
    j = request.json
    r = set_message_status(j)
    return jsonify(res=True, data=r)


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