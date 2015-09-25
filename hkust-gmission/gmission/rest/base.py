from gmission.blueprints.user import jwt_auth

__author__ = 'chenzhao'

import inspect


class ReSTBase(object):
    @classmethod
    def universal_before_post(cls, data):
        # print 'Universal before_post'
        data.pop('id', None)

    @classmethod
    @jwt_auth()
    def check_user_token(cls, **kw):
        return True

    @classmethod
    def processor_name_mapping(cls, prefix):
        exclude_list = []
        processors = {}
        processors_fields = ['GET_SINGLE', 'GET_MANY', 'PATCH_SINGLE', 'PATCH_MANY', 'PUT_SINGLE', 'PUT_MANY', 'POST',
                             'DELETE']
        for raw_method in inspect.getmembers(cls, predicate=inspect.ismethod):
            name, method = raw_method
            if name.startswith(prefix):
                processors[name[len(prefix) + 1:].upper()] = [method.__get__(cls), ]

        if cls.__name__ not in exclude_list and prefix == 'before':
            for key in processors_fields:
                preprocessor = processors.get(key, [])
                preprocessor.insert(0, cls.check_user_token)
                processors[key] = preprocessor
        return processors

    @classmethod
    def universal_preprocessors(cls):
        prefix = 'universal_before'
        return ReSTBase.processor_name_mapping(prefix)

    @classmethod
    def rest_preprocessors(cls):
        prefix = 'before'
        return cls.processor_name_mapping(prefix)

    @classmethod
    def rest_postprocessors(cls):
        prefix = 'after'
        return cls.processor_name_mapping(prefix)

    @classmethod
    def rest_exclude_columns(cls):
        # r = [cln for cln in cls.__mapper__.columns if isinstance(cln, db.RelationshipProperty)]
        return [str(r).split('.')[1] for r in cls.__mapper__.relationships]
