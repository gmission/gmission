from gmission.controllers.user_controller import send_user_auth_email, get_id_from_user_auth_hashid
from gmission.flask_app import GMissionError, app

__author__ = 'CHEN Zhao'

from flask import Blueprint, url_for, session, request, redirect, g, jsonify, json, abort, render_template
from gmission.models import *
from functools import wraps
import time

user_blueprint = Blueprint('user', __name__, template_folder='templates')


def verify_password(username_or_token, password):
    user = User.verify_auth_token(username_or_token)
    if not user:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


def jwt_auth():
    """
    View decorator that requires a valid JWT token to be present in the request
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            jwt_verify()
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def jwt_verify():
    auth = request.headers.get('Authorization', None)
    if auth is None:
        raise GMissionError('Authorization Required', 'Authorization header was missing', 401)
    auth_header_prefix = app.config['APP_AUTH_HEADER_PREFIX']

    parts = auth.split()
    # print 'jwt', parts
    if parts[0].lower() != auth_header_prefix.lower():
        raise GMissionError('Invalid JWT header', 'Unsupported authorization type')
    elif len(parts) == 1:
        raise GMissionError('Invalid JWT header', 'Token missing')
    elif len(parts) > 2:
        raise GMissionError('Invalid JWT header', 'Token contains spaces')

    g.user = user = User.verify_auth_token(parts[1])

    if user is None:
        raise GMissionError('Invalid JWT', 'User does not exist')


@user_blueprint.route('/register', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    if username is None or password is None or email is None:
        raise GMissionError('Invalid', 'missing arguments')
    if User.query.filter_by(username=username).first() is not None:
        raise GMissionError('Invalid', 'existing user')
    if User.query.filter_by(email=email).first() is not None:
        raise GMissionError('Invalid', 'existing email')
    user = User(username=username, email=email)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    send_user_auth_email(user)
    return jsonify(user.get_json(password=True))


@user_blueprint.route('/auth', methods=['POST'])
def get_auth_token():
    username = request.json.get('username')
    password = request.json.get('password')
    if verify_password(username, password):
        token = g.user.generate_auth_token(3600 * 24 * 30)
        return jsonify({'token': token.decode('ascii'), 'duration': 3600 * 24 * 30})
    raise GMissionError('Invalid', 'invalid username or password')


@user_blueprint.route('/email_verify/<hashid>', methods=['GET'])
def user_email_verify(hashid):
    if hashid is None:
        return render_template('email_confirm.html', result='Error request.')
    userid, expiretime = get_id_from_user_auth_hashid(hashid)
    if userid == 0:
        return render_template('email_confirm.html', result='Error request.')
    if int(time.time()) > expiretime:
        return render_template('email_confirm.html', result='This link is expired.')
    user = User.query.get(userid)
    if user is None:
        return render_template('email_confirm.html', result='Error request.')
    if user.active:
        return render_template('email_confirm.html', result='Your email address has been confirmed already.')
    user.active = True
    db.session.commit()
    return render_template('email_confirm.html', result='Thanks, Your email address has been confirmed.')
