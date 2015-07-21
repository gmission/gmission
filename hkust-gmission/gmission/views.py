__author__ = 'CHEN Zhao'


import time
import admin
import blueprints

from flask_app import app, cache
import rest
from flask import render_template, request, redirect, jsonify, g
from models import *
from controllers import task_controller, taxonomy_controller, recognization_controller

import json

app.register_blueprint(blueprints.user_bp,      url_prefix='/user')
app.register_blueprint(blueprints.image_bp,     url_prefix='/image')
app.register_blueprint(blueprints.video_bp,     url_prefix='/video')
app.register_blueprint(blueprints.audio_bp,     url_prefix='/audio')
# flask_app.register_blueprint(blueprints._bp,     url_prefix='/portal')
app.register_blueprint(blueprints.zzy_map_bp,   url_prefix='/mapping')
app.register_blueprint(blueprints.shortcut_bp,  url_prefix='/shortcut')

rest.ReSTManager.init_rest(app)
# admin.init_admin()


def profile_log(*l):
    app.profiling_logger.debug(l)


@app.route('/')
def index():
    return render_template('index.html', config=app.config)

@app.route('/rating')
def rating():
    return render_template('rating.html')


@app.route('/test')
def test():
    # for u in User.query.filter(User.id==49):
    #     return str(task_controller.query_online_users())
    # task = Task.query.filter(Task.id == '435').limit(1).all()
    # task_controller.calibrate_temporal_task_worker_velocity(task[0])
    # return str(task_controller.write_available_worker_profiles_to_file(1))
    # task_controller.calibrate_worker_profile()
    # task_controller.export_temporal_task_results([424], 'test')
    # task_controller.test()
    # task_controller.calibrate_worker_profile()
    return "test OK"


def campaign_task_ranking():
    result = db.engine.execute("select 10*count(distinct task.id), answer.worker_id, user.name from task join answer on task.id=answer.task_id join user on answer.worker_id=user.id where task.requester_id=1 and task.created_on>'2015-06-08' and user.email like '%%ust.hk' group by answer.worker_id order by sum(task.credit) desc; ")
    return [{"name":row[2], "credit":row[0]} for row in result]


@app.route('/hkust_campaign/<email>/<hit_id>')
def hkust_statistic(email, hit_id):
    print email, hit_id
    if email=='*email*':  # from iOS
        #ranking = [{"name":"CHEN Zhao", "credit":100}, {"name":"Messi", "credit":90}, {"name":"C. Ronaldo", "credit":70} ]
        #return render_template("hkust_statistic.html", ranking=campaign_task_ranking())
        pass
    else:  # from android?
        #return render_template("hkust_statistic.html")
        pass

    return render_template("hkust_statistic.html", ranking=campaign_task_ranking())
    return "prepare OK"

################################################################################
############## experiment start


=======
###########################For Mengrui's Experiments
>>>>>>> 608bd7ed0a9888bcfdde39a20b41ecaf8a9affdf
@app.route('/taxonomy_help/<email>')
def taxonomy_help(email):
    return render_template('taxonomy_help.html', email=email)


@app.route('/check_timeout_hits')
def check_timeout_hits():
    taxonomy_controller.check_timeout_hits()
    return 'Finish Checking timeout hits'


@app.route('/jump_to_next_hit/<email>/<current_hit_id>')
def jump_to_next_hit(email, current_hit_id):
    current_hit = Hit.query.get(current_hit_id)
    current_hit.status = 'open'
    db.session.commit()
    return taxonomy_hit(email, current_hit_id)

@app.route('/taxonomy_hit/<email>/<current_hit_id>')
def taxonomy_hit(email, current_hit_id):
    worker = User.query.filter(User.email==email).first()
    if worker is None:
        return "Cannot find your email record... Please Check it again..."
    last_hit = taxonomy_controller.recover_ongoing_hit(worker)
    print 'last_hit'
    # print 'current_hit_id',current_hit_id
    if last_hit is None:
        print 'last is none'
        if current_hit_id == "null":
            next_hit = taxonomy_controller.fetch_next_hit(worker, -1)
        else:
            next_hit = taxonomy_controller.fetch_next_hit(worker, current_hit_id)
    else:
        next_hit = last_hit

    if next_hit is not None:
        taxonomy_query = TaxonomyQuery.query.get(next_hit.attachment_id)

        print 'ok'
        return render_template('taxonomy_hit.html',
                               email=email,
                               credits=worker.credit,
                               hit_value=next_hit.credit,
                               hit_number=next_hit.id,
                               query_content=taxonomy_query.query_node,
                               parent_node=taxonomy_query.parent,
                               target_node=taxonomy_query.target_node,
                               children_node_list=taxonomy_query.children)
    else:
        return "No tasks now... Please try later..."


