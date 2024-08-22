from flask import Blueprint

main_bp = Blueprint('main', __name__)
translate_bp = Blueprint('translate', __name__)
md2all_bp = Blueprint('md2all', __name__)

from . import main, translate, md2all