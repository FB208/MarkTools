from flask import current_app as app
from flask import render_template, request
from . import test_bp
import docx
from utils.embeddings.embedding_util import EmbeddingSearch

@test_bp.route('/test')
def test():
    return render_template('test.html')

@test_bp.route('/test_post', methods=['POST'])
def test_post():
    data = request.json
    # 初始化 EmbeddingSearch
    es = EmbeddingSearch()
    
    '''
    # 读取 docx 文件
    doc = docx.Document('tempfiles/1.docx')
    full_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

    # 调用 add_long_document 方法
    es.add_long_document(full_text)
    '''
    es.load()
    print(f"索引维度: {es.index.d}")
    print(f"索引中的向量数量: {es.index.ntotal}")
    print(f"文档数量: {len(es.documents)}")
   
    return data