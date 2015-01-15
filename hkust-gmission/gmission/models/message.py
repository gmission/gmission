__author__ = 'chenzhao'

from base import *


class BaiduPushInfo(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50)) #android or ios

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=user_id)
    baidu_user_id = db.Column(db.String(50))
    baidu_channel_id = db.Column(db.String(50))

    is_valid = db.Column(db.Boolean, default=True)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    def __unicode__(self):
        return '<Baidu id=%s>' % (self.id, )



class Message(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    content = db.Column(db.String(300))

    att_type = db.Column(db.String(20))
    attachment = db.Column(db.String(200))

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = db.relationship('User', foreign_keys=sender_id)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver = db.relationship('User', foreign_keys=receiver_id)

    status = db.Column(db.String(20), default='new') # delivered, read

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    def __unicode__(self):
        return '<Message id=%s>' % (self.id, )


class Notice(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    title = db.Column(db.String(50))
    content = db.Column(db.String(500))

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    location = db.relationship('Location', foreign_keys=location_id)

    att_type = db.Column(db.String(20))
    attachment = db.Column(db.String(200))

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = db.relationship('User', foreign_keys=sender_id)

    valid_until = db.Column(db.DateTime, default=datetime.datetime.now)

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    def __unicode__(self):
        return '<Message id=%s>' % (self.id, )


class NoticeReceived(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    title = db.Column(db.String(50))
    content = db.Column(db.String(500))

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    location = db.relationship('Location', foreign_keys=location_id)

    att_type = db.Column(db.String(20))
    attachment = db.Column(db.String(200))

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = db.relationship('User', foreign_keys=sender_id)

    valid_until = db.Column(db.DateTime, default=datetime.datetime.now)

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    def __unicode__(self):
        return '<Message id=%s>' % (self.id, )
