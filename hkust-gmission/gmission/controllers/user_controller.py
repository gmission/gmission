#!/usr/bin/env python
# encoding: utf-8
from gmission.config import APP_SECRET_KEY
from gmission.controllers.async_jobs_controller import send_reg_email_async

__author__ = 'rui'
from hashids import Hashids

hashids = Hashids(salt=APP_SECRET_KEY, min_length=32)


def generate_user_auth_hashid(id):
    hashid = hashids.encode(id)
    return hashid


def get_id_from_user_auth_hashid(hashid):
    id = hashids.decode(hashid)
    if len(id) == 1:
        return int(id[0])
    else:
        return 0


def send_user_auth_email(user):
    if user is None:
        return
    if user.active:
        return
    send_reg_email_async(user)


if __name__ == '__main__':
    hashid = generate_user_auth_hashid(1)
    print hashid
    print get_id_from_user_auth_hashid(hashid+hashid)