__author__ = 'chenzhao'

import os.path
from flask import Flask, jsonify
from config import config, is_production, stdout
from models import db
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.cache import Cache

# encoding trick..
import sys

reload(sys)
sys.setdefaultencoding('UTF8')
# from werkzeug.contrib.profiler import ProfilerMiddleware


ROOT = os.path.dirname(os.path.abspath(__file__))

stdout('going to run Flask at %s' % (ROOT))

app = Flask(__name__)
# app.debug = False
app.debug = True

cache_config = {'CACHE_TYPE': 'simple'}
if is_production():
    cache_config = {'CACHE_TYPE': 'redis',
                    'CACHE_KEY_PREFIX': 'GMISSION-',  # important
                    'CACHE_REDIS_URL': 'redis://@docker-redis:6379/0'}

stdout('Flask cache:', cache_config)
cache = Cache(app, config=cache_config)
cache.init_app(app)

# app.config['PROFILE'] = True
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [30])

config(app, ROOT)


def get_config():
    return app.config


db.app = app
db.init_app(app)

from flask.ext.mail import Mail

mail = Mail(app)

from flask.ext.security import Security
from models import user_datastore

security = Security(app, user_datastore)

app.config['DEBUG_TB_PROFILER_ENABLED'] = False
toolbar = DebugToolbarExtension(app)


class GMissionError(Exception):
    def __init__(self, error, description, status_code=400, headers=None):
        self.error = error
        self.description = description
        self.status_code = status_code
        self.headers = headers

    def to_dict(self):
        rv = dict()
        rv['error'] = self.error
        rv['description'] = self.description
        rv['status_code'] = self.status_code
        return rv


@app.errorhandler(GMissionError)
def handle_gmission_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
