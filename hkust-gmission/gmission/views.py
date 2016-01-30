__author__ = 'CHEN Zhao'

import time
import admin
import blueprints

from flask_app import app, cache
import rest
from flask import render_template, request, redirect, jsonify, g
from models import *

import json

app.register_blueprint(blueprints.user_bp, url_prefix='/user')
app.register_blueprint(blueprints.image_bp, url_prefix='/image')
app.register_blueprint(blueprints.video_bp, url_prefix='/video')
app.register_blueprint(blueprints.audio_bp, url_prefix='/audio')
# flask_app.register_blueprint(blueprints._bp,     url_prefix='/portal')
app.register_blueprint(blueprints.shortcut_bp, url_prefix='/shortcut')
app.register_blueprint(blueprints.shortcut_sd, url_prefix='/definitions')

rest.ReSTManager.init_rest(app)


# admin.init_admin()


def profile_log(*l):
    app.profiling_logger.debug(l)


@app.route('/')
def index():
    return render_template('index.html', config=app.config)


@app.route('/test')
def test():
    """Print available functions."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)


def is_cached_url(url):
    return url.endswith('/rest/location')


# @app.before_request
# def before_request():
#     g.request_start_time = time.time()  # time.time is precise enough
#     profile_log(request.path, 'crab', time.time() - g.request_start_time)
#
#
@app.after_request
def after_request(response):
    try:
        if request.method == 'HEAD' and 'num_results' in response.data:
            count = json.loads(response.data)['num_results']
            response.headers.add('GMISSION-Count', str(count))
    except:
        pass
    return response
#     # resp_brief = response.data[:200] if 'json' in response.mimetype else ''
#     # print "[After request:%s %s, %d, %s, %s]" % \
#     #       (request.method, request.url, response.status_code, response.mimetype, resp_brief)
#     # if not getattr(response, 'simple_url_cached', False):
#     #     cache.set(request.url, response)
#     return response


# @app.teardown_request
# def teardown_request(l):
#     profile_log(request.path, time.time() - g.request_start_time)


# 409 Conflict: the best HTTP code I can find
@app.errorhandler(409)
def conflict(e):
    print 'conflict!'
    obj = e.conflict_obj
    obj_dict = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    return jsonify(**obj_dict)
    # print e.get_single_url
    # return redirect(e.get_single_url, code=303)  # something wrong with redirect
