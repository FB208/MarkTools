from flask import Blueprint

main_bp = Blueprint('main', __name__)
translate_bp = Blueprint('translate', __name__)

from . import main, translate