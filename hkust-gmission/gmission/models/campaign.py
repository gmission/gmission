#!/usr/bin/env python
# encoding: utf-8
import datetime
from gmission.models import db, BasicModelMixin

__author__ = 'rui'


class Campaign(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    type = db.Column(db.String(20))
    content = db.Column(db.TEXT)

    status = db.Column(db.String(20), default='open')  # or closed
    icon_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    icon = db.relationship('Attachment', foreign_keys=icon_id)

    hits = db.relationship('HIT', lazy='select')

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)


class CampaignRole(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    description = db.Column(db.String(64))


class CampaignUser(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship('User')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    campaign = db.relationship('Campaign')
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    role = db.relationship('CampaignRole')
    role_id = db.Column(db.Integer, db.ForeignKey('campaign_role.id'))
    created_on = db.Column(db.DateTime, default=datetime.datetime.now)