__author__ = 'CHEN Zhao'
import json_encoder
import log
import sys
import socket
import os.path


def stdout(*lst):
    print '[' + ' '.join(sys.argv) + ']' + ' '.join(map(str, lst))
    sys.stdout.flush()


def config(app, root):
    config_common(app, root)
    # if is_production():
    #     config_production(app)
    # else:
    #     config_developing(app)

    check_dir_config(app)


def is_production():
    stdout('docker now, all is production')
    return True
    # return 'xjimi.com' in socket.gethostname() or 'gmission' in socket.gethostname()


def makedir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def check_dir_config(app):
    for key, value in app.config.items():
        if key.startswith('GMISSION') and key.endswith('DIR'):
            makedir(value)


def config_common(app, root_path):
    app.json_encoder = json_encoder.CustomJSONEncoder

    app.secret_key = 'blabla'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECURITY_TOKEN_AUTHENTICATION_KEY'] = 'UserAuthToken'
    app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'X-Xuewen-User-Auth-Token'

    app.config['GMISSION_IMAGE_UPLOAD_DIR'] = os.path.join(root_path, 'static', 'image', 'original')
    app.config['GMISSION_IMAGE_THUMB_DIR'] = os.path.join(root_path, 'static', 'image', 'thumb')

    app.config['GMISSION_VIDEO_UPLOAD_DIR'] = os.path.join(root_path, 'static', 'video', 'original')
    app.config['GMISSION_VIDEO_THUMB_DIR'] = os.path.join(root_path, 'static', 'video', 'thumb')

    app.config['GMISSION_AUDIO_UPLOAD_DIR'] = os.path.join(root_path, 'static', 'audio', 'original')

    app.config['GMISSION_LOGS_DIR'] = os.path.join(root_path, 'logs')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://csp_team:csp2014hkust@127.0.0.1:3306/gmission_hkust'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://csp_team:csp2014hkust@docker-mysql/gmission_hkust'


    FP_PATH = os.path.join(root_path, 'static', 'fp_collection')
    app.config['APK_PATH'] = os.path.join(FP_PATH, 'app-debug-unaligned.apk')
    app.config['DATA_PATH'] = os.path.join(FP_PATH, 'wherami.zip')
    app.config['WIFIPAD_PATH'] = os.path.join(FP_PATH,'wififorpad.apk')
    app.config['LOCALIZATION_PATH'] = os.path.join(FP_PATH, 'wifilocalization.apk')


    log.set_logger(app)
    app.config.from_object('email')

#
# def config_developing(app):
#     print 'NOT production server'
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://csp_team:csp2014hkust@docker-mysql/gmission_hkust'
#     pass
#
#
# def config_production(app):
#     print 'production server'
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://csp_team:csp2014hkust@docker-mysql/gmission_hkust'
#     pass
