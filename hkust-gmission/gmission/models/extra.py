__author__ = 'chenzhao'

from base import *


class Extra(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)

    hit_id = db.Column(db.Integer, db.ForeignKey('hit.id'), nullable=true)
    hit = db.relationship('Hit', foreign_keys=hit_id)

    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=true)
    answer = db.relationship('Answer', foreign_keys=answer_id)

    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=true)
    campaign = db.relationship('Campaign', foreign_keys=campaign_id)

    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=true)
    message = db.relationship('Message', foreign_keys=message_id)

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)