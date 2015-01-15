__author__ = 'chenzhao'
# coding:utf8

import gevent;
from gevent import monkey; monkey.patch_all()



import os
import sys
import json
import flask
import random
import urllib2
import datetime
from termcolor import colored


from geventhttpclient import HTTPClient
from geventhttpclient.url import URL



def color_print(color, *args):
    colored_str = colored(' '.join(map(str, args)), color)
    # print type(colored_str)
    # print repr(colored_str)
    print colored_str


def http_debug(*args):
    return
    newargs = list(args)
    newargs.insert(0, '[')
    newargs.append(']')
    color_print('grey', *newargs)

url_root = 'http://127.0.0.1:5000/'


def post(urlpath, **kw):
    url = url_root+urlpath
    json_data = json.dumps(kw)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    http_debug('POST', url, json_data)
    resp = requests.post(url, data=json_data, headers=headers)
    http_debug('Response:', resp.status_code, resp.content[:60], '...')
    return resp


def put(urlpath, **kw):
    url = url_root+urlpath
    json_data = json.dumps(kw)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    http_debug('POST', url, json_data)
    resp = requests.put(url, data=json_data, headers=headers)
    http_debug('Response:', resp.status_code, resp.content[:60], '...')
    return resp


def upload(urlpath, filename):
    url = url_root+urlpath
    files = {'file': open(filename, 'rb')}
    resp = requests.post(url, files=files)
    return resp


def get(urlpath):
    url = url_root+urlpath
    # headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    # json_params = json.dumps(kw) if kw else ''
    http_debug('GET', url)
    resp = requests.get(url)
    http_debug('Response:', resp.status_code, resp.content[:60], '...')
    return resp


def delete(urlpath):
    url = url_root+urlpath
    http_debug('DELETE', url)
    resp = requests.delete(url)
    http_debug('Response:', resp.status_code, resp.content[:60], '...')
    assert resp.status_code==204
    return resp


def rest_post(name, obj_dict):
    return post('rest/'+name, **obj_dict)


def rest_get_many(name, filter_dict={}):
    filters = []
    for col_name, col_val in filter_dict.items():
        filters.append(dict(name=col_name, op='==', val=col_val))

    if filters:
        return get('rest/'+name+'?q='+json.dumps(dict(filters=filters)))
    else:
        return get('rest/'+name)


def rest_get(name, _id):
    return get('rest/%s/%d' % (name, _id)).json()


def rest_get_list(name, filter_dict={}):
    return rest_get_many(name, filter_dict).json()['objects']


def rest_put(name, _id, data):
    return put('rest/%s/%d' % (name, _id), **data)


def rest_delete_all(name, filter_dict):
    objs_to_del = rest_get_list(name, filter_dict)
    # print objs_to_del
    for obj in objs_to_del:
        urlpath='rest/%s/%d'%(name, obj['id'])
        delete(urlpath)
    return len(objs_to_del)


def test_case(func, **kw):
    def run_test_case(**kw):
        print '-'*80+'\nTest case begin:', func.__name__
        r = func(**kw)
        # try:
        #     r = func(**kw)
        # except Exception as e:
        #     exc_type, exc_j, exc_tb = sys.exc_info()
        #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #     color_print('red', e, exc_type, fname, exc_tb.tb_lineno)
        #     r = False
        color_print('green' if r else 'red', 'Test case end  :', func.__name__, 'OK' if r else 'failed')
        return r
    return run_test_case


users = [dict(email='test1@xxx.com', password='111111'),
         dict(email='test2@xxx.com', password='111111'),
         dict(email='test3@xxx.com', password='111111'),
         dict(email='test4@xxx.com', password='111111'),
         dict(email='test5@xxx.com', password='111111')]
users_j = []

@test_case
def test_user_created():
    global users, users_j
    users_j = [post('user/login', **u).json() for u in users]
    assert all(u['id'] for u in users_j)
    return True


