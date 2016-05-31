__author__ = 'chenzhao'

from gmission.models import *
from gmission.flask_app import app, db, stdout
import sys
import time


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
    user_role_admin = get_or_create(Role, name='admin', description='who can do anything')
    user_role_user = get_or_create(Role, name='user', description='user')
    campaign_role_owner = get_or_create(CampaignRole, name='owner', description='owner')
    campaign_role_participant = get_or_create(CampaignRole, name='participant', description='participant')
    print 'init roles:', user_role_admin, user_role_user, campaign_role_owner, campaign_role_participant
    db.session.commit()
    return user_role_admin, user_role_user


def init_users():
    admin, user = init_roles()
    users = [
        ('zchenah@ust.hk', '111111', 'chenzhao', [admin, user]),
        ('haidaoxiaofei@gmail.com', '111111', 'chengpeng', [admin, user]),
        ('test1@xxx.com', '111111', 'test1', [user]),
        ('test2@xxx.com', '111111', 'test2', [user]),
        ('test3@xxx.com', '111111', 'test3', [user]),
        ('test4@xxx.com', '111111', 'test4', [user]),
        ('test5@xxx.com', '111111', 'test5', [user]),
    ]
    for email, password, username, roles in users:
        user = get_or_create(User, username=username, email=email, source="python")
        user.hash_password(password)
        for role in roles:
            user_datastore.add_role_to_user(user, role)
    db.session.commit()


if __name__ == '__main__':
    stdout('<<<<<<init db begin.')
    check_db()
    # drop_all_table()
    db.create_all()
    init_users()
    stdout('>>>>>>init db done.')
    # clear_and_import_all()
    pass
