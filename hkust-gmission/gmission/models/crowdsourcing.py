__author__ = 'chenzhao'


from base import *


class Competition(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    brief = db.Column(db.String(500))
    url = db.Column(db.String(150))
    founder = db.relationship('User', lazy='select')
    founder_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    status = db.Column(db.String(20), default='open')  # or closed
    comments = db.Column(db.String(100))
    begin_time = db.Column(db.DateTime, default=datetime.datetime.now)
    end_time = db.Column(db.DateTime, default=lambda:datetime.datetime.now()+datetime.timedelta(days=1))
    created_on = db.Column(db.DateTime, default=datetime.datetime.now)
    hits = db.relationship('Hit', lazy='select')


class Hit(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    competition = db.relationship('Competition', lazy='select')
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'))
    attachment_type = db.Column(db.String(20))
    attachment_id = db.Column(db.Integer)
    worker = db.relationship('User', lazy='select')
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    answer_content = db.Column(db.String(1000))
    comments = db.Column(db.String(100))
    credit = db.Column(db.Integer, default=1)
    deadline = db.Column(db.DateTime, default=lambda:datetime.datetime.now()+datetime.timedelta(minutes=10))
    status = db.Column(db.String(20), default='open')  # or assigned, finished


class TaxonomyQuery(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(100))
    query_node = db.Column(db.String(1000))
    target_node = db.Column(db.String(1000))
    parent = db.Column(db.String(1000))
    siblings = db.Column(db.String(100))
    children = db.Column(db.String(4000))
    conclusion = db.Column(db.String(120))
    status = db.Column(db.String(20), default='open')  # or assigned, finished


class RecognizationQuery(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(100))
    author_list = db.Column(db.String(1000))
    image_name = db.Column(db.String(1000))
    conclusion = db.Column(db.String(120))
    status = db.Column(db.String(20), default='open')  # or assigned, finished

class TableHeadQuery(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(100))
    table_content = db.Column(db.String(1000))
    conclusion = db.Column(db.String(120))
    status = db.Column(db.String(20), default='open')  # or assigned, finished


class Task(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    brief = db.Column(db.String(500))

    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    attachment = db.relationship('Attachment', foreign_keys=attachment_id)

    credit = db.Column(db.Integer, default=10)
    status = db.Column(db.String(20), default='open')  # or closed
    required_answer_count = db.Column(db.Integer, default=3)
    begin_time = db.Column(db.DateTime, default=datetime.datetime.now)
    end_time = db.Column(db.DateTime, default=lambda:datetime.datetime.now()+datetime.timedelta(days=1))
    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    location = db.relationship('Location', foreign_keys=location_id)

    requester = db.relationship('User')
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    answers = db.relationship('Answer', lazy='select')

    audio_brief_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    # answers = db.relationship('Answer', backref=db.backref('task', lazy='select'), lazy='select')

    def __unicode__(self):
        return '<%s,%s>' % (repr(self.id), self.task)


class Beta(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    task = db.relationship('Task')
    value = db.Column(db.Float)


class WorkerQuality(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    worker = db.relationship('User')
    value = db.Column(db.Float)


class Answer(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)

    task = db.relationship('Task', lazy='select')
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

    brief = db.Column(db.String(100))

    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    attachment = db.relationship('Attachment', lazy='immediate', foreign_keys=attachment_id)

    type = db.Column(db.String(20))
    accepted = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    location = db.relationship('Location', lazy='select')
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    worker = db.relationship('User', lazy='select')
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    audio_brief_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    def __unicode__(self):
        return '<%d,%s,%s>' % (self.id, self.task, self.option)

class TemporalTaskAnswer(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)

    task = db.relationship('Task', lazy='select')
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

    brief = db.Column(db.String(100))

    attachment = db.relationship('Attachment', lazy='immediate')
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))

    type = db.Column(db.String(20))
    created_on = db.Column(db.DateTime, default=datetime.datetime.now)

    task_longitude = db.Column(GEO_NUMBER_TYPE, nullable=False)  # x
    task_latitude = db.Column(GEO_NUMBER_TYPE, nullable=False)  # y

    worker = db.relationship('User', lazy='select')
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    worker_profile = db.relationship("WorkerProfile", lazy='select')
    worker_profile_id = db.Column(db.Integer, db.ForeignKey('worker_profile.id'))

    def __unicode__(self):
        return '<%d,%s,%s>' % (self.id, self.task, self.option)

class TemporalTaskAnswerRating(db.Model, BasicModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('temporal_task_answer.id'), nullable=False)
    answer = db.relationship('TemporalTaskAnswer')
    rater_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rater = db.relationship('User')
    value = db.Column(db.Float)
