#!/usr/bin/env python
# encoding: utf-8
import inspect
from flask import Blueprint, jsonify
from gmission.models import *
from alchemyjsonschema import SchemaFactory
from alchemyjsonschema import SingleModelWalker

__author__ = 'rui'

schemadefinition_blueprint = Blueprint('definitions', __name__, template_folder='templates')


def looking_for_class_by_name(model_name):
    for model_cls in globals().values():
        if inspect.isclass(model_cls) and issubclass(model_cls, db.Model):
            if model_cls.__name__ == model_name:
                return model_cls
    return None


@schemadefinition_blueprint.route('/', methods=['GET'])
def schema_definition_list():
    model_list = {'model': []}
    for model_cls in globals().values():
        if inspect.isclass(model_cls) and issubclass(model_cls, db.Model):
            print model_cls.__name__
            model_name = model_cls.__name__
            if model_name not in model_list['model']:
                model_list['model'].append(model_name)
    return jsonify(model_list)


@schemadefinition_blueprint.route('/<model_name>', methods=['GET'])
def generate_schema_definition(model_name):
    model = looking_for_class_by_name(model_name)
    if model:
        factory = SchemaFactory(SingleModelWalker)
        return jsonify(factory(model))
    else:
        return jsonify({})
