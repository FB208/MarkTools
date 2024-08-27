from flask import Blueprint

main_bp = Blueprint('main', __name__)
translate_bp = Blueprint('translate', __name__)
md2all_bp = Blueprint('md2all', __name__)
speech2text_bp = Blueprint('speech2text', __name__)
article_bp = Blueprint('article', __name__)

from . import main, translate, md2all, speech2text, article