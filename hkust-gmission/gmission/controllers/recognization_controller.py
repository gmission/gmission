__author__ = 'bigstone'

from gmission.models.crowdsourcing import *
from gmission.models import *
from gmission.flask_app import app, ROOT
import sys


EACH_QUERY_HITS = 6
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
        check_finish_recognization_query(current_hit.attachment_id)
        return "OK"


def check_finish_recognization_query(query_id):
    finished_hits = Hit.query.filter(Hit.attachment_id == query_id).filter(Hit.status == "finished").all()
    if len(finished_hits) >= EACH_QUERY_HITS:
        recognization_query = RecognizationQuery.query.get(query_id)
        recognization_query.status = 'finished'

        db.session.commit()


def fetch_next_hit(assigned_worker, hit_number):
    print hit_number
    current_hit = Hit.query.filter(Hit.id >= hit_number).filter(Hit.attachment_type == 'recognization').filter(Hit.status == 'open').first()
    if current_hit is not None:
        current_recognization_query = RecognizationQuery.query.get(current_hit.attachment_id)
        while True:
            print 'next_query', current_recognization_query.id
            has_answered = False
            if current_recognization_query is not None:
                #next_hit cannot equal to None
                next_hit = Hit.query.filter(Hit.attachment_type == 'recognization').filter(Hit.attachment_id > current_recognization_query.id).filter(Hit.status=='open').first()
                sibling_hits = Hit.query.filter(Hit.attachment_type == 'recognization').filter(Hit.attachment_id > current_recognization_query.id).filter(Hit.status!='open').all()

                for sibling_hit in sibling_hits:
                    if sibling_hit.worker_id == assigned_worker.id:
                        has_answered = True
                        break
                if has_answered == True:
                    current_recognization_query = RecognizationQuery.query.filter(RecognizationQuery.id > current_recognization_query.id).filter(RecognizationQuery.status == 'open').first()
                else:
                    next_hit.status = 'assigned'
                    next_hit.deadline = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    next_hit.worker_id = assigned_worker.id
                    db.session.commit()
                    return next_hit
            else:
                print 'no next taxonomy_query'
                return None
    return None

def check_timeout_hits():
    timeout_hits = Hit.query.filter(Hit.deadline < datetime.datetime.now()).filter(Hit.status=='assigned').all()
    Hit.query.filter(Hit.deadline < datetime.datetime.now()).filter(Hit.status=='assigned').update({'status': 'open'}, synchronize_session=False)
    db.session.commit()


def fetch_first_hit(assigned_worker):
    print 'first hit'
    next_query = RecognizationQuery.query.filter(RecognizationQuery.status=='open').first()
    if next_query is not None:
        next_hit = Hit.query.filter(Hit.status=='open').filter(Hit.attachment_type == 'recognization').filter(Hit.attachment_id == next_query.id).first()
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
    hit = Hit.query.filter(Hit.status=='assigned').filter(Hit.attachment_type=='recognization').filter(Hit.worker_id==worker.id).first()
    return hit


def create_query(number, author_list, image_name, times):
    query_record = RecognizationQuery(number=number,
                                 author_list=author_list,
                                 image_name=image_name,
                                 status='open'
                                 )
    db.session.add(query_record)
    db.session.commit()
    for i in range(1, times+1):
        hit = Hit(competition_id=3,
                  attachment_type='recognization',
                  attachment_id=query_record.id,
                  credit=1,
                  answer_content='Null',
                  status='open'
                  )
        db.session.add(hit)

    db.session.commit()

