__author__ = 'chenzhao'
from base import *
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from gmission.config import APP_SECRET_KEY

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
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))  # encrypt later
    credit = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean())
    created_on = db.Column(db.DateTime, default=datetime.datetime.now)
    iat = db.Column(db.Integer, default=0)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    # roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def get_roles(self):
        return [role.name for role in self.roles]

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration=3600):
        s = Serializer(APP_SECRET_KEY, expires_in=expiration)
        ret = s.dumps({'id': self.id, 'username': self.username})
        try:
            payload, header = s.loads(ret, return_header=True)
            self.iat = header.get('iat', 0)
            db.session.commit()
        except Exception:
            return ret

        return ret

    def get_json(self, password=False):
        fields_in_json = ['id', 'username', 'email', 'credit', 'active', 'created_on']
        json_dict = {}
        for field in fields_in_json:
            json_dict[field] = getattr(self, field)
        json_dict['roles'] = self.get_roles()
        if password:
            json_dict['password'] = self.password
        return json_dict

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(APP_SECRET_KEY)
        try:
            data, header = s.loads(token, return_header=True)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token

        user = User.query.filter_by(id=data['id'], username=data['username'], iat=header['iat']).first()
        return user

    def __unicode__(self):
        return '<User id=%s email=%s>' % (self.id, self.email)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
