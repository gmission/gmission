__author__ = 'CHEN Zhao'

import os
import subprocess
import random
from gmission.flask_app import app
from flask import Blueprint,  jsonify, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename


video_blueprint = Blueprint('video', __name__, template_folder='templates')


UPLOAD_DIR = app.config['GMISSION_VIDEO_UPLOAD_DIR']
THUMB_DIR = app.config['GMISSION_VIDEO_THUMB_DIR']


def allowed_file(filename):
    return True


def unique_filename(file_obj):
    rid = random.randint(100000000, 999999999)
    return '%d-%s' % (rid, secure_filename(file_obj.filename))


def gen_video_thumb(original_path, thumb_path):
    cmd = 'ffmpeg -i %s -vframes 1 -f image2 %s' % (original_path, thumb_path)
    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print 'something wrong when generate video thumb', cmd, e

    pass

@video_blueprint.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = unique_filename(file)
            original_path = os.path.join(UPLOAD_DIR, filename)
            file.save(original_path)
            thumb_path = os.path.join(THUMB_DIR, filename+'.png')
            gen_video_thumb(original_path, thumb_path)
            return jsonify(filename=filename, size=os.stat(original_path).st_size)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@video_blueprint.route('/original/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@video_blueprint.route('/thumb/<filename>')
def thumb_file(filename):
    return send_from_directory(THUMB_DIR, filename)
