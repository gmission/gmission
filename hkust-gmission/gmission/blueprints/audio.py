__author__ = 'CHEN Zhao'

import os
import subprocess
import random
from gmission.flask_app import app
from flask import Blueprint,  jsonify, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename


audio_blueprint = Blueprint('audio', __name__, template_folder='templates')


UPLOAD_DIR = app.config['GMISSION_AUDIO_UPLOAD_DIR']


def allowed_file(filename):
    return True


def unique_filename(file_obj):
    rid = random.randint(100000000, 999999999)
    return '%d-%s' % (rid, secure_filename(file_obj.filename))


@audio_blueprint.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = unique_filename(file)
            original_path = os.path.join(UPLOAD_DIR, filename)
            file.save(original_path)
            return jsonify(filename=filename, size=os.stat(original_path).st_size)

@audio_blueprint.route('/original/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

