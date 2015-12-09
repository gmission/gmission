#!/usr/bin/env python
# encoding: utf-8
from base import *

__author__ = 'rui'


class BaiduPushInfo(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))  # android or ios

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', foreign_keys=user_id)
    baidu_user_id = db.Column(db.String(50), nullable=False)
    baidu_channel_id = db.Column(db.String(50), nullable=False)

    is_valid = db.Column(db.Boolean, default=True, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)

    def __unicode__(self):
        return '<Baidu id=%s>' % (self.id,)


class Message(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(300), nullable=False)

    att_type = db.Column(db.String(20))
    attachment = db.Column(db.String(200))

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender = db.relationship('User', foreign_keys=sender_id)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver = db.relationship('User', foreign_keys=receiver_id)

    status = db.Column(db.String(20), default='new', nullable=False)  # delivered, read

    created_on = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)

    def __unicode__(self):
        return '<Message id=%s>' % (self.id,)