@test_case
def user_register_new():
    new_user = dict(email='testcase_new_user@test.com', password='1234567', name='testcase_new')
    rest_delete_all('user', dict(email=new_user['email']))

    r = post('user/register', **new_user)
    assert r.status_code == 200
    rjson = r.json()
    assert rjson['res'] == 0
    assert rjson['email'] == new_user['email']
    assert rjson['name'] == new_user['name']
    roles = rjson['roles']
    assert 'requester' in roles and 'worker' in roles and 'admin' not in roles
    assert rjson['token'] and rjson['id'] and rjson['credit']
    return True


@test_case
def user_register_existing():
    existing_user = dict(email='testcase_existing_user@test.com', password='1234567', name='testcase_existing')
    rest_post('user', existing_user)

    r = post('user/register', **existing_user)
    assert r.status_code == 200
    assert r.json()['res'] != 0
    return True


@test_case
def user_login_success():
    user = dict(email='testcase_existing_user@test.com', password='1234567', name='testcase_existing')
    rest_post('user', user)

    r = post('user/login', email=user['email'], password=user['password'])
    assert r.status_code == 200
    rjson = r.json()
    assert rjson['res'] == 0
    assert rjson['email'] == user['email']
    assert rjson['name'] == user['name']
    assert rjson['token'] and rjson['id'] and rjson['credit']

    r = post('user/login', name=user['name'], password=user['password'])
    assert r.status_code == 200
    rjson = r.json()
    assert rjson['res'] == 0
    assert rjson['email'] == user['email']
    assert rjson['name'] == user['name']
    assert rjson['token'] and rjson['id'] and rjson['credit']

    return True

@test_case
def user_login_fail():
    user = dict(email='testcase_existing_user@test.com', password='1234567', name='testcase_existing')
    rest_post('user', user)

    r = post('user/login', email=user['email'], password=user['password']+'asdf')
    assert r.status_code == 200
    rjson = r.json()
    assert rjson['res'] != 0
    return True

@test_case
def new_image_task():
    user = dict(email='testcase_existing_user@test.com', password='1234567', name='testcase_existing')
    r = post('user/login', email=user['email'], password=user['password'])
    user_j = r.json()

    bound = dict(left_top_longitude=100,
                    left_top_latitude=120,
                    right_bottom_longitude=101,
                    right_bottom_latitude=121)
    location = dict(name='testlocation', longitude=110, latitude=119, bound=bound)
    new_task = dict(type='image',
                    brief='test new image task',
                    credit=10,
                    required_answer_count=3,
                    requester_id=user_j['id'],
                    location=location)

    r = rest_post('task', new_task)
    task_j = r.json()
    assert task_j['id'] and task_j['begin_time'] and task_j['end_time'] and task_j['location_id']
    assert task_j['status'] == 'open'
    assert task_j['type'] == new_task['type']
    assert task_j['credit'] == new_task['credit']
    assert task_j['requester_id'] == new_task['requester_id']
    return True




@test_case
def new_task_with_existing_location():
    user = dict(email='testcase_existing_user@test.com', password='1234567', name='testcase_existing')
    r = post('user/login', email=user['email'], password=user['password'])
    user_j = r.json()

    bound = dict(left_top_longitude=100, left_top_latitude=120, right_bottom_longitude=101, right_bottom_latitude=121)
    location = dict(name='testlocation', longitude=110, latitude=119, bound=bound)
    r = rest_post('location', location)
    location_j = r.json()

    new_task = dict(type='image',
                    brief='test new image task',
                    credit=10,
                    required_answer_count=3,
                    requester_id=user_j['id'],
                    location=location)

    r = rest_post('task', new_task)
    task_j = r.json()
    assert task_j['id'] and task_j['begin_time'] and task_j['end_time'] and task_j['location_id']
    assert task_j['status'] == 'open'
    assert task_j['type'] == new_task['type']
    assert task_j['credit'] == new_task['credit']
    assert task_j['requester_id'] == new_task['requester_id']

    assert task_j['location_id'] == location_j['id']
    return True


@test_case
def upload_image():
    filename = 'HKUST.jpeg'
    file_j = upload('image/upload', filename).json()

    assert filename in file_j['filename']
    assert file_j['size'] == os.path.getsize(filename)

    r = get('image/original/'+file_j['filename'])
    assert int(r.headers['content-length']) == os.path.getsize(filename)

    r = get('image/thumb/'+file_j['filename'])
    assert 0 < int(r.headers['content-length']) < os.path.getsize(filename)

    return True


