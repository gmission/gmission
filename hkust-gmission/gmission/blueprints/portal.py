__author__ = 'CHEN Zhao'

import os.path
from flask import Blueprint, jsonify, request, render_template

portal_blueprint = Blueprint('portal', __name__, template_folder=os.path.join('templates', 'portal'))


@portal_blueprint.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


