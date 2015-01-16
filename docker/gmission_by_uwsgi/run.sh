#!/bin/sh

cd /GMission-Server/services

export C_FORCE_ROOT="true"
celery -A push_msg.task worker >>../logs/celery.log 2>&1 &

cd /GMission-Server/hkust-gmission
python db_util.py  &&  uwsgi --ini /uwsgi.ini
