__author__ = 'haidaoxiaofei'

from base import *
from crowdsourcing import *
from message import *


class Extra(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)

    hit_id = db.Column(db.Integer, db.ForeignKey('hit.id'), nullable=True)
    hit = db.relationship('HIT', foreign_keys=hit_id)

    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=True)
    answer = db.relationship('Answer', foreign_keys=answer_id)

    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=True)
    campaign = db.relationship('Campaign', foreign_keys=campaign_id)

    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    message = db.relationship('Message', foreign_keys=message_id)

    content = db.Column(db.String(200))

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)