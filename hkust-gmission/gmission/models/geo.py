__author__ = 'chenzhao'


from base import *


class Location(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    coordinate_id = db.Column(db.Integer, db.ForeignKey('coordinate.id'))
    coordinate = db.relationship('Coordinate')


class Coordinate(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)

    longitude = db.Column(GEO_NUMBER_TYPE, nullable=False)  # x
    latitude = db.Column(GEO_NUMBER_TYPE, nullable=False)  # y
    altitude = db.Column(GEO_NUMBER_TYPE, nullable=False)  # y