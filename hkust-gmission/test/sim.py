__author__ = 'chenzhao'


import time
from gmission.models import *
import random
from gmission import app


SIM_USER_IDS = range(1000000)
BULK_SIZE = 10000


def create_sim_users():
    existing_sim_user_ids = set([int(u[0][3:]) for u in db.session.query(User.name).filter(User.name.like('sim%')).all()])

    l = SIM_USER_IDS
    for ids in [l[i:i+BULK_SIZE] for i in range(0, len(l), BULK_SIZE)]:
        print ids
        db.engine.execute(User.__table__.insert(), [{'name': 'sim%d'%i, 'email': 'sim%d@sim.com'%i, 'password': '111111'}
                                                    for i in ids if i not in existing_sim_user_ids])
    db.session.commit()
    return


def sim_trace():
    # users = User.query.filter(User.name.like('sim%'))
    sim_user_ids = (u[0] for u in db.session.query(User.id).filter(User.name.like('sim%')))

    traces = []
    for user_id in sim_user_ids:
        lo = random.uniform(1, 100)
        la = random.uniform(1, 100)
        traces.append({'longitude':lo, 'latitude':la, 'radius':0, 'user_id':user_id})
        if len(traces) == BULK_SIZE:
            db.engine.execute(UserLastPosition.__table__.insert(), traces)
            db.session.commit()
            del traces[:]
            print BULK_SIZE, 'inserted'
    if traces:
        db.engine.execute(UserLastPosition.__table__.insert(), traces)
        db.session.commit()


def main():
    # create_sim_users()
    sim_trace()
    pass


if __name__=='__main__':
    main()



