__author__ = 'chenzhao'
from base import *
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin, BasicModelMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    def __unicode__(self):
        return self.name


class User(db.Model, UserMixin, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))  # encrypt later
    credit = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    # roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def get_roles(self):
        return [role.name for role in self.roles]

    def __unicode__(self):
        return '<User id=%s email=%s>' % (self.id, self.email)




user_datastore = SQLAlchemyUserDatastore(db, User, Role)

