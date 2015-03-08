# -*- coding: utf-8 -*-
__author__ = 'chenzhao'
import datetime, time

import math
import dateutil
import dateutil.tz
import errno
import os
from sets import Set
from gmission.controllers.payment_controller import pay_image, pay_choice
from gmission.controllers.message_controller import send_request_messages, save_and_push_temporal_task_msg
from gmission.models import *
import subprocess

def refresh_task_status():
    check_expired()
    check_enough_answer()
    pass


def check_expired():
    print 'check_expired'
    expired_requests = Task.query.filter_by(status='open') \
        .filter(Task.end_time <= datetime.datetime.now()).all()
    for expired_request in expired_requests:
        # print 'close expired', expired_request.id, expired_request.task.brief
        close_task_and_pay_workers(expired_request)
        fail_related_assignment(expired_request)


def check_enough_answer():
    print 'check_enough_answer'
    for request in Task.query.filter_by(status='open').all():
        if len(request.answers) >= request.required_answer_count:
            # print 'close enough answer', request.id, request.task.brief
            close_task_and_pay_workers(request)


EXPORT_DIR = '/GMission-Server/export-files/'
def export_temporal_task_results(task_ids, subdir_name):
    tasks = []
    for id in task_ids:
        task = Task.query.get(id)
        if task is not None:
            tasks.append(task)
            assigned_workers = calibrate_temporal_task_worker_velocity(task)
            export_assigned_worker_profiles_to_file(task, assigned_workers, EXPORT_DIR+subdir_name)

    write_task_profiles_to_file(tasks, EXPORT_DIR+subdir_name)


MATLAB_WORKSPACE = '/GMission-Server/matlab-workspace/'
def call_matlab(current_time_string):
    import requests
    base_url = "http://docker_matlab:9090/matlab/"
    resp = requests.get(base_url+current_time_string)
    assert resp.status_code == 200
    return resp.text


def close_task_and_pay_workers(task):
    if task.type in ('image', 'video', 'mix'):
        pay_image(task)
    else:  # text multiple choice
        # pay_choice(task)
        pass
    task.status = 'closed'
    delete_related_messages(task)
    db.session.commit()


def clean_temporal_tasks_and_messages():
    tasks = Task.query.filter(Task.status=='open')
    for t in tasks:
        Task.query.filter_by(status='open').update({'status': 'closed'}, synchronize_session=False)
        fail_related_assignment(t)

def delete_related_messages(task):
    Message.query.filter_by(att_type=task.__class__.__name__,
                            attachment=task.id).update({'status': 'deleted'}, synchronize_session=False)
    db.session.commit()


def fail_related_assignment(task):
    Message.query.filter_by(att_type='TemporalTask',
                            attachment=task.id, status='new').update({'status': 'failed'}, synchronize_session=False)
    db.session.commit()


def assign_task_to_workers(task):
    assign_task_to_all_nearby_workers(task)
    pass


def assign_temporal_task_to_workers_random():
    available_workers = query_temporal_available_workers_profile()
    opening_tasks = query_opening_temporal_task()
    import random
    random.seed()
    if len(available_workers) != 0 and len(opening_tasks) != 0:
        for w in available_workers:
            assigned_task = opening_tasks[random.randint(0, len(opening_tasks)-1)]
            db.session.add(w)
            db.session.commit()
            save_and_push_temporal_task_msg(assigned_task, w)


