__author__ = 'chenzhao'

from base import *


class SensitiveWord(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(16))
    level = db.Column(db.Integer)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now)
