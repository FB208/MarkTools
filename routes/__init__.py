from flask import Blueprint


main_bp = Blueprint('main', __name__)
translate_bp = Blueprint('translate', __name__)
md2all_bp = Blueprint('md2all', __name__)
speech2text_bp = Blueprint('speech2text', __name__)
article_bp = Blueprint('article', __name__)
test_bp = Blueprint('test', __name__)
wechat_bp = Blueprint('wechat', __name__)
starbot_bp = Blueprint('starbot', __name__, url_prefix='/starbot')
scheduler_bp = Blueprint('scheduler', __name__)
life_bp = Blueprint('life', __name__)
word_plugin_bp = Blueprint('word_plugin', __name__)
auth_bp = Blueprint('auth', __name__)
fun_bp = Blueprint('fun', __name__, url_prefix='/fun')
text2speech_bp = Blueprint('text2speech', __name__)
wechat_sub_account_bp = Blueprint('wechat_sub_account', __name__)
lighthouse_bp = Blueprint('lighthouse', __name__, url_prefix='/lh')
html2pic_bp = Blueprint('html2pic', __name__, url_prefix='/html2pic')

from . import main, translate, md2all, speech2text, article, test, wechat, scheduler, life, wechat_sub_account, word_plugin, auth, fun, starbot, text2speech, lighthouse, html2pic   
