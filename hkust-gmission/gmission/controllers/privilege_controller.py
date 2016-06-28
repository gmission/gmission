#!/usr/bin/env python
# encoding: utf-8
from collections import defaultdict

from flask import request

from gmission.flask_app import GMissionError
from gmission.models import get_or_create, Role

__author__ = 'rui'

# admin = get_or_create(Role, name='admin', description='who can do anything')
# user = get_or_create(Role, name='user', description='user')
role_admin = 'admin'
role_user = 'user'
role_everyone = [role_admin, role_user]
role_guest = None  # no need login


def priv(role=[role_guest], pre_callback=None, post_callback=None, skip_with_query=False):
    return Privilege(role, pre_callback, post_callback, skip_with_query)


priv_table = defaultdict(priv)
priv_table_inited = False


class Privilege(object):
    def __init__(self, allow_roles=[], pre_callback=None, post_callback=None, skip_with_query=False):
        self.allow_roles = allow_roles
        self.pre_callback = pre_callback
        self.post_callback = post_callback
        self.skip_with_query = skip_with_query

    def is_deny_all(self):
        return self.allow_roles == [] and self.pre_callback is None

    def check(self, user):
        role_pass = True
        if len(self.allow_roles) > 0:
            if role_everyone == self.allow_roles:
                role_pass = True
            else:
                role_pass = False
                for role in self.allow_roles:
                    roleobj = get_or_create(Role, name=role)
                    if roleobj in user.roles:
                        role_pass = True
                        break
        if request.query_string and request.method == 'GET' and self.skip_with_query:
            role_pass = True

        if not role_pass:
            raise GMissionError('Invalid JWT', 'User don\'t have privilege', 401)

        if self.pre_callback is not None:
            return self.pre_callback(user)


def push_priv_rule(rule, method, priv):
    if type(method) == str:
        priv_table[(rule, method)] = priv
    if type(method) == list:
        for m in method:
            priv_table[(rule, m)] = priv