def assign_temporal_task_to_workers():
    opening_tasks = query_opening_temporal_task()
    available_workers = query_temporal_available_workers_profile()
    print "task count:", len(opening_tasks)
    print "available_workers:", len(available_workers)
    if len(opening_tasks) != 0 and len(available_workers) != 0:
        current_time_string = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        for a in available_workers:
            db.session.add(a)

        db.session.commit()

        # write current situation to files
        write_available_worker_profiles_to_file(available_workers, MATLAB_WORKSPACE + current_time_string)
        write_task_profiles_to_file(opening_tasks, MATLAB_WORKSPACE + current_time_string)
        for t in opening_tasks:
            calibrate_temporal_task_worker_velocity(t)
            write_assigned_worker_profiles_to_file(t, MATLAB_WORKSPACE + current_time_string)

        result = subprocess.call(['/GMission-Server/shellScripts/matlab_batcher.sh',
                                  'spatialTaskAssign', '/GMission-Server/matlab-workspace/'+current_time_string])
        if result != 0:
            print "error in calling Matlab script..."
            return

        # read_assignments
        assignment_result_lines = read_assignment_result_from_file(current_time_string)

        for line in assignment_result_lines:
            pair = line.split(" ")
            task = Task.query.get(pair[0])
            worker_profile = WorkerProfile.query.get(pair[1])
            if task is not None and worker_profile is not None:
                save_and_push_temporal_task_msg(task, worker_profile)


