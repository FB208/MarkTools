from flask import current_app as app
from flask import render_template
from . import article_bp

@article_bp.route('/article')
def rewrite():
    return render_template('rewrite.html')

