__author__ = 'haidaoxiaofei'

import os
import random
from gmission.flask_app import app
from flask import Blueprint,  jsonify, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from gmission.controllers import d3_controller, async_jobs_controller

d3_blueprint = Blueprint('d3', __name__, template_folder='templates')


D3_MODEL_DIR = app.config['GMISSION_3D_MODEL_DIR']
HTML_DIR = app.config['GMISSION_HTML_DIR']


@d3_blueprint.route('/ply/<hit_id>/<filename>')
def ply_file(hit_id, filename):
    ply_file_dir = os.path.join(D3_MODEL_DIR, hit_id, 'bundle')
    print ply_file_dir
    return send_from_directory(ply_file_dir, filename)


@d3_blueprint.route('/3d_request_direction/<hit_id>')
def request_direction(hit_id):
    print hit_id
    return d3_controller.calculate_next_best_direction(hit_id)


@d3_blueprint.route('/rebuild_3d_sparse_models')
def rebuild_3d_models():
    d3_controller.rebuild_3d_sparse_models()
    return 'good'

@d3_blueprint.route('/view/<hit_id>/<filename>')
def view_ply(hit_id, filename):
    return render_template('plyloadviewer.html',
                           hit_id=hit_id,
                           filename=filename)

@d3_blueprint.route('/email_model/<requester_id>/<hit_id>/<filename>')
def email_link_ply(requester_id, hit_id, filename):
    async_jobs_controller.send_view_ply_email_async(requester_id, hit_id, filename)
    return 'ok'
