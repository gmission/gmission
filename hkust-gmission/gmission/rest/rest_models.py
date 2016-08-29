__author__ = 'chenzhao'

from .base import ReSTBase
from werkzeug.exceptions import Conflict
from gmission.models import *
from gmission.controllers.geo_controller import filter_location
from gmission.controllers.message_controller import send_answer_message
from gmission.controllers.task_controller import assign_task_to_workers, log_worker_as_campaign_participant, refresh_hit_status
from gmission.controllers.payment_controller import pay_for_instant_type_hit


class ReSTUser(User, ReSTBase):
    @classmethod
    def before_get_many(cls, search_params=None, **kwargs):
        pass
        # print 'ReSTUser before_get_many'

    @classmethod
    def before_get_single(cls, instance_id=None, **kwargs):
        pass
        # print 'ReSTUser before_get_single'

    @classmethod
    def after_get_many(cls, **kwargs):
        pass
        # print 'ReSTUser after_get_many'

    @classmethod
    def before_post(cls, data):
        pass
        # print 'ReSTUser before_post'


class ReSTAttachment(Attachment, ReSTBase):
    pass


class ReSTMessage(Message, ReSTBase):
    pass


class ReSTBaiduPushInfo(BaiduPushInfo, ReSTBase):
    pass


class ReSTHIT(HIT, ReSTBase):
    @classmethod
    def before_post(cls, data):
        filter_location(data)

    @classmethod
    def after_post(cls, result=None):
        hit = HIT.query.get(result['id'])
        assign_task_to_workers(hit)
        # why?
        # credit_process(hit)
        pass


class ReSTAnswer(Answer, ReSTBase):
    @classmethod
    def before_post(cls, data):
        data['accepted'] = False
        filter_location(data)

    @classmethod
    def before_put_single(cls, instance_id=None, data=None):  # PUT means updating submitted answers
        filter_location(data)

    @classmethod
    def after_post(cls, result):
        answer = Answer.query.get(result['id'])
        # send_answer_message(answer) messages are not needed in wechat
        pay_for_instant_type_hit(answer)
        refresh_hit_status(answer.hit)
        log_worker_as_campaign_participant(answer)

    @classmethod
    def after_get_many(cls, search_params=None, **kwargs):
        pass
        # print 'ReSTAnswer after_get_many'


class ReSTLocation(Location, ReSTBase):
    @classmethod
    def before_post(cls, data):
        pass
        # print 'ReSTLocation before_post'

    @classmethod
    def after_post(cls, **kw):
        pass
        # print 'ReSTLocation after_post'
        # print kw


class ReSTPositionTrace(PositionTrace, ReSTBase):
    @classmethod
    def after_post(cls, result):
        # print 'ReSTPositionTrace after_post'
        pos = get_or_create(UserLastPosition, user_id=result['user_id'])
        # pos:UserLastPosition
        pos.longitude = result['longitude']
        pos.latitude = result['latitude']
        pos.z = result['z']
        db.session.commit()


class ReSTUserLastPosition(UserLastPosition, ReSTBase):
    @classmethod
    def after_post(cls, **kw):
        pass
        # print 'ReSTPositionTrace after_post'


class ReSTSelection(Selection, ReSTBase):
    pass
