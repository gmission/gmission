__author__ = 'bigstone'

from gmission.models.crowdsourcing import *
from gmission.models import *
from gmission.flask_app import app, ROOT
import sys


EACH_QUERY_HITS = 3
def answer_hit(hit_number, worker_email, answer_content):
    current_hit = Hit.query.get(hit_number)
    worker = User.query.filter(User.email == worker_email).first()
    if worker is None:
        return "error email"
    else:
        current_hit.worker_id = worker.id
        worker.credit += current_hit.credit
        current_hit.answer_content = answer_content
        current_hit.status = 'finished'

        db.session.commit()
        check_finish_table_head_query(current_hit.attachment_id)
        return "OK"


def check_finish_table_head_query(query_id):
    finished_hits = Hit.query.filter(Hit.attachment_id == query_id).filter(Hit.status == "finished").all()
    if len(finished_hits) >= EACH_QUERY_HITS:
        table_head_query = TableHeadQuery.query.get(query_id)
        table_head_query.status = 'finished'

        db.session.commit()


def fetch_next_hit(assigned_worker, hit_number):
    print hit_number
    current_hit = Hit.query.filter(Hit.id >= hit_number).filter(Hit.attachment_type == 'table_head').filter(Hit.status == 'open').first()
    if current_hit is not None:
        current_table_head_query = TableHeadQuery.query.get(current_hit.attachment_id)
        while True:
            has_answered = False
            if current_table_head_query is not None:
                #next_hit cannot equal to None
                next_hit = Hit.query.filter(Hit.attachment_type == 'table_head').filter(Hit.attachment_id > current_table_head_query.id).filter(Hit.status=='open').first()
                if next_hit is None:
                    return None
                sibling_hits = Hit.query.filter(Hit.attachment_type == 'table_head').filter(Hit.attachment_id == next_hit.attachment_id).filter(Hit.status!='open').all()

                print 'next_query', current_table_head_query.id

                for sibling_hit in sibling_hits:
                    if sibling_hit.worker_id == assigned_worker.id:
                        has_answered = True
                        break
                if has_answered == True:
                    current_table_head_query = TableHeadQuery.query.filter(TableHeadQuery.id > current_table_head_query.id).filter(TableHeadQuery.status == 'open').all()
                    if len(current_table_head_query) != 0:
                        current_table_head_query = current_table_head_query[0]
                else:
                    next_hit.status = 'assigned'
                    next_hit.deadline = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    next_hit.worker_id = assigned_worker.id
                    db.session.commit()
                    return next_hit
            else:
                print 'no next query'
                return None
    return None


def fetch_first_hit(assigned_worker):
    print 'first hit'
    next_query = TableHeadQuery.query.filter(TableHeadQuery.status=='open').first()
    if next_query is not None:
        next_hit = Hit.query.filter(Hit.status=='open').filter(Hit.attachment_type == 'table_head').filter(Hit.attachment_id == next_query.id).first()
        if next_hit is not None:
            next_hit.status = 'assigned'
            next_hit.deadline = datetime.datetime.now() + datetime.timedelta(minutes=10)
            next_hit.worker_id = assigned_worker.id
            db.session.commit()
            return next_hit
        else:
            print 'no opened hit'
            return None
    else:
        print 'no opened query'
        return None


def recover_ongoing_hit(worker):
    print 'recovering ongoing hit'
    hit = Hit.query.filter(Hit.status=='assigned').filter(Hit.attachment_type=='table_head').filter(Hit.worker_id==worker.id).first()
    return hit


def create_query(number, table_content, times):
    query_record = TableHeadQuery(number=number,
                                 table_content=table_content,
                                 status='open'
                                 )
    db.session.add(query_record)
    db.session.commit()
    for i in range(1, times+1):
        hit = Hit(competition_id=4,
                  attachment_type='table_head',
                  attachment_id=query_record.id,
                  credit=1,
                  answer_content='Null',
                  status='open'
                  )
        db.session.add(hit)

    db.session.commit()

#for Close questions###################################################################################################

def answer_hit_c(hit_number, worker_email, answer_content):
    current_hit = Hit.query.get(hit_number)
    worker = User.query.filter(User.email == worker_email).first()
    if worker is None:
        return "error email"
    else:
        current_hit.worker_id = worker.id
        worker.credit += current_hit.credit
        current_hit.answer_content = answer_content
        current_hit.status = 'finished'

        db.session.commit()
        check_finish_table_head_query(current_hit.attachment_id)
        return "OK"




def fetch_next_hit_c(assigned_worker, hit_number):
    print hit_number
    current_hit = Hit.query.filter(Hit.id >= hit_number).filter(Hit.attachment_type == 'table_head_c').filter(Hit.status == 'open').first()
    if current_hit is not None:
        current_table_head_query = TableHeadQuery.query.get(current_hit.attachment_id)
        while True:
            has_answered = False
            if current_table_head_query is not None:
                #next_hit cannot equal to None
                next_hit = Hit.query.filter(Hit.attachment_type == 'table_head_c').filter(Hit.attachment_id > current_table_head_query.id).filter(Hit.status=='open').first()
                if next_hit is None:
                    return None
                sibling_hits = Hit.query.filter(Hit.attachment_type == 'table_head_c').filter(Hit.attachment_id == next_hit.attachment_id).filter(Hit.status!='open').all()

                print 'next_query', current_table_head_query.id

                for sibling_hit in sibling_hits:
                    if sibling_hit.worker_id == assigned_worker.id:
                        has_answered = True
                        break
                if has_answered == True:
                    current_table_head_query = TableHeadQuery.query.filter(TableHeadQuery.id > current_table_head_query.id).filter(TableHeadQuery.status == 'open').all()
                    if len(current_table_head_query) != 0:
                        current_table_head_query = current_table_head_query[0]
                else:
                    next_hit.status = 'assigned'
                    next_hit.deadline = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    next_hit.worker_id = assigned_worker.id
                    db.session.commit()
                    return next_hit
            else:
                print 'no next query'
                return None
    return None


def fetch_first_hit_c(assigned_worker):
    print 'first hit'
    next_query = TableHeadQuery.query.filter(TableHeadQuery.status=='open').first()
    if next_query is not None:
        next_hit = Hit.query.filter(Hit.status=='open').filter(Hit.attachment_type == 'table_head_c').filter(Hit.attachment_id == next_query.id).first()
        if next_hit is not None:
            next_hit.status = 'assigned'
            next_hit.deadline = datetime.datetime.now() + datetime.timedelta(minutes=10)
            next_hit.worker_id = assigned_worker.id
            db.session.commit()
            return next_hit
        else:
            print 'no opened hit'
            return None
    else:
        print 'no opened query'
        return None


def recover_ongoing_hit_c(worker):
    print 'recovering ongoing hit'
    hit = Hit.query.filter(Hit.status=='assigned').filter(Hit.attachment_type=='table_head_c').filter(Hit.worker_id==worker.id).first()
    return hit


def create_query_c(number, table_content, conclusion, times):
    query_record = TableHeadQuery(number=number,
                                 table_content=table_content,
                                 conclusion=conclusion,
                                 status='open'
                                 )
    db.session.add(query_record)
    db.session.commit()
    for i in range(1, times+1):
        hit = Hit(competition_id=5,
                  attachment_type='table_head_c',
                  attachment_id=query_record.id,
                  credit=1,
                  answer_content='Null',
                  status='open'
                  )
        db.session.add(hit)

    db.session.commit()