@test_case
def new_answer_with_image():
    requester = dict(email='testcase_requester@test.com', password='1234567', name='testcase_requester')
    requester_j = rest_post('user', requester).json()

    worker = dict(email='testcase_worker@test.com', password='1234567', name='testcase_worker')
    worker_j = rest_post('user', worker).json()

    bound = dict(left_top_longitude=100, left_top_latitude=120, right_bottom_longitude=101, right_bottom_latitude=121)
    location = dict(name='testlocation', longitude=110, latitude=119, bound=bound)
    task = dict(type='image', brief='test new image task', requester_id=requester_j['id'], location=location, credit=10)
    task_j = rest_post('task', task).json()

    original_filename = 'HKUST.jpeg'
    filename = upload('image/upload', original_filename).json()['filename']
    attachment = dict(name='image name', type='image', value=filename)
    answer = dict(task_id=task_j['id'], brief='test image answer', type='image', location=location,
                  worker_id=worker_j['id'], attachment=attachment)

    r = rest_post('answer', answer)
    answer_j = r.json()
    assert answer_j['task_id'] == task_j['id']
    att = rest_get('attachment', answer_j['attachment_id'])
    assert att['value'] == filename

    answers_of_task = rest_get_list('answer', dict(task_id=task_j['id']))
    assert answer_j['id'] in (a['id'] for a in answers_of_task)

    messages = rest_get_list('message', dict(receiver_id=requester_j['id']))
    assert str(task_j['id']) in [m['attachment'] for m in messages]

    return True



@test_case
def comment_answer():
    requester = dict(email='testcase_requester@test.com', password='1234567', name='testcase_requester')
    requester_j = rest_post('user', requester).json()
    worker = dict(email='testcase_worker@test.com', password='1234567', name='testcase_worker')
    worker_j = rest_post('user', worker).json()
    bound = dict(left_top_longitude=100, left_top_latitude=120, right_bottom_longitude=101, right_bottom_latitude=121)
    location = dict(name='testlocation', longitude=110, latitude=119, bound=bound)
    task = dict(type='image', brief='test answer comment task', requester_id=requester_j['id'], location=location, credit=10)
    task_j = rest_post('task', task).json()

    original_filename = 'HKUST.jpeg'
    filename = upload('image/upload', original_filename).json()['filename']
    attachment = dict(name='image name', type='image', value=filename)
    answer = dict(task_id=task_j['id'], brief='test image answer', type='image', location=location,
                  worker_id=worker_j['id'], attachment=attachment)
    r = rest_post('answer', answer)
    answer_j = r.json()
    comment = dict(answer_id=answer_j['id'], content='this is a comment', sender_id=requester_j['id'],
                   receiver_id=worker_j['id'])
    comment_j = rest_post('answer_comment', comment)

    messages = rest_get_list('message', dict(receiver_id=worker_j['id']))
    assert str(answer_j['id']) in [m['attachment'] for m in messages]

    return True


def enough_answer():
    requester = dict(email='testcase_requester@test.com', password='1234567', name='testcase_requester')
    requester_j = rest_post('user', requester).json()

    location = dict(name='testlocation', longitude=110, latitude=119)
    task = dict(type='image', brief='test answer', requester_id=requester_j['id'],
                credit=2, required_answer_count=3, location=location)
    task_j = rest_post('task', task).json()

    global users
    workers = []
    for u in users[:task['required_answer_count']]:
        worker = rest_post('user', u).json()
        workers.append(worker)
        answer = dict(task_id=task_j['id'], brief='test answer', type='image', worker_id=worker['id'])
        rest_post('answer', answer)

    for u, worker_before in zip(users[:task['required_answer_count']], workers):
        worker_after = rest_post('user', u).json()
        assert worker_after['credit'] - worker_before['credit'] == task['credit']

    requester_j_after = rest_post('user', requester).json()
    assert requester_j['credit'] - requester_j_after['credit'] == task['credit']*task['required_answer_count']

    return True