def write_task_profiles_to_file(tasks, directory):
    output_template = '{t.id} {t.location.longitude} {t.location.latitude} ' \
                      '{begin_time_seconds} {end_time_seconds} {beta}\n'
    # directory = MATLAB_WORKSPACE + current_time_string
    try:
        os.makedirs(directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    with open(directory+'/tasks.txt', 'a') as f:
        for t in tasks:
            beta = Beta.query.filter(Beta.task_id==t.id).all()[0]
            print beta
            if beta is not None:
                print "beta", beta.value
                begin_time_seconds = (t.begin_time-datetime.datetime(1970, 1, 1)).total_seconds()
                end_time_seconds = (t.end_time - datetime.datetime(1970, 1, 1)).total_seconds()
                f.write(output_template.format(t=t, beta=beta.value,
                                               begin_time_seconds=begin_time_seconds,
                                               end_time_seconds=end_time_seconds))
        f.close()


def write_available_worker_profiles_to_file(workers, directory):
    output_template = '{w.id} {w.longitude} {w.latitude} ' \
                      '{created_on_time_seconds} {w.min_angle} {w.max_angle} ' \
                      '{w.velocity} {w.reliability}\n'
    # directory = MATLAB_WORKSPACE + current_time_string
    try:
        os.makedirs(directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    with open(directory+'/available_workers.txt', 'a') as f:
        for w in workers:
            created_on_time_seconds = (w.created_on-datetime.datetime(1970, 1, 1)).total_seconds()
            output_content = str(output_template.format(w=w, created_on_time_seconds=created_on_time_seconds))
            f.write(output_content)
            print output_content
        f.close()


def export_assigned_worker_profiles_to_file(task, workers, directory):
    output_template = str(task.id) + ' {w.id} {w.longitude} {w.latitude} {created_on_time_seconds} {w.min_angle} ' \
                                     '{w.max_angle} {w.velocity} {w.reliability}\n'
    # directory = MATLAB_WORKSPACE + current_time_string
    print "output assigned workers about task:", task.id
    try:
        os.makedirs(directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    with open(directory+'/assigned_workers.txt', 'a') as f:
        for worker_profile in workers:
            created_on_time_seconds = (worker_profile.created_on-datetime.datetime(1970, 1, 1)).total_seconds()
            f.write(output_template.format(w=worker_profile, created_on_time_seconds=created_on_time_seconds))
        f.close()


def write_assigned_worker_profiles_to_file(task, directory):
    output_template = str(task.id) + ' {w.id} {w.longitude} {w.latitude} {created_on_time_seconds} {w.min_angle} ' \
                                     '{w.max_angle} {w.velocity} {w.reliability}\n'
    # directory = MATLAB_WORKSPACE + current_time_string
    print "output assigned workers about task:", task.id
    try:
        os.makedirs(directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    with open(directory+'/assigned_workers.txt', 'a') as f:
        temporal_workers_assignment_messages = Message.query.filter(Message.att_type == 'TemporalTask')\
            .filter(Message.attachment == task.id).filter(Message.status == 'submitted').all()
        for m in temporal_workers_assignment_messages:
            fields = m.content.split(';')
            temporal_worker_profile_id = fields[0]
            print "workerProfile ID:", temporal_worker_profile_id
            worker_profile = WorkerProfile.query.get(temporal_worker_profile_id)
            if worker_profile is not None:
                created_on_time_seconds = (worker_profile.created_on-datetime.datetime(1970, 1, 1)).total_seconds()
                f.write(output_template.format(w=worker_profile, created_on_time_seconds=created_on_time_seconds))
        f.close()


def read_assignment_result_from_file(current_time_string):
    directory = MATLAB_WORKSPACE + current_time_string
    with open(directory + '/assignment_result.txt', 'r') as r:
        lines = r.readlines()
        r.close()

    return lines


def extract_temporal_task_answers_to_table():
    # try:
    #     num_rows_deleted = TemporalTaskAnswer.query.delete()
    #     db.session.commit()
    # except:
    #     db.session.rollback()
    latest_answer = TemporalTaskAnswer.query.order_by(TemporalTaskAnswer.created_on).limit(1).all()

    if len(latest_answer) == 0:
        first_temporal_task = Task.query.get(424)
        start_time = first_temporal_task.created_on
    else:
        start_time = latest_answer[0].created_on

    tasks = Task.query.filter(Task.created_on > start_time).all()
    count = 0
    shouldCount = 0
    answerCount = 0
    for task in tasks:

        temporal_workers_assignment_messages = Message.query.filter(Message.att_type == 'TemporalTask')\
            .filter(Message.attachment == task.id).all()
        for m in temporal_workers_assignment_messages:
            fields = m.content.split(';')
            temporal_worker_profile_id = fields[0]
            worker_profile = WorkerProfile.query.get(temporal_worker_profile_id)
            temporal_worker_latitude = worker_profile.latitude
            temporal_workers_longitude = worker_profile.longitude
            submit_message = Answer.query\
                .filter(Answer.task_id == m.attachment)\
                .filter(Answer.worker_id == m.receiver_id)\
                .filter(Answer.created_on > m.created_on)\
                .order_by(Answer.created_on).limit(1).all()
            if len(submit_message) == 0:
                print 'no submit message', count
                count += 1
                continue
            else:
                answer = submit_message[0]
                next_assign_message = Message.query.filter(Message.att_type == 'TemporalTask')\
                    .filter(Message.attachment == m.attachment).filter(Message.sender_id == m.sender_id)\
                    .filter(Message.receiver_id == m.receiver_id).filter(Message.created_on > m.created_on)\
                    .order_by(Message.created_on).limit(1).all()
                print 'should have one', shouldCount
                shouldCount += 1
                if len(next_assign_message) == 0 or next_assign_message[0].created_on > answer.created_on:
                    # detected one temporal task submitted answer
                    print 'real answered', answerCount
                    answerCount += 1
                    temporal_answer = TemporalTaskAnswer(task_id=answer.task_id,
                                                         brief=task.brief,
                                                         attachment_id=answer.attachment_id,
                                                         type=answer.type,
                                                         task_latitude=answer.task.location.latitude,
                                                         task_longitude=answer.task.location.longitude,
                                                         worker_id=answer.worker_id,
                                                         worker_profile_id=worker_profile.id)
                    db.session.add(temporal_answer)

                db.session.commit()



def calibrate_temporal_task_worker_velocity(task):
    temporal_workers_assignment_messages = Message.query.filter(Message.att_type == 'TemporalTask')\
        .filter(Message.attachment == task.id).all()
    assigned_workers = []
    for m in temporal_workers_assignment_messages:
        start_moving_time = m.created_on
        fields = m.content.split(';')
        temporal_worker_profile_id = fields[0]
        worker_profile = WorkerProfile.query.get(temporal_worker_profile_id)
        temporal_worker_latitude = worker_profile.latitude
        temporal_workers_longitude = worker_profile.longitude
        submit_message = Message.query.filter(Message.type == 'new answer noti')\
            .filter(Message.attachment == m.attachment)\
            .filter(Message.sender_id == m.receiver_id)\
            .filter(Message.receiver_id == m.sender_id)\
            .filter(Message.created_on > m.created_on)\
            .order_by(Message.created_on).limit(1).all()
        if len(submit_message) == 0:
            print 'no submit message'
            continue
        else:
            submit_message = submit_message[0]
            next_assign_message = Message.query.filter(Message.att_type == 'TemporalTask')\
                .filter(Message.attachment == m.attachment).filter(Message.sender_id == m.sender_id)\
                .filter(Message.receiver_id == m.receiver_id).filter(Message.created_on > m.created_on)\
                .order_by(Message.created_on).limit(1).all()
            if len(next_assign_message) == 0 or next_assign_message[0].created_on > submit_message.created_on:
                if submit_message.created_on > task.end_time:
                    moving_time_seconds = (task.end_time - start_moving_time).total_seconds() - 2
                else:
                    moving_time_seconds = (submit_message.created_on - start_moving_time).total_seconds()
                distance = geo_distance(task.location.longitude,
                                           task.location.latitude,
                                           temporal_workers_longitude,
                                           temporal_worker_latitude)
                print "distance", distance
                print "moving_time", moving_time_seconds
                calibrated_velocity = (distance / moving_time_seconds) * 1.001
                if calibrated_velocity * moving_time_seconds < distance:
                    print "wrong velocity detected.."
                print "new velocity", calibrated_velocity
                WorkerProfile.query.filter(WorkerProfile.id == temporal_worker_profile_id) \
                    .update({'velocity': calibrated_velocity}, synchronize_session=False)
                db.session.commit()
                assigned_workers.append(WorkerProfile.query.get(temporal_worker_profile_id))

    return assigned_workers


def calibrate_worker_profile():
    print "here"
    worker_profiles = WorkerProfile.query.all()
    for w in worker_profiles:
        print "calibrating worker:", w.id
        # position = PositionTrace.query.filter(PositionTrace.user_id==w.worker_id)\
        #     .filter(PositionTrace.created_on <= w.created_on).order_by(PositionTrace.created_on.desc()).limit(1).all()[0]
        # WorkerProfile.query.filter(WorkerProfile.id == w.id) \
        #             .update({'latitude': position.latitude, 'longitude': position.longitude}, synchronize_session=False)
        if w.min_angle == w.max_angle:
            WorkerProfile.query.filter(WorkerProfile.id == w.id) \
                .update({'max_angle': w.min_angle + 2 * math.pi}, synchronize_session=False)
        if w.velocity == 0 or w.velocity > 1:
            WorkerProfile.query.filter(WorkerProfile.id == w.id) \
                .update({'velocity': DEFAULT_VELOCITY}, synchronize_session=False)

        db.session.commit()


def configUserQuality():
    temporal_answers = TemporalTaskAnswer.query.all()
    answer_avg_rating_values = {}
    print "answers count:", len(temporal_answers)
    for answer in temporal_answers:
        ratings = TemporalTaskAnswerRating.query.filter(TemporalTaskAnswerRating.answer_id==answer.id).all()
        rating_values = list([rate.value for rate in ratings])
        # print "ratings:", rating_values
        rating_values.sort()
        if len(rating_values) >= 3:
            rating_values = rating_values[1:len(rating_values)-1]

        answer_avg_rating_values[answer.id] = sum(rating_values) / float(len(rating_values))

    answer_workers_id = list([answer.worker_id for answer in temporal_answers])
    answer_workers_id = list(set(answer_workers_id))
    answer_workers_id.sort()

    for worker_id in answer_workers_id:
        worker_quality_value = 0
        answer_times = 0
        for answer in temporal_answers:
            if answer.worker_id == worker_id:
                worker_quality_value += answer_avg_rating_values[answer.id]
                answer_times += 1

        worker_quality = WorkerQuality(worker_id=worker_id, value=(worker_quality_value/answer_times)/5)
        db.session.add(worker_quality)

    db.session.commit()


def export_user_qualities(directory):
    output_template = '{w.worker_id} {w.value}\n'
    worker_qualities = WorkerQuality.query.all()
    with open(directory+'/workers_quality.txt', 'a') as f:
        for wq in worker_qualities:
            f.write(output_template.format(w=wq))

    f.close()


def export_worker_profile_user_id_map(directory):
    output_template = '{w.id} {w.worker_id}\n'
    worker_profiles = WorkerProfile.query.all()
    with open(directory+'/worker_profile_to_user.txt', 'a') as f:
        for wq in worker_profiles:
            f.write(output_template.format(w=wq))

    f.close()




DEFAULT_RELIABILITY = 0.9
DEFAULT_VELOCITY = 0.000005
def calculate_current_profile(user):
    traces = PositionTrace.query.order_by(PositionTrace.created_on.desc()).filter(PositionTrace.user_id==user.id).limit(20).all()

    worker_quality = WorkerQuality.query.filter(WorkerQuality.worker_id==user.id).limit(1).all()
    if len(worker_quality) != 0:
        user_quality = worker_quality[0].value
    else:
        user_quality = DEFAULT_RELIABILITY
    worker_profile = WorkerProfile(longitude=0,
                                   latitude=0,
                                   min_angle=0,
                                   max_angle=0,
                                   velocity=DEFAULT_VELOCITY,
                                   reliability=user_quality,
                                   worker_id=user.id)

    print "length of traces:", len(traces)
    print "user id:", user.id
    if len(traces) < 2:
        return worker_profile

    end_point, traces = traces[0], traces[1:]
    min_angle = 0
    max_angle = 0
    has_inited = False
    last_point = end_point
    velocities = Set()

    for index, t in enumerate(traces):
        if t.latitude == end_point.latitude and t.longitude == end_point.longitude:
            continue
        arrival_angle = geo_angle(t.longitude, t.latitude, end_point.longitude, end_point.latitude)
        # print "arrival_angle:", arrival_angle
        if not has_inited:
            min_angle = arrival_angle
            max_angle = arrival_angle
            has_inited = True
            # print "initial angle:", arrival_angle
            continue
        if arrival_angle > max_angle:
            max_angle = arrival_angle
            # print "max_angle:", max_angle
        if arrival_angle < min_angle:
            min_angle = arrival_angle
            # print "min_angle:", min_angle

        velocity = DEFAULT_VELOCITY

        distance = geo_distance(t.longitude, t.latitude, last_point.longitude, last_point.latitude)
        time_interval = (last_point.created_on - t.created_on).total_seconds()
        if time_interval != 0:
            velocity = distance / time_interval
        last_point = t
        velocities.add(velocity)

    # min_angle = min_angle + math.pi
    # max_angle = max_angle + math.pi

    if min_angle < 0:
        max_angle += 2 * math.pi
        min_angle += 2 * math.pi


    # last_profile = WorkerProfile.query.order_by(WorkerProfile.created_on.desc())\
    #     .filter(WorkerProfile.worker_id==user.id).limit(1).all()
    #
    # if len(last_profile) == 0:
    #     worker_profile.reliability = DEFAULT_RELIABILITY
    # else:
    #     worker_profile.reliability = last_profile[0].reliability

    worker_profile.max_angle = max_angle
    worker_profile.min_angle = min_angle
    if len(velocities) != 0:
        worker_profile.velocity = float((max(velocities) + min(velocities))/2)

    if worker_profile.velocity < DEFAULT_VELOCITY:
        worker_profile.velocity = DEFAULT_VELOCITY

    worker_profile.longitude = end_point.longitude
    worker_profile.latitude = end_point.latitude
    worker_profile.created_on = end_point.created_on

    # return [worker_profile.velocity, worker_profile.reliability, velocities]
    return worker_profile

def geo_angle(startPointLong, startPointLati, endPointLong, endPointLati):
    angle = math.atan2(endPointLati - startPointLati, endPointLong - startPointLong)
    return angle



K_IN_KNN = 10
def assign_task_to_knn_workers(task):
    """:type task:Task"""
    location = task.location
    print 'assign_task_to_knn_workers: location', location
    lo, la = location.longitude, location.latitude
    users = [u for u in get_nearest_n_users(lo, la, K_IN_KNN+1) if u.id!=task.requester_id][:K_IN_KNN]
    # users = [u for u in User.query.all() if u.id!=task.requester_id]
    send_request_messages(task, users)


def query_temporal_available_workers_profile():
    users = query_online_users()
    available_users = []

    for u in users:
        latest_temporal_task_message = Message.query.filter(Message.receiver_id == u.id)\
            .filter(Message.att_type == 'TemporalTask').order_by(Message.created_on.desc()).limit(1).all()
        if len(latest_temporal_task_message) != 0:
            if latest_temporal_task_message[0].status != 'new':
                available_users.append(u)
        else:
            available_users.append(u)

    available_users_profile = []
    for u in available_users:
        u_profile = calculate_current_profile(u)
        available_users_profile.append(u_profile)

    return available_users_profile


def query_online_users():
    ten_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
    online_users = User.query.join(UserLastPosition)\
        .filter(UserLastPosition.user_id == User.id)\
        .filter(UserLastPosition.last_updated >= ten_minutes_ago).all()
    return online_users


def query_opening_temporal_task():
    # assume every temporal task needs 1000 workers and other kind of task does not need 1000 workers
    opening_task = Task.query\
        .filter(Task.status == 'open').filter(Task.brief.startswith('(ST)')).all()
    return opening_task


def assign_task_to_all_nearby_workers(task):
    location = task.location
    print 'assign_task_to_all_nearby_workers: location', location
    lo, la = location.longitude, location.latitude
    users = [u for u in get_nearby_users(lo, la) if u != task.requester]
    send_request_messages(task, users)
    pass


def local_datetime(dt_string):
    if isinstance(dt_string, datetime.datetime):
        return dt_string
    dt = dateutil.parser.parse(dt_string)
    if dt.tzinfo:
        dt = dt.astimezone(dateutil.tz.tzlocal())
    return dt


def geo_distance(long1, lati1, long2, lati2):
    return math.sqrt((long1-long2)**2+(lati1-lati2)**2)
    pass


# 1km is about 0.01, 1m is 0.00001
def get_nearest_n_users(longitude, latitude, n, r=0.00001):
    P = UserLastPosition

    in_rect = (P.longitude>=longitude-r) & (P.longitude<=longitude+r) \
                   & (P.latitude>=latitude-r) & (P.latitude <= latitude+r)
    c = P.query.filter(in_rect).count()

    print 'KNN', n, r, c

    if c < n and r < 0.1:
        return get_nearest_n_users(longitude, latitude, n, r*2)

    ps = sorted(P.query.filter(in_rect).all(), key=lambda p: geo_distance(p.longitude, p.latitude, longitude, latitude))
    return [p.user for p in ps[:n]]


def get_nearby_users(longitude, latitude):
    r = 0.05
    P = UserLastPosition

    in_rect = (P.longitude>=longitude-r) & (P.longitude<=longitude+r) \
              & (P.latitude>=latitude-r) & (P.latitude<=latitude+r)
    c = P.query.filter(in_rect).count()

    print 'user in 5km bound:', c

    # ps = sorted(P.query.filter(in_rect).all(), key=lambda p: geo_distance(p.longitude, p.latitude, longitude, latitude))
    return [p.user for p in P.query.filter(in_rect).all()]


if __name__=='__main__':
    check_expired()
