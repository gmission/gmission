__author__ = 'chenzhao'

from gmission.models import *
from gmission.flask_app import app, db, stdout
import sys
import time

from import_data import clear_and_import_all


def check_db():
    tried_times = 0
    while tried_times < 30:
        try:
            with db.engine.connect() as conn:
                stdout('db is ready.')
                pass
        except Exception:
            time.sleep(1)
            tried_times += 1
            stdout('waiting for db', tried_times)
            sys.stdout.flush()
            continue
        return
    stdout('db is not ready, cannot start')
    raise Exception()


def drop_all_table():
    from sqlalchemy.engine import reflection
    from sqlalchemy.schema import MetaData, Table, DropTable, ForeignKeyConstraint, DropConstraint
    conn = db.engine.connect()
    trans = conn.begin()
    inspector = reflection.Inspector.from_engine(db.engine)
    metadata = MetaData()
    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(ForeignKeyConstraint((), (), name=fk['name']))
        t = Table(table_name, metadata, *fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))

    for table in tbs:
        conn.execute(DropTable(table))

    trans.commit()


def init_roles():
    requester = get_or_create(Role, name='requester', description='who can ask', )
    worker = get_or_create(Role, name='worker', description='who can answer', )
    admin = get_or_create(Role, name='admin', description='who can do anything', )
    return requester, worker, admin


def init_users():
    requester, worker, admin = init_roles()
    users = [
        # ('scheduler@gmission.com', '111111', 'Request Scheduler', [requester,]),
        #      ('zchenah@ust.hk', '111111', 'Chen Zhao', [admin, worker, requester]),
        #      ('rfu@connect.ust.hk', '111111', 'Free', [admin,worker, requester]),
        #      ('zhaoziyuan1991@gmail.com', '111111', 'Ziyuan', [admin, worker, requester]),
        #      ('haidaoxiaofei@gmail.com', '111111', 'Cheng Peng', [admin, worker, requester]),
        #      ('lxia@ust.hk', '111111', 'Leihao', [admin, worker, requester]),
        ('test1@xxx.com', '111111', 'Testing NO.1', [worker, requester]),
        ('test2@xxx.com', '111111', 'Testing NO.2', [worker, requester]),
        ('test3@xxx.com', '111111', 'Testing NO.3', [worker, requester]),
        ('test4@xxx.com', '111111', 'Testing NO.4', [worker, requester]),
        ('test5@xxx.com', '111111', 'Testing NO.5', [worker, requester]),
    ]
    for email, password, name, roles in users:
        user = get_or_create(User, email=email, password=password, name=name)
        for role in roles:
            user_datastore.add_role_to_user(user, role)
    db.session.commit()
    create_user_for_each_phone()


def create_user_for_each_phone():
    requester, worker, admin = init_roles()
    users = [
        # ('zopo_orange@ust.hk', '111111', 'zopo_orange', [worker, requester]),
        #      ('zopo_blue@ust.hk', '111111', 'zopo_blue', [worker, requester]),
        #      ('zopo_white@ust.hk', '111111', 'zopo_white', [worker, requester]),
        #      ('zopo_black@ust.hk', '111111', 'zopo_black', [worker, requester]),
        #      ('redmi1@ust.hk', '111111', 'redmi1', [worker, requester]),
        #      ('redmi2@ust.hk', '111111', 'redmi2', [worker, requester]),
        #      ('redmi3@ust.hk', '111111', 'redmi3', [worker, requester]),
        #      ('redmi4@ust.hk', '111111', 'redmi4', [worker, requester]),
        #      ('redmi5@ust.hk', '111111', 'redmi5', [worker, requester]),
        #      ('redmi6@ust.hk', '111111', 'redmi6', [worker, requester]),
        #      ('redmi7@ust.hk', '111111', 'redmi7', [worker, requester]),
        #      ('redmi8@ust.hk', '111111', 'redmi8', [worker, requester]),
        #      ('redmi9@ust.hk', '111111', 'redmi9', [worker, requester]),
        #      ('samsung_white@ust.hk', '111111', 'samsung_white', [worker, requester]),
        #      ('samsung_blue@ust.hk', '111111', 'samsung_blue', [worker, requester]),
        #      ('redmi1@ust.hk', '111111', 'redmi1', [worker, requester]),
        #      ('redmi2@ust.hk', '111111', 'redmi2', [worker, requester]),
        #      ('redmi3@ust.hk', '111111', 'redmi3', [worker, requester]),
        #      ('redmi4@ust.hk', '111111', 'redmi4', [worker, requester]),
        #      ('redmi5@ust.hk', '111111', 'redmi5', [worker, requester]),
        #      ('redmi6@ust.hk', '111111', 'redmi6', [worker, requester]),
        #      ('redmi7@ust.hk', '111111', 'redmi7', [worker, requester]),
        #      ('redmi8@ust.hk', '111111', 'redmi8', [worker, requester]),
        #      ('redmi9@ust.hk', '111111', 'redmi9', [worker, requester]),
        #      ('backup1@ust.hk', '111111', 'backup1', [worker, requester]),
        #      ('backup2@ust.hk', '111111', 'backup2', [worker, requester]),
    ]
    for email, password, name, roles in users:
        user = get_or_create(User, email=email, password=password, name=name)
        for role in roles:
            user_datastore.add_role_to_user(user, role)
    db.session.commit()


def init_assign_messages():
    pass


def init_user_roles():
    user_role_admin = get_or_create(Role, name='admin', description='who can do anything')
    user_role_user = get_or_create(Role, name='user', description='user')


def init_data():
    init_user_roles()
    init_users()
    # clear_and_import_all()
    # init_assign_messages()


def init_db():
    db.create_all()


if __name__ == '__main__':
    # drop_all_table()
    stdout('<<<<<<init db begin.')
    check_db()
    # drop_all_table()
    init_db()
    init_data()
    stdout('>>>>>>init db done.')
    # raise Exception("error")
    # clear_and_import_all()
    pass
