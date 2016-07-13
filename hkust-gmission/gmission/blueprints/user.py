from gmission.controllers.privilege_controller import priv_table, role_everyone, init_priv_table, role_guest
from gmission.controllers.user_controller import send_user_auth_email, get_id_from_user_auth_hashid
from gmission.flask_app import GMissionError, app

__author__ = 'CHEN Zhao'

from flask import Blueprint, url_for, session, request, redirect, g, jsonify, json, abort, render_template
from gmission.models import *
from sqlalchemy.sql import text
from functools import wraps
import time

user_blueprint = Blueprint('user bp', __name__, template_folder='templates')


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
            # jwt_verify()
            return fn(*args, **kwargs)

        return decorator

    return wrapper


@app.before_request
def jwt_verify():
    if not request.url_rule:
        return
    # check priv table
    init_priv_table()
    priv = priv_table[(request.url_rule.rule, request.method)]

    try:
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

        # check user by table rules or pre_callback
        return priv.check(user)
    except GMissionError as err:
        # print 'priv', priv, priv.allow_roles
        if priv and role_guest in priv.allow_roles:
            return
        else:
            # for easy debug
            if 'testingust' in request.args:
                g.user = User.query.get(int(request.args['testingust'] or 1))
                print g.user
                return
            raise err


@user_blueprint.route('/register', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    source = request.json.get('source', 'unknown')
    if username is None or password is None or email is None:
        raise GMissionError('Invalid', 'missing arguments')
    if User.query.filter_by(username=username).first() is not None:
        raise GMissionError('Invalid', 'existing user')
    if User.query.filter_by(email=email).first() is not None:
        raise GMissionError('Invalid', 'existing email')
    user = User(username=username, email=email, source=source)
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
        userdict = g.user.get_json()
        ret = userdict.copy()
        ret.update({'token': token.decode('ascii'), 'duration': 3600 * 24 * 30})
        return jsonify(ret)
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


@user_blueprint.route('/credit/campaign/<campaign_id>', methods=['GET'])
def user_credit_campaign_log(campaign_id):
    credit = [transaction.credit for transaction in db.session.query(CreditTransaction).all() if transaction.campaign_id == int(campaign_id) and transaction.worker_id == g.user.id]
    return jsonify({'credit': sum(credit)})

@user_blueprint.route('/answered-hits', methods=['GET'])
def user_answerd_hits():
    cid = request.args.get('cid')
    if cid:
        hits = [(hit.id, hit.title) for c, hit, answer in db.session.query(Campaign, HIT, Answer). \
            filter(Campaign.id==HIT.campaign_id, HIT.id==Answer.hit_id, Answer.worker_id==g.user.id,
                   Campaign.id==int(cid)) ]
    else:
        hits = [(hit.id, hit.title) for hit, answer in db.session.query(HIT, Answer).\
                    filter(HIT.id==Answer.hit_id, Answer.worker_id==g.user.id) ]
        # {"id":hit.id, "title":hit.title}
    return jsonify({'hits': [{"id":hit[0], "title":hit[1]} for hit in list(set(hits))]})


@user_blueprint.route('/unanswered-hits', methods=['GET'])
def user_unanswerd_hits():
    cid = request.args.get('cid')
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 20))

    if cid:
        sql = text('''select id, title, credit from hit where campaign_id = :cid and status='open' and
                        id not in (select hit_id from answer A where A.worker_id = :wid) limit :l offset :o''')
        res = db.engine.execute(sql, cid=int(cid), wid=g.user.id, l=limit, o=offset)
    else:
        sql = text('''select id, title, credit from hit where status='open' and
                        id not in (select hit_id from answer A where A.worker_id = :wid) limit :l offset :o''')
        res = db.engine.execute(sql, wid=g.user.id, l=limit, o=offset)

    return jsonify({'hits': [{"id":hit[0], "title":hit[1], "credit":hit[2]} for hit in res]})


@user_blueprint.route('/answered-campaigns', methods=['GET'])
def user_answerd_campaigns():
    sql = text('''select distinct(C.id) from campaign C join hit H on C.id=H.campaign_id
                                                   join answer A on H.id=A.hit_id
                                                   where A.worker_id= :uid''')
    cids = [r[0] for r in db.engine.execute(sql, uid=g.user.id)]
    campaigns = db.session.query(Campaign).filter(Campaign.id.in_(cids)).all()
    return jsonify({'campaigns': [c.as_dict() for c in campaigns]})


@user_blueprint.route('/campaign/<int:campaign_id>', methods=['GET'])
def next_campaign_hit(campaign_id):
    campaign_dict = db.session.query(Campaign).get(campaign_id).as_dict()

    sql = text('''select count(*) from hit where campaign_id = :cid and
                        id in (select hit_id from answer A where A.worker_id = :wid) ''')

    campaign_dict['answered_count'] = db.engine.scalar(sql, cid=campaign_id, wid=g.user.id)

    sql = text('''select count(*) from hit where campaign_id = :cid and status='open' and
                        id not in (select hit_id from answer A where A.worker_id = :wid) ''')

    campaign_dict['unanswered_count'] = db.engine.scalar(sql, cid=campaign_id, wid=g.user.id)

    return jsonify(campaign_dict)