@app.route('/answer_hit', methods=['POST'])
def answer_hit():
    print 'here'
    email = request.form['email_address']
    option = request.form['option']
    sub_option = request.form['sub_option']
    hit_number = request.form['hit_number']
    print "ok"
    if sub_option != "":
        return taxonomy_controller.answer_hit(hit_number, email, option+":"+sub_option)
    else:
        return taxonomy_controller.answer_hit(hit_number, email, option)


@app.route('/taxonomy_create', methods=['POST'])
def taxonomy_create():
    query_number = request.form['query_number']
    parent_node_info = request.form['parent']
    target_node_info = request.form['target']
    query_node_info = request.form['query']
    children_node_info = request.form['children']
    taxonomy_controller.create_query(query_number, parent_node_info, target_node_info, query_node_info, children_node_info, 6)
    return "OK"


@app.route('/taxonomy_status_query/<query_number>')
def taxonomy_status_query(query_number):
    print query_number
    query = TaxonomyQuery.query.filter(TaxonomyQuery.number==query_number).first()
    if query is not None:
        if query.status == 'finished':
            return "FINISHED"
        else:
            return "OPEN"
    else:
        return "ERROR"


@app.route('/taxonomy_hits_query/<query_number>')
def taxonomy_hits_query(query_number):
    query = TaxonomyQuery.query.filter(TaxonomyQuery.number==query_number).first()
    if query is not None:
        options = query.children.split(',')
        hits = Hit.query.filter(Hit.attachment_id==query.id).all()
        hit_string = ''
        if len(hits) >= 2:
            last_hit = hits.pop()
        elif len(hits) == 1:
            return answer_format(options, hits[0].answer_content)
        else:
            return 'Empty'
        for hit in hits:
            hit_string += answer_format(options, hit.answer_content)+'#'

        hit_string += answer_format(options, last_hit.answer_content)
        return hit_string
    else:
        return 'None'


#########//////////////////////For Yunfan's Experiments
@app.route('/jump_to_next_recognization_hit/<email>/<current_hit_id>')
def jump_to_next_recognization_hit(email, current_hit_id):
    current_hit = Hit.query.get(current_hit_id)
    current_hit.status = 'open'
    db.session.commit()
    return recognization_hit(email, current_hit_id)

@app.route('/recognization_hit/<email>/<current_hit_id>')
def recognization_hit(email, current_hit_id):
    worker = User.query.filter(User.email==email).first()
    if worker is None:
        return "Cannot find your email record... Please Check it again..."
    last_hit = recognization_controller.recover_ongoing_hit(worker)
    # print 'last_hit'
    print 'current_hit_id', current_hit_id
    if last_hit is None:
        # print 'last is none'
        if current_hit_id == "null":
            next_hit = recognization_controller.fetch_next_hit(worker, -1)
        else:
            next_hit = recognization_controller.fetch_next_hit(worker, current_hit_id)
    else:
        next_hit = last_hit

    if next_hit is not None:
        recognization_query = RecognizationQuery.query.get(next_hit.attachment_id)

        print 'ok'
        return render_template('recognization_hit.html',
                               email=email,
                               credits=worker.credit,
                               hit_value=next_hit.credit,
                               hit_number=next_hit.id,
                               image_name=recognization_query.image_name,
                               author_list=recognization_query.author_list,
                               )
    else:
        return "No tasks now... Please try later..."


@app.route('/recognization_answer_hit', methods=['POST'])
def answer_recognization_hit():
    print 'here'
    email = request.form['email_address']
    answer_content = request.form['answer_content']
    hit_number = request.form['hit_number']
    print "ok"
    return recognization_controller.answer_hit(hit_number, email, answer_content)


