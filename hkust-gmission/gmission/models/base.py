__author__ = 'chenzhao'

import datetime
import re
import hashlib
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import backref

db = SQLAlchemy()


GEO_NUMBER_TYPE = db.REAL()


#python any is stupid
def good_any(l):
    for i in l:
        if i:
            return i
    return False


def get_or_create(model, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.flush()
        return instance


def remove_and_commit(model, **kwargs):
    db.session.query(model).filter_by(**kwargs).delete()
    db.session.commit()


class BasicModelMixin(object):
    @staticmethod
    def model_base(cls):
        if db.Model not in cls.__bases__:
            return good_any(BasicModelMixin.model_base(base) for base in cls.__bases__)
        return cls

    @classmethod
    def urlname(cls):
        model_cls = BasicModelMixin.model_base(cls)
        if not model_cls:
            raise Exception('urlname must be called from a db.Model class')
        # print 'urlname', model_cls
        s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', model_cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()

    def __unicode__(self):
        return "%s id:%d" % (self.__class__.__name__, self.id)

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return self.__unicode__()
