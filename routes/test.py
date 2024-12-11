from flask import current_app as app
from flask import render_template, request, jsonify
from . import test_bp
import os
import docx
from utils.embeddings.embedding_v2_util import EmbeddingSearchV2 as EmbeddingSearch
from services.test_service import history_chat
from services.google_tuned import list as google_tuned_list
@test_bp.route('/test')
def test():
    return render_template('test.html')

@test_bp.route('/test_post', methods=['POST'])
def test_post():
    data = request.json
    # 初始化 EmbeddingSearch
    es = EmbeddingSearch()
    
    
    # 读取 docx 文件
    for i in range(1, 4):
        doc = docx.Document(os.path.join(app.config['BASE_PATH'], 'tempfiles', f'{i}.docx'))
        full_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

        # 调用 add_long_document 方法
        es.add_long_document(full_text)
    
    print(f"索引维度: {es.index.d}")
    print(f"索引中的向量数量: {es.index.ntotal}")
    print(f"文档数量: {len(es.documents)}")
    
    documents = es.display_all_documents()

    
    data['documents'] = documents
    return data

@test_bp.route('/test/env', methods=['GET'])
def get_env():
    keys = ['LLM_SERVICE']
    env_vars = {key: os.environ.get(key) for key in keys if key in os.environ}
    
    # 以 JSON 格式返回环境变量
    return jsonify(env_vars)

@test_bp.route('/test/history', methods=['GET'])
def test_history():
    return history_chat()


@test_bp.route('/test/google_tuned', methods=['GET'])
def test_google_tuned():
    return google_tuned_list()


@test_bp.route('/test/charts', methods=['GET'])
def test_charts():
    return render_template('charts.html')


@test_bp.route('/v1/license/activate', methods=['POST'])
def test_license_activate():
    data = {"ok":True,"code":2000,"message":"license success"}
    
    return data