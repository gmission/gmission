__author__ = 'chenzhao'


from base import *


class Attachment(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(20)) #image, video, option, list
    value = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    children = db.relationship('Attachment', backref=db.backref("parent", remote_side=id), lazy='select')
    # parent = db.relationship('Attachment', backref="children")
