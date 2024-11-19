from flask import Blueprint


main_bp = Blueprint('main', __name__)
translate_bp = Blueprint('translate', __name__)
md2all_bp = Blueprint('md2all', __name__)
speech2text_bp = Blueprint('speech2text', __name__)
article_bp = Blueprint('article', __name__)
test_bp = Blueprint('test', __name__)
wechat_bp = Blueprint('wechat', __name__)
scheduler_bp = Blueprint('scheduler', __name__)
life_bp = Blueprint('life', __name__)
word_plugin_bp = Blueprint('word_plugin', __name__)

from . import main, translate, md2all, speech2text, article, test, wechat, scheduler, life, word_plugin 