import pytest
import os, json
from app import create_app
from test_config import TestConfig
from utils.google_search_util import GoogleSearchUtil

# 创建Flask应用
app = create_app()
app.config.from_object(TestConfig)

# pytest -s tests/utils/google_search_util_test.py::test_search
def test_search():
    with app.app_context():
        api_key = app.config.get('GOOGLE_SEARCH_API_KEY')
        cx = app.config.get('GOOGLE_SEARCH_CX')
        
        assert api_key, "缺少 GOOGLE_SEARCH_API_KEY 配置"
        assert cx, "缺少 GOOGLE_SEARCH_CX 配置"
        
        search_util = GoogleSearchUtil(api_key, cx)
        results = search_util.search("三国演义")
        
        # 保存搜索结果
        output_path = os.path.join('tempfiles', 'google_search_results.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"搜索结果已保存到: {output_path}")
        assert results, "搜索结果不应为空"

# pytest -s tests/utils/google_search_util_test.py::test_fetch_page_content
def test_fetch_page_content():
    with app.app_context():
        api_key = app.config.get('GOOGLE_SEARCH_API_KEY')
        cx = app.config.get('GOOGLE_SEARCH_CX')
        
        search_util = GoogleSearchUtil(api_key, cx)
        
        # 测试获取单个页面内容
        url = "https://baike.baidu.com/item/%E4%B8%89%E5%9B%BD%E6%BC%94%E4%B9%89/5782"
        result = search_util.fetch_page_content(url)
        
        # 将内容保存为txt文件
        output_path = os.path.join('tempfiles', 'page_content.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['content'])
            
        # 同时保存完整结果为JSON（包含状态等信息）
        json_path = os.path.join('tempfiles', 'page_content_full.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print(f"页面内容已保存到: {output_path}")
        print(f"完整结果已保存到: {json_path}")
        
        # 验证结果
        assert result['url'] == url
        assert 'content' in result
        assert 'status' in result

# pytest -s tests/utils/google_search_util_test.py::test_fetch_main_content
def test_fetch_main_content():
    with app.app_context():
        api_key = app.config.get('GOOGLE_SEARCH_API_KEY')
        cx = app.config.get('GOOGLE_SEARCH_CX')
        
        search_util = GoogleSearchUtil(api_key, cx)
        url = "https://baike.baidu.com/item/%E4%B8%89%E5%9B%BD%E6%BC%94%E4%B9%89/5782"
        documents = search_util.fetch_article_details(url)

        # 定义输出文件路径
        output_path = os.path.join('tempfiles', 'article_details.json')

        # 将 documents 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            # 将每个 Document 对象转换为字典并写入文件
            document_details = [
                {
                    "url": doc.metadata.get('url', 'N/A'),
                    "title": doc.metadata.get('title', 'N/A'),
                    "content": doc.page_content
                }
                for doc in documents
            ]
            json.dump(document_details, f, ensure_ascii=False, indent=2)

        print(f"文档内容已保存到: {output_path}")