@app.route('/recognization_create', methods=['POST'])
def recognization_create():
    query_number = request.form['query_number']
    author_list = request.form['author_list']
    image_name = request.form['image_name']
    recognization_controller.create_query(query_number, author_list, image_name, 6)
    return "OK"


@app.route('/recognization_status_query/<query_number>')
def recognization_status_query(query_number):
    print query_number
    query = RecognizationQuery.query.filter(RecognizationQuery.number==query_number).first()
    if query is not None:
        if query.status == 'finished':
            return "FINISHED"
        else:
            return "OPEN"
    else:
        return "ERROR"


@app.route('/recognization_hits_query/<query_number>')
def recognization_hits_query(query_number):
    query = RecognizationQuery.query.filter(RecognizationQuery.number == query_number).first()
    if query is not None:
        hits = Hit.query.filter(Hit.attachment_id == query.id).all()
        hit_string = query.author_list+"#"
        if len(hits) == 0:
            return 'Empty'
        for hit in hits:
            hit_string += hit.answer_content + '#'

        return hit_string
    else:
        return 'None'
######################Hit finish############################


def answer_format(options, answer_content):
    number = answer_content[0]
    print(options)
    if number == '3' or number == '4':
        pre_option = answer_content[0:2]
        sub_options = answer_content[2:].split(',')
        for sub_option in sub_options:
            index = 0
            meet = False
            for option in options:
                if option == sub_option:
                    meet = True
                    pre_option += str(index)

                index += 1

            if not meet:
                pre_option += '-1'

            pre_option += ','
        print pre_option
        pre_option = pre_option[0: len(pre_option) - 1]

        return pre_option
    else:
        return answer_content




@app.route('/assignWorkers')
def assign_workers():
    task_controller.assign_temporal_task_to_workers()
    return "assignWorkers OK"

@app.route('/refreshTaskStatus')
def refresh_task_status():
    task_controller.refresh_task_status()
    return "refresh task status OK"

@app.route('/prepareTemporalTaskAnswers')
def prepareTemporalTaskAnswers():
    task_controller.extract_temporal_task_answers_to_table()
    return "prepare OK"


@app.route('/configUserQuality')
def configUserQuality():
    # task_controller.configUserQuality()
    # task_controller.export_user_qualities('/GMission-Server/export-files/')
    task_controller.export_worker_profile_user_id_map('/GMission-Server/export-files/')
    return "config OK"


@app.route('/getAnswerMessage', methods=['POST'])
def getTemporalAnswerById():
    answer_id = request.form['answer_id']
    temporal_answer = TemporalTaskAnswer.query.get(answer_id)
    if temporal_answer is not None:
        task = Task.query.get(temporal_answer.task_id)

        return jsonify(current_anwer_id=temporal_answer.id,
                       brief=temporal_answer.brief,
                       location_content=task.location.name,
                       task_lat=temporal_answer.task_latitude,
                       task_lon=temporal_answer.task_longitude,
                       worker_lat=temporal_answer.worker_profile.latitude,
                       worker_lon=temporal_answer.worker_profile.longitude,
                       pic_name=temporal_answer.attachment.value
                       )


@app.route('/rateTemporalAnswer', methods=['POST'])
def rateTemporalAnswer():
    print 'here'
    answer_id = request.form['answer_id']
    worker_email = request.form['email_address']
    value = request.form['value']
    rater = User.query.filter(User.email==worker_email).all()
    if len(rater) != 0:
        rater_id = rater[0].id
    else:
        rater_id = 1

    temporal_answer_rating = TemporalTaskAnswerRating(answer_id=answer_id,
                                                      rater_id=rater_id,
                                                      value=value)
    next_temporal_answer = TemporalTaskAnswer.query.filter(TemporalTaskAnswer.id > answer_id).limit(1).all()
    if len(next_temporal_answer) == 0:
        next_answer_id = -1
    else:
        next_answer_id = next_temporal_answer[0].id

    db.session.add(temporal_answer_rating)
    db.session.commit()

    return jsonify(next_answer_id=next_answer_id)


