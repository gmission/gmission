from collections import defaultdict, Counter
from gmission.models import *

__author__ = 'chenzhao'


def log_payment(requester, worker, answer, credit):
    ct = CreditTransaction(credit=credit,
                           requester=requester,
                           worker=worker,
                           answer_id=answer.id,
                           hit_id=answer.hit_id,
                           campaign_id=answer.hit.campaign_id)
    db.session.add(ct)


def has_paid(answer):
    logged = CreditTransaction.query.filter(CreditTransaction.answer_id==answer.id).count()
    return logged > 0


def pay_for_instant_type_hit(answer):
    if answer.hit.payment=="instant":
        pay(answer)


def pay(answer):
    if has_paid(answer):  # double insurance for no duplicate payment
        return False, "paid before"
    credit = answer.hit.credit

    answer.accepted = True
    answer.worker.credit += credit
    answer.hit.requester.credit -= credit
    log_payment(answer.hit.requester, answer.worker, answer, credit)
    db.session.commit()
    return True, credit


def exchange(user, credit, money, channel, action):
    if user.credit + credit < 0:
        print 'exchange failed, user credit<0'
        return False
    user.credit += credit
    ce = CreditExchange(credit=credit, money=money, user_id=user.id, channel=channel, action=action)
    db.session.add(ce)
    db.session.commit()
    return ce


def pay_majority(hit):
    print hit
    print len(hit.answers), 'answers total'
    if len(hit.answers)<hit.required_answer_count:
        return "not enough answers"
    valid_answers = sorted(hit.answers, key=lambda a:a.created_on)[:hit.required_answer_count]  # to prevent sync issues
    print len(valid_answers), 'valid answers'

    correct_ordinal = get_majority_ordinal(hit)
    print 'correct ordinal', correct_ordinal
    correct_answers = filter(lambda a:a.ordinal == correct_ordinal, valid_answers)
    print 'correct answers', correct_answers
    result = map(pay, correct_answers)
    return [{'answer':a.id, 'result':r} for a, r in zip(correct_answers, result)]


def pay_image(task):
    for answer in task.answers:
        pay(task.requester, answer.worker, answer, task.credit)


def get_majority_ordinal(hit):
    if not hit.answers:
        return None
    counter = Counter(a.ordinal for a in hit.answers)
    majority_ordinal, majority_count = counter.most_common(1)[0]
    return majority_ordinal

