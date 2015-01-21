__author__ = 'chenzhao'


import time
import random
import datetime
from unit_test import *

#
# SIM_USER_IDS = range(1000000)
# BULK_SIZE = 10000
#
#
# def create_sim_users():
#     existing_sim_user_ids = set([int(u[0][3:]) for u in db.session.query(User.name).filter(User.name.like('sim%')).all()])
#
#     l = SIM_USER_IDS
#     for ids in [l[i:i+BULK_SIZE] for i in range(0, len(l), BULK_SIZE)]:
#         print ids
#         db.engine.execute(User.__table__.insert(), [{'name': 'sim%d'%i, 'email': 'sim%d@sim.com'%i, 'password': '111111'}
#                                                     for i in ids if i not in existing_sim_user_ids])
#     db.session.commit()
#     return
#
#
# def sim_trace():
#     # users = User.query.filter(User.name.like('sim%'))
#     sim_user_ids = (u[0] for u in db.session.query(User.id).filter(User.name.like('sim%')))
#
#     traces = []
#     for user_id in sim_user_ids:
#         lo = random.uniform(1, 100)
#         la = random.uniform(1, 100)
#         traces.append({'longitude':lo, 'latitude':la, 'radius':0, 'user_id':user_id})
#         if len(traces) == BULK_SIZE:
#             db.engine.execute(UserLastPosition.__table__.insert(), traces)
#             db.session.commit()
#             del traces[:]
#             print BULK_SIZE, 'inserted'
#     if traces:
#         db.engine.execute(UserLastPosition.__table__.insert(), traces)
#         db.session.commit()



def create_sim_user(count):
    uids = []
    for i in range(count):
        id_str = 'sim_work_%d'%i
        user = dict(email='%s@sim.com'%(id_str,), password='1234567', name=id_str)
        rest_post('user', user)
        u = post('user/login', **user).json()
        uids.append(u['id'])
    return uids


def sim_trace():
    fire_bird_pos = (114.274277, 22.340725)
    total_workers = 10
    for uid in create_sim_user(total_workers):
        print uid
        steps = random.randint(10, 100)
        lon, lat = fire_bird_pos
        created_on = datetime.datetime(2015, 1, 1)
        for step in range(steps):
            lon_speed = random.random()/100000*random.choice([-1,1])   # meters/second , hopefully
            lat_speed = random.random()/100000*random.choice([-1,1])   # meters/second , hopefully
            duration = random.randint(5, 600)  # seconds
            lon += lon_speed*duration
            lat += lat_speed*duration
            created_on += datetime.timedelta(seconds=duration)
            trace = dict(longitude=lon, latitude=lat, z=0, user_id=uid, created_on=created_on.isoformat().split('.')[0])
            trace_j = rest_post('position_trace', trace).json()

    pass


def main():
    # create_sim_users()
    sim_trace()
    pass


if __name__=='__main__':
    main()