@app.route('/cleanTemporalTask')
def cleanTemporalTask():
    # for u in User.query.filter(User.id==49):
    #     return str(task_controller.query_online_users())
    # task = Task.query.filter(Task.id == '435').limit(1).all()
    # task_controller.calibrate_temporal_task_worker_velocity(task[0])
    # return str(task_controller.write_available_worker_profiles_to_file(1))
    # task_controller.calibrate_worker_profile()
    task_controller.clean_temporal_tasks_and_messages()
    # task_controller.test()
    return "test OK"


@app.route('/export')
def export():
    # task_controller.export_temporal_task_results(range(424,429), 'random_1min')  #redo
    # task_controller.export_temporal_task_results(range(429,434), 'random_2min')
    # task_controller.export_temporal_task_results(range(434,439), 'random_3min')
    # task_controller.export_temporal_task_results(range(439,444), 'random_4min')
    task_controller.export_temporal_task_results(range(817,822), 'greedy_1min')
    task_controller.export_temporal_task_results(range(812,817), 'greedy_2min')
    # task_controller.export_temporal_task_results(range(541,546), 'greedy_1min')
    # task_controller.export_temporal_task_results(range(546,551), 'greedy_2min')
    # task_controller.export_temporal_task_results(range(551,556), 'greedy_3min')
    # task_controller.export_temporal_task_results(range(556,566), 'greedy_4min')

    # task_controller.export_temporal_task_results(range(623,628), 'sampling_1min')
    task_controller.export_temporal_task_results(range(802,807), 'sampling_1min')
    # task_controller.export_temporal_task_results(range(707,712), 'sampling_2min')
    # task_controller.export_temporal_task_results(range(722,727), 'sampling_3min')
    # task_controller.export_temporal_task_results(range(616,621), 'sampling_4min')

    # task_controller.export_temporal_task_results(range(732,737), 'dv_1min')
    # task_controller.export_temporal_task_results(range(737,742), 'dv_2min')
    # task_controller.export_temporal_task_results(range(742,747), 'dv_3min')
    # task_controller.export_temporal_task_results(range(747,752), 'dv_4min')

    # task_controller.export_temporal_task_results(range(752,757), 'ground_1min')
    task_controller.export_temporal_task_results(range(822,827), 'ground_2min')
    # task_controller.export_temporal_task_results(range(757,762), 'ground_3min')
    task_controller.export_temporal_task_results(range(793,798), 'ground_4min')
    return "export OK"


@app.route('/marauders-map')
def marauders_map():
    users = User.query.all()

    user_traces = {}
    # for u in User.query.all()[:50]:
    for u in User.query.filter(User.id==36):
        traces = PositionTrace.query.filter_by(user=u).all()
        user_traces[u.id] = [(t.longitude, t.latitude) for t in traces]

    return render_template('marauders_map.html', users=users, user_traces=json.dumps(user_traces))



@cache.cached(timeout=3600, key_prefix='crabwords')
def load_crabwords():
    return [w.word for w in SensitiveWord.query.all()]


def is_cached_url(url):
    return url.endswith('/rest/location')


@app.before_request
def before_request():
    g.request_start_time = time.time()  # time.time is precise enough

    # if is_cached_url(request.url):
    #     cached_response = cache.get(request.url)
    #     if cached_response:
    #         cached_response.simple_url_cached = True
    #         return cached_response

    g.crabwords = [] #load_crabwords()

    profile_log(request.path, 'crab', time.time()-g.request_start_time)
    # print "[Before request:%s %s, %s]" % (request.method, request.url, request.json)


@app.after_request
def after_request(response):
    # resp_brief = response.data[:200] if 'json' in response.mimetype else ''
    # print "[After request:%s %s, %d, %s, %s]" % \
    #       (request.method, request.url, response.status_code, response.mimetype, resp_brief)
    # if not getattr(response, 'simple_url_cached', False):
    #     cache.set(request.url, response)
    return response


@app.teardown_request
def teardown_request(l):
    profile_log(request.path, time.time()-g.request_start_time)


@app.route('/matlab/<directory>')
def matlab(directory):
    return directory



#409 Conflict: the best HTTP code I can find
@app.errorhandler(409)
def conflict(e):
    print 'conflict!'
    obj = e.conflict_obj
    obj_dict = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    return jsonify(**obj_dict)
    # print e.get_single_url
    # return redirect(e.get_single_url, code=303)  # something wrong with redirect

