from base import *

__author__ = 'Jian Xun'


class WorkerDetail(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    capacity = db.Column(db.Integer)
    reliability = db.Column(db.REAL())
    min_direction = db.Column(db.REAL())
    max_direction = db.Column(db.REAL())
    velocity = db.Column(db.REAL())
    region_min_lon = db.Column(GEO_NUMBER_TYPE)
    region_min_lat = db.Column(GEO_NUMBER_TYPE)
    region_max_lon = db.Column(GEO_NUMBER_TYPE)
    region_max_lat = db.Column(GEO_NUMBER_TYPE)
    is_online = db.Column(db.BOOLEAN, default=True)


class HitDetail(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, db.ForeignKey('hit.id'), primary_key=True)
    confidence = db.Column(db.REAL())
    entropy = db.Column(db.REAL())
    is_valid = db.Column(db.BOOLEAN, default=True)
