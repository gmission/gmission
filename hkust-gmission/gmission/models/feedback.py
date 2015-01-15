__author__ = 'chenzhao'

from base import *


class Feedback(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(2000))
    status = db.Column(db.String(16))  # viewed, replied, ...

    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    attachment = db.relationship('Attachment', foreign_keys=attachment_id)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=user_id)

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    def __unicode__(self):
        return '<Feedback id=%s, title:%s>' % (self.id, self.title)


