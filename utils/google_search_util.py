from googleapiclient.discovery import build
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import json
import os
import chardet
from flask import current_app as app

class GoogleSearchUtil:
    def __init__(self):
        """
        初始化Google搜索工具
        :param api_key: Google API密钥
        :param cx: 搜索引擎ID
        """
        self.api_key = app.config.get('GOOGLE_SEARCH_API_KEY')
        self.cx = app.config.get('GOOGLE_SEARCH_CX')
        self.service = build('customsearch', 'v1', developerKey=self.api_key)

    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        执行Google搜索，只返回HTML页面结果
        :param query: 搜索查询
        :param num_results: 需要返回的结果数量
        :return: 搜索结果列表
        """
        # 只搜索HTML和HTM页面
        modified_query = f"{query} (filetype:html OR filetype:htm OR filetype:php OR filetype:asp OR filetype:aspx OR filetype:jsp)"
        
        try:
            result = self.service.cse().list(
                q=modified_query,
                cx=self.cx,
                num=num_results
            ).execute()
            
            search_results = []
            if 'items' in result:
                for item in result['items']:
                    search_result = {
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    }
                    search_results.append(search_result)
            
            return search_results

        except Exception as e:
            print(f"搜索出错: {str(e)}")
            return []

    def fetch_page_content(self, url: str) -> Dict[str, Any]:
        """
        获取指定URL的网页内容
        :param url: 网页URL
        :return: 包含网页内容的字典
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            # 使用chardet检测编码
            detected_encoding = chardet.detect(response.content)['encoding']
            response.encoding = detected_encoding if detected_encoding else 'utf-8'
            
            # 如果检测的编码仍然导致乱码，尝试其他编码
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
            except Exception:
                # 尝试常见的中文编码
                for encoding in ['gb18030', 'gbk', 'gb2312']:
                    try:
                        response.encoding = encoding
                        soup = BeautifulSoup(response.text, 'html.parser')
                        break
                    except Exception:
                        continue
            
            # 移除script和style元素
            for script in soup(["script", "style"]):
                script.decompose()
                
            # 获取文本内容
            text = soup.get_text(separator='\n', strip=True)
            
            result = {
                'url': url,
                'content': text,
                'status': 'success',
                'encoding': response.encoding
            }

            return result
            
        except Exception as e:
            print(f"获取页面内容失败 {url}: {str(e)}")
            return {
                'url': url,
                'content': '',
                'status': 'error',
                'error': str(e)
            }

    def fetch_article_details(self, url: str):
        return ""
        # try:
        #     loader = WebBaseLoader(url)
        #     documents = loader.load()

        #     # 打印提取的正文内容
        #     for doc in documents:
        #         print("URL:", doc.metadata.get('url', 'N/A'))
        #         print("Title:", doc.metadata.get('title', 'N/A'))
        #         print("Content:", doc.page_content)

        #     # 直接返回 documents 列表
        #     return documents
        # except Exception as e:
        #     print(f"提取内容失败 {url}: {str(e)}")
        #     return None