@test_case
def user_last_location():
    global users
    user = rest_post('user', users[0]).json()

    trace = dict(longitude=random.random(), latitude=random.random(), z=random.randint(-9, 9), user_id=user['id'])
    trace_j = rest_post('position_trace', trace).json()
    position_l = rest_get_list('user_last_position', {'user_id':user['id']})
    assert len(position_l) == 1
    position_j = position_l[0]
    assert position_j['longitude'] == trace_j['longitude']
    assert position_j['latitude'] == trace_j['latitude']
    assert position_j['z'] == trace_j['z']

    return True


@test_case
def noti_nearby_user_for_new_task():
    global users
    nearby_worker = rest_post('user', users[0]).json()
    requester = rest_post('user', users[1]).json()

    trace = dict(longitude=random.random(), latitude=random.random(), z=random.randint(-9, 9), user_id=nearby_worker['id'])
    # print trace
    trace_j = rest_post('position_trace', trace).json()
    # print trace_j

    location = dict(name='testlocation with someone nearby %f, %f'%(trace['longitude'], trace['latitude']),
                    longitude=trace['longitude'], latitude=trace['latitude'])
    new_task = dict(type='mix', brief='test new image task', requester_id=requester['id'], location=location)
    task_j = rest_post('task', new_task).json()

    messages = rest_get_list('message', dict(receiver_id=nearby_worker['id']))
    assert str(task_j['id']) in [m['attachment'] for m in messages]

    return True


@test_case
def new_text_task():
    global users
    requester = rest_post('user', users[1]).json()

    location = dict(name='testlocation', longitude=110, latitude=119)
    options = [{'type': 'text', 'brief':'text answer %d'%(i), "worker_id":requester['id']} for i in range(3)]

    new_task = dict(type='text', brief='test new choice task', requester_id=requester['id'], location=location, answers=options)

    task_j = rest_post('task', new_task).json()
    answers_of_task = rest_get_list('answer', dict(task_id=task_j['id']))
    for opt in options:
        assert opt['brief'] in [a['brief'] for a in answers_of_task]
    # print task_j

    return True

@test_case
def put_existing_answer():
    global users
    requester = rest_post('user', users[1]).json()

    worker = dict(email='testcase_worker@test.com', password='1234567', name='testcase_worker')
    worker_j = rest_post('user', worker).json()

    location = dict(name='testlocation', longitude=110, latitude=119)
    # options = [{'type': 'text', 'brief':'text answer %d'%(i), "worker_id":requester['id']} for i in range(3)]

    new_task = dict(type='text', brief='test new text task', requester_id=requester['id'], location=location)

    task_j = rest_post('task', new_task).json()


    answer = dict(task_id=task_j['id'], brief='test text answer', type='text', location=location,
                  worker_id=worker_j['id'])

    r = rest_post('answer', answer)
    answer_j = r.json()
    assert answer_j['task_id'] == task_j['id']
    assert answer_j['brief'] == answer['brief']

    answer['brief'] = 'modified text answer'
    r = rest_put('answer', answer_j['id'] ,answer)
    answer_j = r.json()
    assert answer_j['brief'] == answer['brief']

    answers_of_task = rest_get_list('answer', dict(task_id=task_j['id']))
    # print task_j

    return True


@test_case
def new_checkin():
    global users
    user = rest_post('user', users[1]).json()

    location = dict(name='testlocation', longitude=110, latitude=119)

    new_checkin = dict(type='text', content='test new checkin', user_id=user['id'], location=location)

    checkin_j = rest_post('checkin', new_checkin).json()
    # print checkin_j

    return True


# def new_task_with_random_location_from_random_use():


def rand_xy():
    x = random.randint(100, 110)+random.random()
    y = random.randint(100, 110)+random.random()
    return x, y


