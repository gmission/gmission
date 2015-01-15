__author__ = 'bigstone'

from base import *


# class InterestedThing(db.Model, BasicModelMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     description = db.Column(db.String(200), nullable=True)
#
#     image_name = db.Column(db.String(200), nullable=True)
#
#
#     location_name = db.Column(db.String(200), nullable=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     user = db.relationship('User', foreign_keys=user_id)
#
#     created_on = db.Column(db.DateTime, default=datetime.datetime.now)

class Thing(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=True)

    image_name = db.Column(db.String(200), nullable=True)

    location_name = db.Column(db.String(200), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=user_id)

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

class ThingRelation(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)

    thing_id = db.Column(db.Integer, db.ForeignKey('thing.id'))
    thing = db.relationship('Thing', foreign_keys=thing_id)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=user_id)

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

class ThingComment(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))

    thing = db.relationship('Thing', lazy='select')
    thing_id = db.Column(db.Integer, db.ForeignKey('thing.id'))

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = db.relationship('User', foreign_keys=sender_id)

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    def __unicode__(self):
        return '<ThingComment id=%s>' % (self.id, )

