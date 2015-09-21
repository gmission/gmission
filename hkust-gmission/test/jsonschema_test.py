#!/usr/bin/env python
# encoding: utf-8
import inspect
import json
from gmission.models import *

__author__ = 'rui'

from alchemyjsonschema import SchemaFactory
from alchemyjsonschema import SingleModelWalker

if __name__ == '__main__':
    factory = SchemaFactory(SingleModelWalker)
    print(json.dumps(factory(HIT)))
    for model_cls in globals().values():
        if inspect.isclass(model_cls) and issubclass(model_cls, db.Model):
            print model_cls.__name__