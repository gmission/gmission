__author__ = 'CHEN Zhao'

from flask import Blueprint, jsonify, request, g

from gmission.models import *



shortcut_blueprint = Blueprint('shortcut', __name__, template_folder='templates')

@shortcut_blueprint.route('/campaign/<campaign_id>/next-hit', methods=['GET'])
def next_campaign_hit(campaign_id):
    # campaign = Campaign.query.get(campaign_id)
    # if campaign.callback_prefix:
        # pass
    uid = g.user.id

    answered_hits = [hit.id for hit,answer in db.session.query(HIT, Answer).filter(HIT.id==Answer.hit_id, Answer.worker_id==uid).all()]
    print 'answered', answered_hits

    hit = HIT.query.filter(HIT.campaign_id==campaign_id, HIT.status=='open', ~HIT.id.in_(answered_hits)).first()
    print 'next hit', hit.id

    return jsonify({'hit_id': hit.id})

@shortcut_blueprint.route('/answered-hits', methods=['GET'])
def blablabla():
    # {"id":hit.id, "title":hit.title}
    return ""
