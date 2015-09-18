__author__ = 'CHEN Zhao'

from functools import wraps
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, url_for, session, request, redirect, g, jsonify, json, abort, render_template
from flask.ext.security import auth_token_required, current_user
from flask.ext.restless import ProcessingException


user_blueprint = Blueprint('user', __name__, template_folder='templates')

# from gmission.models.basic_models import *
from gmission.models import *

@auth_token_required
def check_user(data=None, **kw):
    # if 'user_id' in kw:
    #     if current_user.id != kw['user_id']:
    #         raise ProcessingException(description='Not authenticated!')
    pass


def add_credit(result=None, **kw):
    # print result
    # print kw
    # user = User.query.get(result['worker_id'])
    # task = Task.query.get(result['task_id'])
    # print user, task
    # task.requester
    # user.credit += 10
    pass


@user_blueprint.route('/login', methods=['POST'])
def login():
    p = request.json
    print 'login new_request', p
    if 'email' in p:
        user = User.query.filter_by(email=p['email'], password=p['password']).first()
    elif 'name' in p:
        user = User.query.filter_by(name=p['name'], password=p['password']).first()
    else:
        return jsonify(res=-1, msg='invalid login info')
    if user:
        return jsonify(res=0, token=user.get_auth_token(), name=user.name, expire='2099-01-01 00:00:00', id=user.id, email=user.email, credit=user.credit, roles=user.get_roles())
    else:
        return jsonify(res=-1, msg='invalid login info')


@user_blueprint.route('/register', methods=['POST'])
def register():
    p = request.json
    # print 'register new_request', p
    role_worker = user_datastore.find_role('worker')
    role_requester = user_datastore.find_role('requester')
    user = User(email=p['email'], password=p['password'], name=p['name'], roles=[role_worker, role_requester])
    try:
        db.session.add(user)
        db.session.commit()
        # send_reg_email_async(user)
        return jsonify(res=0, token=user.get_auth_token(), name=user.name, expire='2099-01-01 00:00:00', id=user.id, email=user.email, credit=user.credit, roles=user.get_roles())
    except Exception as e:
        db.session.rollback()
        if isinstance(e, IntegrityError):
            return jsonify(res=-1, msg='duplicate entry')
        else:
            raise e
    finally:
        db.session.close()

@user_blueprint.route('/refresh', methods=['POST'])
def refresh():
    p = request.json
    if 'id' in p:
        user = User.query.filter_by(id=p['id']).first()
    return jsonify(res=0, token=user.get_auth_token(), name=user.name, expire='2099-01-01 00:00:00', id=user.id, email=user.email, credit=user.credit, roles=user.get_roles())


