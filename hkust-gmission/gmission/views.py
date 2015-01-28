__author__ = 'CHEN Zhao'


import time
import admin
import blueprints

from flask_app import app, cache
import rest
from flask import render_template, request, redirect, jsonify, g
from models import *
from controllers import task_controller

import json

app.register_blueprint(blueprints.user_bp,      url_prefix='/user')
app.register_blueprint(blueprints.image_bp,     url_prefix='/image')
app.register_blueprint(blueprints.video_bp,     url_prefix='/video')
app.register_blueprint(blueprints.audio_bp,     url_prefix='/audio')
# flask_app.register_blueprint(blueprints._bp,     url_prefix='/portal')
app.register_blueprint(blueprints.zzy_map_bp,   url_prefix='/mapping')
app.register_blueprint(blueprints.shortcut_bp,  url_prefix='/shortcut')

rest.ReSTManager.init_rest(app)
# admin.init_admin()


def profile_log(*l):
    app.profiling_logger.debug(l)


@app.route('/')
def index():
    return render_template('index.html', config=app.config)

@app.route('/test')
def test():
    for u in User.query.filter(User.id==49):
        return str(task_controller.get_current_profile(u))


@app.route('/marauders-map')
def marauders_map():
    users = User.query.all()

    user_traces = {}
    # for u in User.query.all()[:50]:
    for u in User.query.filter(User.id==36):
        traces = PositionTrace.query.filter_by(user=u).all()
        user_traces[u.id] = [(t.longitude, t.latitude) for t in traces]

    return render_template('marauders_map.html', users=users, user_traces=json.dumps(user_traces))



@cache.cached(timeout=3600, key_prefix='crabwords')
def load_crabwords():
    return [w.word for w in SensitiveWord.query.all()]


def is_cached_url(url):
    return url.endswith('/rest/location')


@app.before_request
def before_request():
    g.request_start_time = time.time()  # time.time is precise enough

    # if is_cached_url(request.url):
    #     cached_response = cache.get(request.url)
    #     if cached_response:
    #         cached_response.simple_url_cached = True
    #         return cached_response

    g.crabwords = [] #load_crabwords()

    profile_log(request.path, 'crab', time.time()-g.request_start_time)
    # print "[Before request:%s %s, %s]" % (request.method, request.url, request.json)


@app.after_request
def after_request(response):
    # resp_brief = response.data[:200] if 'json' in response.mimetype else ''
    # print "[After request:%s %s, %d, %s, %s]" % \
    #       (request.method, request.url, response.status_code, response.mimetype, resp_brief)
    # if not getattr(response, 'simple_url_cached', False):
    #     cache.set(request.url, response)
    return response


@app.teardown_request
def teardown_request(l):
    profile_log(request.path, time.time()-g.request_start_time)




#409 Conflict: the best HTTP code I can find
@app.errorhandler(409)
def conflict(e):
    print 'conflict!'
    obj = e.conflict_obj
    obj_dict = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    return jsonify(**obj_dict)
    # print e.get_single_url
    # return redirect(e.get_single_url, code=303)  # something wrong with redirect

