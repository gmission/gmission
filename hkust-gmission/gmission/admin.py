# -*- coding:utf8  -*-

from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask_app import app
from models import *


def all_models():
    import inspect
    for cls in globals().values():
        if inspect.isclass(cls) and issubclass(cls, db.Model):
            yield cls


def init_admin():
    admin = Admin(app, name=u"gMission Admin Control Panel")
    for model in all_models():
        print 'to add in admin portal:', model.__name__
        admin.add_view(ModelView(model, db.session, name="%s" % model.__name__))



