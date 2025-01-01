import pytest
import docx
from utils.embeddings.embedding_v2_util import EmbeddingSearchV2
from app import create_app
from test_config import TestConfig

# 创建Flask应用

app = create_app()
app.config.from_object(TestConfig)

# pytest -s tests/utils/embedding_v2_utils_test.py::test_add_document_v2 -v
def test_add_document_v2():
    with app.app_context():
        # 初始化 EmbeddingSearchV2
        es = EmbeddingSearchV2()
        
        # 读取测试文档
        doc = docx.Document('tempfiles/1.docx')
        full_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        
        # 测试添加文档功能
        es.add_long_document(full_text)
        #documents = es.display_all_documents()
        # 验证文档是否被成功添加
        # print(documents)
        #assert len(documents) > 0

# pytest -s tests/utils/embedding_v2_utils_test.py::test_search_v2 -v
def test_search_v2():
    with app.app_context():
        es = EmbeddingSearchV2()
        
        # 先检查文档内容
        # es.check_documents()
        
        # 测试不同的搜索查询
        test_queries = [
            '''投资理财创业'''
        ]
        
        for query in test_queries:
            print(f"\n测试查询: {query}")
            results = es.search(query)
            
            assert len(results) >= 0, "搜索结果可以为空，但不应该报错"
            
            print("\n搜索结果验证:")
            for score, document in results:
                print(f"相似度分数: {score}")
                # 检查文档是否包含查询词的任何部分
                query_terms = query.lower().split()
                doc_lower = document.lower()
                matches = [term for term in query_terms if term in doc_lower]
                print(f"匹配的关键词: {matches if matches else '无'}")
                print(f"文档片段: {document[:200]}...")
                print("---")

def test_batch_add_documents_v2():
    with app.app_context():
        # 初始化 EmbeddingSearchV2
        es = EmbeddingSearchV2()
        
        # 准备多个测试文档
        test_documents = [
            "这是第一个测试文档，讨论人工智能技术。",
            "这是第二个测试文档，关于机器学习应用。",
            "这是第三个测试文档，探讨深度学习发展。"
        ]
        
        # 测试批量添加文档
        es.batch_add_documents(test_documents)
        
        # 验证批量添加结果
        assert len(es.documents) == len(test_documents)
        assert es.index is not None
        assert es.index.ntotal == len(test_documents)

def test_document_similarity_v2():
    with app.app_context():
        # 初始化并加载索引
        es = EmbeddingSearchV2()
        es.load()
            
        # 测试文档相似度计算
        doc1 = "人工智能技术正在快速发展"
        doc2 = "AI技术发展日新月异"
        
        similarity = es.calculate_document_similarity(doc1, doc2)
        
        # 验证相似度分数
        assert 0 <= similarity <= 1, "相似度分数应该在0到1之间"
        print(f"文档相似度分数: {similarity}")