def init_priv_table():
    global priv_table_inited
    if not priv_table_inited:
        push_priv_rule('/audio/upload', ['GET', 'POST'], priv(role=role_everyone))
        push_priv_rule('/image/upload', ['GET', 'POST'], priv(role=role_everyone))
        push_priv_rule('/video/upload', ['GET', 'POST'], priv(role=role_everyone))
        #
        push_priv_rule('/rest/answer', ['GET'], priv(role=[role_admin], skip_with_query=True))
        push_priv_rule('/rest/answer', ['POST', 'PUT', 'PATCH', 'DELETE'], priv(role=role_everyone))
        push_priv_rule('/rest/answer/<instid>', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], priv(role=role_everyone))

        push_priv_rule('/rest/attachment', ['GET'], priv(role=[role_admin], skip_with_query=True))
        push_priv_rule('/rest/attachment', ['POST', 'PUT', 'DELETE'], priv(role=role_everyone))
        push_priv_rule('/rest/attachment/<instid>', ['GET','POST', 'PUT', 'DELETE'], priv(role=role_everyone))

        push_priv_rule('/rest/campaign', ['GET', 'POST', 'PUT', 'DELETE'], priv(role=role_everyone))
        push_priv_rule('/rest/campaign/<instid>', ['GET', 'POST', 'PUT', 'DELETE'], priv(role=role_everyone))

        push_priv_rule('/rest/campaign_role', ['GET'], priv(role=[role_admin], skip_with_query=True))
        push_priv_rule('/rest/campaign_role', ['POST', 'PUT', 'DELETE'], priv(role=role_everyone))
        push_priv_rule('/rest/campaign_role/<instid>', ['GET','POST', 'PUT', 'DELETE'], priv(role=role_everyone))

        push_priv_rule('/rest/campaign_user', ['GET'], priv(role=[role_admin], skip_with_query=True))
        push_priv_rule('/rest/campaign_user', ['POST', 'PUT', 'DELETE'], priv(role=role_everyone))
        push_priv_rule('/rest/campaign_user/<instid>', ['GET','POST', 'PUT', 'DELETE'], priv(role=role_everyone))

        push_priv_rule('/rest/coordinate', ['GET'], priv(role=[role_admin]))
        push_priv_rule('/rest/coordinate', ['POST', 'PUT', 'DELETE'], priv(role=role_everyone))
        push_priv_rule('/rest/coordinate/<instid>', ['GET','POST', 'PUT', 'DELETE'], priv(role=role_everyone))

        push_priv_rule('/rest/credit_transaction', ['GET', 'POST', 'PUT', 'DELETE'], priv(role=[role_admin]))
        push_priv_rule('/rest/credit_transaction/<instid>', ['GET','POST', 'PUT', 'DELETE'], priv(role=[role_admin]))

        push_priv_rule('/rest/hit', ['GET', 'POST', 'PUT', 'DELETE'], priv(role=role_everyone))
        push_priv_rule('/rest/hit/<instid>', ['GET', 'POST', 'PUT', 'DELETE'], priv(role=role_everyone))

        push_priv_rule('/rest/location', ['GET', 'POST', 'PUT', 'DELETE'], priv(role=role_everyone))
        push_priv_rule('/rest/location/<instid>', ['GET', 'POST', 'PUT', 'DELETE'], priv(role=role_everyone))

        push_priv_rule('/rest/position_trace', ['GET'], priv(role=[role_admin]))
        push_priv_rule('/rest/position_trace', ['POST', 'PUT', 'DELETE'], priv(role=role_everyone))
        push_priv_rule('/rest/position_trace/<instid>', ['GET','POST', 'PUT', 'DELETE'], priv(role=[role_admin]))

        push_priv_rule('/rest/role', ['GET', 'POST', 'PUT', 'DELETE'], priv(role=[role_admin]))
        push_priv_rule('/rest/role/<instid>', ['GET','POST', 'PUT', 'DELETE'], priv(role=[role_admin]))

        push_priv_rule('/rest/user', ['GET', 'POST', 'PUT', 'DELETE'], priv(role=[role_admin]))
        push_priv_rule('/rest/user/<instid>', ['GET','POST', 'PUT', 'DELETE'], priv(role=role_everyone))

        push_priv_rule('/rest/user_last_position', ['GET', 'POST', 'PUT', 'DELETE'], priv(role=[role_admin]))
        push_priv_rule('/rest/user_last_position/<instid>', ['GET','POST', 'PUT', 'DELETE'], priv(role=[role_admin]))

        push_priv_rule('/rest/baidu_push_info', ['GET'], priv(role=[role_admin], skip_with_query=True))
        push_priv_rule('/rest/baidu_push_info', ['POST', 'PUT', 'DELETE'], priv(role=role_everyone))
        push_priv_rule('/rest/baidu_push_info/<instid>', ['GET', 'POST', 'PUT', 'DELETE'], priv(role=role_everyone))

        push_priv_rule('/rest/message', ['GET'], priv(role=[role_admin], skip_with_query=True))
        push_priv_rule('/rest/message', ['POST', 'PUT', 'DELETE'], priv(role=[role_admin]))
        push_priv_rule('/rest/message/<instid>', ['GET','POST', 'PUT', 'DELETE'], priv(role=role_everyone))

        push_priv_rule('/rest/selection', ['GET', 'POST', 'PUT', 'DELETE'], priv(role=role_everyone))
        push_priv_rule('/rest/selection/<instid>', ['GET', 'POST', 'PUT', 'DELETE'], priv(role=role_everyone))

        push_priv_rule('/user/credit/campaign/<campaign_id>', ['GET'], priv(role=role_everyone))
        push_priv_rule('/user/answered-campaigns', ['GET'], priv(role=role_everyone))
        push_priv_rule('/user/answered-hits', ['GET'], priv(role=role_everyone))

        priv_table_inited = True
