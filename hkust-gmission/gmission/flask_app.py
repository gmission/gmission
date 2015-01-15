__author__ = 'chenzhao'

import os.path
from flask import Flask
from config import config, is_production
from models import db
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.cache import Cache


# from werkzeug.contrib.profiler import ProfilerMiddleware



ROOT = os.path.dirname(os.path.abspath(__file__))


print 'run %s at %s' % (__name__, ROOT)

app = Flask(__name__)
app.debug = False
app.debug = True

if is_production():
    cache = Cache(app, config={'CACHE_TYPE': 'redis',
                               'CACHE_KEY_PREFIX': 'GMISSION_SZWW-',  # important
                               'CACHE_REDIS_URL': 'redis://@localhost:6379/0'})
else:
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

cache.init_app(app)
print 'Flask Cache:', cache.cache

# app.config['PROFILE'] = True
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [30])

config(app, ROOT)
db.app = app
db.init_app(app)


from flask.ext.mail import Mail
mail = Mail(app)

from flask.ext.security import Security
from models import user_datastore
security = Security(app, user_datastore)


app.config['DEBUG_TB_PROFILER_ENABLED'] = True
toolbar = DebugToolbarExtension(app)







