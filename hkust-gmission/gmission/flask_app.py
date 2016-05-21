__author__ = 'chenzhao'

import os.path
from flask import Flask, jsonify
from config import config, stdout
from models import db, get_or_create, Role
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.cache import Cache
# encoding trick..
import sys

reload(sys)
sys.setdefaultencoding('UTF8')


ROOT = os.path.dirname(os.path.abspath(__file__))

stdout('going to run Flask at %s' % (ROOT))

app = Flask(__name__)
app.debug = True

cache_config = {'CACHE_TYPE': 'redis',
                'CACHE_KEY_PREFIX': 'GMISSION-',  # important
                'CACHE_REDIS_URL': 'redis://@docker-redis:6379/0'}

stdout('Flask cache config:', cache_config)
cache = Cache(app, config=cache_config)
cache.init_app(app)


config(app, ROOT)


db.app = app
db.init_app(app)


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
