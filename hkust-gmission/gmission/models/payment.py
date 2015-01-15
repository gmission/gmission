__author__ = 'chenzhao'

from base import *


class CreditTransaction(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    credit = db.Column(db.Integer, nullable=False)

    answer_id = db.Column(db.Integer)

    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    worker = db.relationship('User', foreign_keys=worker_id)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    requester = db.relationship('User', foreign_keys=requester_id)

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)
