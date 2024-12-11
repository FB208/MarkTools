# import pytest
# import docx
# from utils.embeddings.embedding_v2_util import EmbeddingSearch

# # pytest tests/utils/embedding_utils_test.py::test_add_long_document
# def test_add_long_document():
#     # 初始化 EmbeddingSearch
#     es = EmbeddingSearch()
    
#     # 读取 docx 文件
#     doc = docx.Document('tempfiles/1.docx')
#     full_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    
#     # 调用 add_long_document 方法
#     es.add_long_document(full_text)
    
#     # 验证文档是否被成功添加
#     assert len(es.documents) > 0
#     assert es.index is not None
    

# # pytest tests/utils/embedding_utils_test.py::test_search_existing_index
# def test_search_existing_index():
#     # 初始化 EmbeddingSearch
#     es = EmbeddingSearch()
    
#     # 加载现有索引
#     es.load()
    
#     # 检查索引和文档是否存在
#     assert es.index is not None, "索引未成功加载"
#     assert len(es.documents) > 0, "文档列表为空"
    
#     print(f"索引维度: {es.index.d}")
#     print(f"索引中的向量数量: {es.index.ntotal}")
#     print(f"文档数量: {len(es.documents)}")
    
#     # 搜索关键词
#     query = "人工智能"
#     results = es.search(query, top_k=3)
    
#     # 验证搜索结果
#     assert len(results) > 0, "搜索结果不应为空"
    
#     print("搜索结果:")
#     for distance, document in results:
#         print(f"距离: {distance}, 文档: {document}")
    
#     # 验证搜索结果的相关性
#     for _, document in results:
#         assert "人工智能" in document or "AI" in document, "搜索结果应该包含'人工智能'或'AI'"
        
# # pytest tests/utils/embedding_utils_test.py::test_display_all_documents
# def test_display_all_documents():
#     # 初始化 EmbeddingSearch
#     es = EmbeddingSearch()
    
#     # 加载现有索引
#     es.load()
    
#     # 显示所有文档
#     documents = es.display_all_documents()
#     for i, doc in enumerate(documents):
#         print(f"文档 {i+1}: {doc}")