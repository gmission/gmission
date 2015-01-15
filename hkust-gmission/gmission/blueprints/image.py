__author__ = 'CHEN Zhao'

import os
import random
from gmission.flask_app import app
from flask import Blueprint,  jsonify, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

from PIL import Image


image_blueprint = Blueprint('image', __name__, template_folder='templates')


ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg', 'gif']
UPLOAD_DIR = app.config['GMISSION_IMAGE_UPLOAD_DIR']
THUMB_DIR = app.config['GMISSION_IMAGE_THUMB_DIR']


def allowed_file(filename):
    return True
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def unique_filename(file_obj):
    rid = random.randint(100000000, 999999999)
    return '%d-%s' % (rid, secure_filename(file_obj.filename))


def gen_image_thumb(original_path, thumb_path):
    thumb_max_size = 250, 250
    im = Image.open(original_path)
    im.thumbnail(thumb_max_size, Image.ANTIALIAS)
    im.save(thumb_path)


@image_blueprint.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = unique_filename(file)
            original_path = os.path.join(UPLOAD_DIR, filename)
            file.save(original_path)
            thumb_path = os.path.join(THUMB_DIR, filename)
            gen_image_thumb(original_path, thumb_path)
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

@image_blueprint.route('/original/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@image_blueprint.route('/thumb/<filename>')
def thumb_file(filename):
    return send_from_directory(THUMB_DIR, filename)
