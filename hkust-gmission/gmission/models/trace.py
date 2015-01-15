__author__ = 'chenzhao'

from base import *


class PositionTrace(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)

    longitude = db.Column(GEO_NUMBER_TYPE)
    latitude = db.Column(GEO_NUMBER_TYPE)
    z = db.Column(db.Integer)

    user = db.relationship('User')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)


class UserLastPosition(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)

    longitude = db.Column(GEO_NUMBER_TYPE)
    latitude = db.Column(GEO_NUMBER_TYPE)
    z = db.Column(db.Integer)  # meter?

    user = db.relationship('User')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)

