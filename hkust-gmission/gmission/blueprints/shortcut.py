__author__ = 'CHEN Zhao'

from flask import Blueprint, jsonify, request

shortcut_blueprint = Blueprint('shortcut', __name__, template_folder='templates')
