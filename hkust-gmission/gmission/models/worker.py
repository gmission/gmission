__author__ = 'bigstone'
from crowdsourcing import *
class WorkerProfile(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    worker = db.relationship('User', foreign_keys=worker_id)
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    min_angle = db.Column(db.Float)
    max_angle = db.Column(db.Float)
    velocity = db.Column(db.Float)
    reliability = db.Column(db.Float)

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    def __unicode__(self):
        return '<WorkerProfile id=%s>' % (self.id, )
