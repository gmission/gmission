__author__ = 'chenzhao'


from .base import ReSTBase
from werkzeug.exceptions import Conflict
from gmission.models import *
from gmission.controllers.message_controller import send_answer_message, send_answer_comment_message
from gmission.controllers.harmony_controller import contains_sensitive_words
from gmission.controllers.task_controller import refresh_task_status, assign_task_to_workers
from gmission.controllers.payment_controller import pay
# import gmission.controllers.message_controller.send_answer_message as send_answer_message

# for k,v in app.blueprints.items():
#     print k,v

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
        # print 'ReSTUser before_post'
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            e = Conflict()
            existing_user.auth_token = existing_user.get_auth_token()
            e.conflict_obj = existing_user
            raise e


class ReSTAttachment(Attachment, ReSTBase):
    pass


class ReSTMessage(Message, ReSTBase):
    pass


def filter_location(data):
    if data.get('location_id', None):
        # print 'location_id provided, pop location'
        data.pop('location', None)
        return
    if 'location' in data:
        # print 'location provided'
        uc_keys = ['name', 'longitude','latitude']
        existing_location = Location.query.filter_by(**dict(zip(uc_keys, map(data['location'].get, uc_keys)))).first()
        # print 'existing location', existing_location
        if existing_location:
            data.pop('location', None)
            data['location_id'] = existing_location.id


class ReSTTask(Task, ReSTBase):
    @classmethod
    def before_post(cls, data):
        print "beta", data.get("beta")
        # print 'ReSTTask before_post'
        filter_location(data)
    @classmethod
    def after_post(cls, result=None):

        # print 'ReSTTask after_post'
        task = Task.query.get(result['id'])
        assign_task_to_workers(task)


class ReSTThing(Thing, ReSTBase):
    @classmethod
    def before_post(cls, data):
        # print 'ReSTTask before_post'
        pass
    @classmethod
    def after_post(cls, result=None):
        pass
        # print 'ReSTTask after_post'


class ReSTAnswer(Answer, ReSTBase):
    @classmethod
    def before_post(cls, data):
        # print 'ReSTAnswer before_post'
        filter_location(data)
                # data['status'] = 'open'
    @classmethod
    def before_put_single(cls, instance_id=None, data=None):
        # print 'ReSTAnswer before_put'
        filter_location(data)
    @classmethod
    def after_post(cls, result):
        # print 'ReSTAnswer after_post'
        answer = Answer.query.get(result['id'])
        send_answer_message(answer)
        refresh_task_status()
        # Prof. Chen wants workers to be paid at once:
        pay(answer.task.requester, answer.worker, answer, answer.task.credit)

    @classmethod
    def after_get_many(cls, search_params=None, **kwargs):
        pass
        # print 'ReSTAnswer after_get_many'


class ReSTLocation(Location, ReSTBase):
    @classmethod
    def before_post(cls, data):
        # print 'ReSTLocation before_post'
        uc_keys = ['name', 'longitude','latitude']
        location = Location.query.filter_by(**dict(zip(uc_keys, map(data.get, uc_keys)))).first()
        if location:
            e = Conflict()
            e.conflict_obj = location
            raise e

        # data['status'] = 'open'
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


class ReSTIndoorRectangle(IndoorRectangle, ReSTBase):
    pass



class ReSTBaiduPushInfo(BaiduPushInfo, ReSTBase):
    @classmethod
    def before_post(cls, data):
        baidu_uid = data.get("baidu_user_id", "")
        existings = BaiduPushInfo.query.filter(BaiduPushInfo.baidu_user_id == baidu_uid).update({'is_valid': False}, synchronize_session=False)
        pass
    pass


class ReSTCheckin(Checkin, ReSTBase):
    @classmethod
    def before_post(cls, data):
        # print 'ReSTCheckin before_post'
        filter_location(data)


class ReSTAnswerComment(AnswerComment, ReSTBase):
    @classmethod
    def after_post(cls, result):
        # print result
        # print 'ReSTAnswerComment after_post'
        ans = Answer.query.filter_by(id=result['answer_id']).first() # adhoc for mango demo
        send_answer_comment_message(result['sender_id'], result['receiver_id'], ans.task_id, ans)


class ReSTMoment(Moment, ReSTBase):
    @classmethod
    def before_post(cls, data):
        # print 'ReSTCheckin before_post'
        content = data.get('content')
        if contains_sensitive_words(content):
            data['status'] = 'private'
        else:
            data['status'] = 'public'
    pass


class ReSTCategory(Category, ReSTBase):
    pass



class ReSTBaiduPushInfo(BaiduPushInfo, ReSTBase):
    @classmethod
    def before_post(cls, data):
        baidu_uid = data.get("baidu_user_id", "")
        existings = BaiduPushInfo.query.filter(BaiduPushInfo.baidu_user_id == baidu_uid).update({'is_valid': False}, synchronize_session=False)
        pass
    pass
