__author__ = 'chenzhao'

import os.path
from flask import Flask



ROOT = os.path.dirname(os.path.abspath(__file__))


print 'run %s at %s' % (__name__, ROOT)

app = Flask(__name__)
app.debug = True
# app.debug = False



