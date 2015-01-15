__author__ = 'chenzhao'

from crowdsourcing import *


class AnswerComment(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))

    answer = db.relationship('Answer', lazy='select')
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'))

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = db.relationship('User', foreign_keys=sender_id)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver = db.relationship('User', foreign_keys=receiver_id)

    reply_to_id = db.Column(db.Integer, db.ForeignKey('answer_comment.id'))
    reply_to = db.relationship('AnswerComment', foreign_keys=reply_to_id)

    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    def __unicode__(self):
        return '<Comment id=%s>' % (self.id, )


