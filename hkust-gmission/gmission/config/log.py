__author__ = 'chenzhao'
import logging
import os.path
import os
from logging.handlers import RotatingFileHandler


def set_logger(app):
    logs_path = app.config['GMISSION_LOGS_DIR']
    if not os.path.exists(logs_path):
        os.mkdir(logs_path)

    set_flask_logger(app, logs_path)
    set_profiling_logger(app, logs_path)

    set_admin_logger(app, logs_path)
    set_push_msg_logger(app, logs_path)


def set_flask_logger(app, logs_path):
    log_file = os.path.join(logs_path, 'GMission.log')
    handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)


def set_profiling_logger(app, logs_path):
    profiling_formatter = logging.Formatter('%(asctime)s %(message)s')

    profiling_log_file = os.path.join(logs_path, 'GMissionProfiling.log')

    profiling_handler = RotatingFileHandler(profiling_log_file, maxBytes=10000000, backupCount=1)
    profiling_handler.setFormatter(profiling_formatter)

    logger = logging.getLogger('GMissionProfiling')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(profiling_handler)

    app.profiling_logger = logger



def set_admin_logger(app, logs_path):
    admin_formatter = logging.Formatter('%(asctime)s %(message)s')
    admin_log_file = os.path.join(logs_path, 'GMissionAdmin.log')
    admin_handler = RotatingFileHandler(admin_log_file, maxBytes=10000000, backupCount=1)
    admin_handler.setFormatter(admin_formatter)
    logger = logging.getLogger('GMissionAdmin')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(admin_handler)
    app.admin_logger = logger



def set_push_msg_logger(app, logs_path):
    profiling_formatter = logging.Formatter('%(asctime)s %(message)s')

    profiling_log_file = os.path.join(logs_path, 'GMissionAsyncJobs.log')

    profiling_handler = RotatingFileHandler(profiling_log_file, maxBytes=10000000, backupCount=1)
    profiling_handler.setFormatter(profiling_formatter)

    logger = logging.getLogger('GMissionAsyncJobs')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(profiling_handler)

    app.push_msg_logger = logger

