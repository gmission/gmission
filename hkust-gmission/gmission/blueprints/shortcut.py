__author__ = 'CHEN Zhao'

from flask import Blueprint, jsonify, request, g
import redis
import random
import decimal

from gmission.models import *
from gmission.controllers.payment_controller import pay_majority, exchange


# ssdb = redis.StrictRedis(host='docker-ssdb', port=8888, db=0)


shortcut_blueprint = Blueprint('shortcut', __name__, template_folder='templates')

@shortcut_blueprint.route('/campaign/<campaign_id>/next-hit', methods=['GET'])
def next_campaign_hit(campaign_id):
    uid = g.user.id

    # print 'ssdb ts:', ssdb.get('test-timestamp')
    # print 'ssdb un:', ssdb.get('user')
    #
    # ssdb.set('user', g.user.username)
    # ssdb.set('test', "testing")
    # ssdb.set('test-timestamp', str(datetime.datetime.now()))

    answered_hits = [hit.id for hit,answer in db.session.query(HIT, Answer).filter(HIT.id==Answer.hit_id, Answer.worker_id==uid).all()]

    hit = None
    if random.random() > 0.5:  # this is how randomized algorithm rocks
        hit = HIT.query.filter(HIT.campaign_id==campaign_id, HIT.properties=='golden', HIT.status=='open',
                               ~HIT.id.in_(answered_hits)).first()
    if not hit:
        hit = HIT.query.filter(HIT.campaign_id==campaign_id, HIT.status=='open', ~HIT.id.in_(answered_hits)).first()

    if hit:
        return jsonify({'hit_id': hit.id})
    else:
        return jsonify({'hit_id': None})


@shortcut_blueprint.route('/exchange', methods=['GET'])
def exchange_():
    try:
        credit = int(request.values.get('credit'))
        if 'money' in request.values:
            money = decimal.Decimal(request.values.get('money'))
        else:
            money = -decimal.Decimal(credit)/100
        channel = request.values.get('channel')
    except Exception as e:
        print "exchange parameters error:", e
        return jsonify(error="invalid parameters")
    if credit * money >= 0:
        return jsonify(error="invalid parameters, credit and money must go to different directions")
    if credit < 0 and g.user.credit+credit < 0:
        return jsonify(error="invalid parameters, not enough credit")
        campaign = Campaign.query.get(cid)
        answers_list = map(pay_majority, campaign.hits)
        return jsonify(hits=zip((h.id for h in campaign.hits), answers_list))

    if credit > 0:
        action = 'topup'
    else:
        action = 'withdraw'

    ce = exchange(g.user, credit, money, channel, action)
    return jsonify(ce.as_dict())

@shortcut_blueprint.route('/pay-majority', methods=['GET'])
def pay_majority_():
    hid = request.values.get('hid')
    if hid:
        hit = HIT.query.get(hid)
        answers = pay_majority(hit)
        return jsonify(paid_answers=[a.id for a in answers])
    cid = request.values.get('cid')
    if cid:
        campaign = Campaign.query.get(cid)
        answers_list = map(pay_majority, campaign.hits)
        return jsonify(hits=zip((h.id for h in campaign.hits), answers_list))

    return jsonify(error="invalid parameters")


@shortcut_blueprint.route('/answered-hits', methods=['GET'])
def blablabla():
    # {"id":hit.id, "title":hit.title}
    return ""
