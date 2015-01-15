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
    admin = Admin(app, name=u"深圳世界之窗")
    for model in all_models():
        admin.add_view(ModelView(model, db.session, name=model.__name__))



