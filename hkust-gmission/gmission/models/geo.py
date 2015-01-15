__author__ = 'chenzhao'


from base import *


class Category(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    # locations = db.relationship('IndoorLocation', backref="category")

    def __unicode__(self):
        return '<%d,%s>' % (self.id, self.name)


class Region(db.Model, BasicModelMixin): #only HKUST now
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


class Location(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.relationship('Category', lazy='select')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    region = db.relationship('Region', lazy='select')
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))

    longitude = db.Column(GEO_NUMBER_TYPE, nullable=False)  # x
    latitude = db.Column(GEO_NUMBER_TYPE, nullable=False)  # y
    z = db.Column(db.Integer)

    bound_id = db.Column(db.Integer, db.ForeignKey('location_bound.id'))
    bound = db.relationship('LocationBound')

    __table_args__ = (UniqueConstraint('name', 'z', name='location_uc'), )


#TODO: to be or not to be?
class LocationBound(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)

    left_top_longitude = db.Column(GEO_NUMBER_TYPE)
    left_top_latitude = db.Column(GEO_NUMBER_TYPE)
    right_bottom_longitude = db.Column(GEO_NUMBER_TYPE)
    right_bottom_latitude = db.Column(GEO_NUMBER_TYPE)


#for indoor localization only
class IndoorRectangle(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location')
    z = db.Column(db.Integer)
    left_top_longitude = db.Column(GEO_NUMBER_TYPE)
    left_top_latitude = db.Column(GEO_NUMBER_TYPE)
    right_bottom_longitude = db.Column(GEO_NUMBER_TYPE)
    right_bottom_latitude = db.Column(GEO_NUMBER_TYPE)
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
