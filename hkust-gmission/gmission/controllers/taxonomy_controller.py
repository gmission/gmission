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
        check_finish_taxonomy_query(current_hit.attachment_id)
        return "OK"


def check_finish_taxonomy_query(query_id):
    finished_hits = Hit.query.filter(Hit.attachment_id == query_id).filter(Hit.status == "finished").all()
    if len(finished_hits) >= EACH_QUERY_HITS:
        taxonomy_query = TaxonomyQuery.query.get(query_id)
        taxonomy_query.status = 'finished'

        db.session.commit()


def fetch_next_hit(assigned_worker, hit_number):
    current_hit = Hit.query.get(hit_number)
    if current_hit is not None:
        current_taxonomy_query = TaxonomyQuery.query.get(current_hit.attachment_id)
        while True:
            next_taxonomy_query = TaxonomyQuery.query.filter(TaxonomyQuery.id > current_hit.attachment_id).filter(TaxonomyQuery.status == 'open').first()

            if next_taxonomy_query is not None:
                next_hit = Hit.query.filter(Hit.attachment_type == 'taxonomy').filter(Hit.attachment_id == next_taxonomy_query.id).filter(Hit.status=='open').first()
                if next_hit is not None:
                    next_hit.status = 'assigned'
                    next_hit.deadline = datetime.datetime.now() + datetime.timedelta(minutes=10)
                    next_hit.worker_id = assigned_worker.id
                    db.session.commit()
                    return next_hit
                else:
                    current_taxonomy_query = next_taxonomy_query
            else:
                return None
    return None


def fetch_first_hit(assigned_worker):
    next_query = TaxonomyQuery.query.filter(TaxonomyQuery.status=='open').first()
    if next_query is not None:
        next_hit = Hit.query.filter(Hit.status=='open').filter(Hit.attachment_type == 'taxonomy').filter(Hit.attachment_id == next_query.id).first()
        if next_hit is not None:
            next_hit.status = 'assigned'
            next_hit.deadline = datetime.datetime.now() + datetime.timedelta(minutes=10)
            next_hit.worker_id = assigned_worker.id
            db.session.commit()
            return next_hit
        else:
            return None
    else:
        return None