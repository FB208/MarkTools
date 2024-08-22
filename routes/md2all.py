from flask import current_app as app
from flask import render_template, request, jsonify
from . import md2all_bp
from werkzeug.wrappers.response import ResponseStream

@md2all_bp.route('/md2all')
def md2all():
    return render_template('md2all.html')

@md2all_bp.route('/saved_resource')
def saved_resource():
    return render_template('saved_resource.html')