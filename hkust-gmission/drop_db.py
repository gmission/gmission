#!/usr/bin/env python
# encoding: utf-8
__author__ = 'rui'

from gmission.flask_app import app, db, stdout


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


if __name__ == '__main__':
    drop_all_table()
    pass
