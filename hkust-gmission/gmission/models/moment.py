__author__ = 'chenzhao'

from base import *


class Moment(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(256))
    status = db.Column(db.String(16))  # public, private, to be checked, ...

    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    attachment = db.relationship('Attachment', foreign_keys=attachment_id)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=user_id)

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    def __unicode__(self):
        return '<Moment id=%s>' % (self.id, )


