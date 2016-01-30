__author__ = 'chenzhao'

import inspect
from flask.ext import restless
from gmission.models import *
from .base import ReSTBase
from gmission.flask_app import db, app


REST_PREFIX = '/rest'


class ReSTManager(object):
    rest_models = []

    @classmethod
    def rest_url_get_single(cls, model_obj):
        return '%s/%s/%d' % (REST_PREFIX, model_obj.urlname(), model_obj.id)

    @classmethod
    def init_rest(cls, app):
        for model_cls in globals().values():
            if inspect.isclass(model_cls) and issubclass(model_cls, db.Model):
                # print model_cls
                if model_cls not in ReSTBase.__subclasses__():
                    ReSTManager.rest_models.append(type('ReST'+model_cls.__name__, (model_cls, ReSTBase), {}))

        cls.manager = restless.APIManager(app, flask_sqlalchemy_db=db,
                                                      preprocessors=ReSTBase.universal_preprocessors())
        for rest_class in ReSTBase.__subclasses__():
            cls.manager.create_api(rest_class, methods=['GET', 'POST', 'PUT', 'DELETE'],
                                               url_prefix=REST_PREFIX,
                                               results_per_page=None,
                                               allow_functions=True,
                                               exclude_columns=rest_class.rest_exclude_columns(),
                                               collection_name=rest_class.urlname(),
                                               preprocessors=rest_class.rest_preprocessors(),
                                               postprocessors=rest_class.rest_postprocessors(), )
