__author__ = 'chenzhao'

from base import *


# type = text / image / selection
class HIT(db.Model, BasicModelMixin):
    __tablename__ = 'hit'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    title = db.Column(db.String(200))
    content = db.Column(db.TEXT)

    properties = db.Column(db.String(100))

    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    attachment = db.relationship('Attachment', foreign_keys=attachment_id)

    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship('Campaign', lazy='select')

    credit = db.Column(db.Integer, default=10)
    status = db.Column(db.String(20), default='open')  # or closed
    required_answer_count = db.Column(db.Integer, default=3)
    min_selection_count = db.Column(db.Integer, default=1)
    max_selection_count = db.Column(db.Integer, default=1)
    begin_time = db.Column(db.DateTime, default=datetime.datetime.now)
    end_time = db.Column(db.DateTime, default=lambda: datetime.datetime.now() + datetime.timedelta(days=300))
    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    location = db.relationship('Location', foreign_keys=location_id)

    requester = db.relationship('User')
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    selections = db.relationship('Selection', lazy='select')
    answers = db.relationship('Answer', lazy='select')

    def __unicode__(self):
        return '<%d,%s>' % (self.id, self.title)


class Answer(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)

    hit = db.relationship('HIT', lazy='select')
    hit_id = db.Column(db.Integer, db.ForeignKey('hit.id'))

    type = db.Column(db.String(20))
    content = db.Column(db.String(200))
    ordinal = db.Column(db.Integer)  # for selections

    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    attachment = db.relationship('Attachment', lazy='immediate', foreign_keys=attachment_id)

    accepted = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    location = db.relationship('Location', lazy='select')
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    worker = db.relationship('User', lazy='select')
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __unicode__(self):
        return '<%d,%s,%s>' % (self.id, self.hit, self.content)


class Selection(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)

    hit = db.relationship('HIT', lazy='select')
    hit_id = db.Column(db.Integer, db.ForeignKey('hit.id'))

    type = db.Column(db.String(20))
    content = db.Column(db.String(200))

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)
