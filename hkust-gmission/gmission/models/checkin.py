__author__ = 'chenzhao'

from base import *


class Checkin(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    content = db.Column(db.String(300))

    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    attachment = db.relationship('Attachment', foreign_keys=attachment_id)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=user_id)

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location', foreign_keys=location_id)

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)