all_names = ["世界之窗", "前广场", "世界之窗北门", "世界之窗南门", "世界之窗北侧门", "大胡子艺术", "世界文化浮雕墙", "世界地图喷泉", "环球舞台",
       "亚马逊丛林穿越", "巴西耶稣山", "墨西哥巨石头像", "秘鲁那斯卡图线壁", "印加迷城攀岩", "墨西哥凝神武士像", "印第安射箭场", "印第安图腾柱",
       "印第安民居", "巴西议会大厦", "美国自由女神像", "美国白宫", "美国国会大厦", "美国林肯纪念堂", "美国总统山", "科罗拉多峡谷漂流", "科罗拉多大峡谷",
       "金字塔探秘", "非洲民居", "埃及基萨金字塔群", "埃及阿布辛伯勒神庙", "玻璃凯旋门", "阿尔卑斯冰雪世界"]


def new_task_concurrent(thread_id):
    begin_time = time.time()
    location_name = u'西贡区大学道'
    # location_name = all_names[random.randint(0, len(all_names)-1)]
    requester_id = 40

    bound = dict(left_top_longitude=100, left_top_latitude=120, right_bottom_longitude=101, right_bottom_latitude=121)
    location = dict(name=location_name, longitude=110, latitude=119, bound=bound)

    new_task = dict(type='image',
                    brief='test concurrent',
                    credit=10,
                    required_answer_count=3,
                    requester_id=requester_id,
                    location=location)

    r = rest_post('task', new_task)
    task_j = r.json()
    end_time = time.time()
    print 'single cost', thread_id, end_time-begin_time
    assert task_j['id'] and task_j['begin_time'] and task_j['end_time'] and task_j['location_id']
    assert task_j['status'] == 'open'
    assert task_j['type'] == new_task['type']
    assert task_j['credit'] == new_task['credit']
    assert task_j['requester_id'] == new_task['requester_id']

# @test_case
def new_task_with_random_location():
    user = dict(email='testcase_existing_user@test.com', password='1234567', name='testcase_existing')
    r = post('user/login', email=user['email'], password=user['password'])
    user_j = r.json()

    bound = dict(left_top_longitude=100, left_top_latitude=120, right_bottom_longitude=101, right_bottom_latitude=121)
    x,y = rand_xy()
    location = dict(name='testlocation(%.4f,%.4f)'%(x,y), longitude=x, latitude=y, bound=bound)
    r = rest_post('location', location)
    location_j = r.json()

    new_task = dict(type='image',
                    brief='test random location task',
                    credit=10,
                    required_answer_count=3,
                    requester_id=user_j['id'],
                    location=location)

    r = rest_post('task', new_task)
    task_j = r.json()
    assert task_j['id'] and task_j['begin_time'] and task_j['end_time'] and task_j['location_id']
    assert task_j['status'] == 'open'
    assert task_j['type'] == new_task['type']
    assert task_j['credit'] == new_task['credit']
    assert task_j['requester_id'] == new_task['requester_id']

    assert task_j['location_id'] == location_j['id']
    return True


def run_all_cases(n):
    test_user_created()

    user_register_new()
    user_register_existing()
    user_login_success()
    user_login_fail()
    new_image_task()
    new_task_with_existing_location()
    # upload_image()
    # new_answer_with_image()
    comment_answer()
    enough_answer()
    user_last_location()
    noti_nearby_user_for_new_task()
    new_text_task()
    put_existing_answer()
    new_checkin()
    print n


def get_simple(n):
    url = 'http://gmission-asia.cloudapp.net/gmission_szww/test_data?size=10000'
    data = urllib2.urlopen(url).read()


req_counter = 0
total_limit = 50000
def concurrent_test_unit(seq):
    global req_counter, total_limit
    while req_counter < total_limit:
        req_counter += 1
        get_simple(seq)
        # print req_counter


def gevent_test():
    con = 500
    print 'concurrent begin', con
    begin = datetime.datetime.now()
    jobs = [gevent.spawn(concurrent_test_unit, i) for i in range(con)]
    gevent.joinall(jobs)
    end = datetime.datetime.now()
    print 'time:', (end-begin).total_seconds()
    print 'rps:', total_limit/(end-begin).total_seconds()


def main():
    global url_root
    url_root = 'http://gmission-asia.cloudapp.net/gmission_szww/'
    gevent_test()


if __name__=='__main__':
    main()
