from collections import defaultdict
from gmission.models import *

__author__ = 'chenzhao'


def log_payment(requester, worker, answer, credit):
    ct = CreditTransaction(credit=credit,
                           requester=requester,
                           worker=worker,
                           answer_id=answer.id)
    db.session.add(ct)


def has_paid(requester, worker, answer):
    logged = CreditTransaction.query.filter(CreditTransaction.answer_id==answer.id).count()
    return logged > 0


def pay(requester, worker, answer, credit):
    if has_paid(requester, worker, answer):
        return
    worker.credit += credit
    requester.credit -= credit
    log_payment(requester, worker, answer, credit)
    db.session.commit()


def pay_image(task):
    for answer in task.answers:
        pay(task.requester, answer.worker, answer, task.credit)


def get_majority_option(request):
    if not request.answers:
        return None
    option_counter = defaultdict(int)
    for answer in request.answers:
        option_counter[answer.option] += 1
    return max(option_counter.items(), key=lambda i:i[1])[0]


def pay_choice(task):
    credit = task.credit
    majority_option = get_majority_option(task)
    good_answers = filter(lambda a:a.option==majority_option, task.answers) # \!/ not necessary
    for answer in sorted(good_answers, key=lambda a:a.created_on)[:task.required_answer_count]:  # should be updated on
        pay(task.requester, answer.worker, answer, credit)


