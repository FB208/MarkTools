import os
import google.generativeai as genai
from chromadb import Client, Settings
import chromadb.utils.embedding_functions as embedding_functions
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from flask import current_app as app

'''
google-generativeai的models/text-embedding-004模型
+chroma向量存储库实现
更加轻量
'''

class DebugGoogleGenerativeAiEmbeddingFunction(embedding_functions.GoogleGenerativeAiEmbeddingFunction):
    def __call__(self, texts):
        print(f"\n=== Google Embedding API 调用 ===")
        print(f"输入文本数量: {len(texts)}")
        print(f"第一个文本示例: {texts[0][:100]}..." if texts else "无文本")
        
        result = super().__call__(texts)
        
        if result:
            print(f"返回向量数量: {len(result)}")
            print(f"每个向量维度: {len(result[0]) if result and len(result) > 0 else 'None'}")
        print("================================\n")
        return result

class EmbeddingSearchV2:
    def __init__(self, 
                 collection_name="default_collection",
                 storage_dir='static/embedding'):
        # 初始化 Google AI
        api_key = app.config['SIMPLE_GOOGLE_API_KEY']
        genai.configure(api_key=api_key)
        
        # 初始化 Chroma
        self.storage_dir = storage_dir
        self.client = Client(Settings(
            persist_directory=storage_dir,
            is_persistent=True
        ))
        
        # 使用调试版本的 embedding 函数
        self.embedding_function = DebugGoogleGenerativeAiEmbeddingFunction(
            api_key=api_key,
            model_name="models/text-embedding-004"
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
        
        print(f"当前集合中的文档数量: {self.collection.count()}")

    def add_documents(self, documents):
        if not documents:
            print("没有文档需要添加")
            return
        
        print("\n=== 开始文档添加过程 ===")
        # 确保 documents 是列表
        if isinstance(documents, str):
            documents = [documents]
            
        print(f"准备添加文档数量: {len(documents)}")
        
        # 为新文档生成嵌入向量并检查重复
        new_documents = []
        new_ids = []
        start_id = self.collection.count()
        
        for i, doc in enumerate(documents):
            print(f"\n检查文档 {i+1}:")
            print(f"文档内容: {doc[:100]}..." if len(doc) > 100 else doc)
            
            results = self.collection.query(
                query_texts=[doc],
                n_results=1
            )
            
            # 如果集合为空，distances 不会在结果中
            distances = results.get('distances', [[1.0]])[0]
            
            # 如果距离大于阈值，认为是新文档
            if not distances or distances[0] > 0.02:  # 设置一个较小的阈值
                new_documents.append(doc)
                new_ids.append(f"doc_{start_id + len(new_documents) - 1}")
        
        if new_documents:
            # 添加新文档到 Chroma
            self.collection.add(
                documents=new_documents,
                ids=new_ids
            )
            print(f"实际添加新文档数量: {len(new_documents)}")
            print(f"当前文档总数: {self.collection.count()}")
        else:
            print("所有文档都是重复的，没有新文档添加。")

    def add_long_document(self, document, max_tokens=1024):
        num_tokens_in_text = self.num_tokens_in_string(document)
        token_size = self.calculate_chunk_size(
            token_count=num_tokens_in_text, token_limit=max_tokens
        )
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name="gpt-3.5-turbo",
            chunk_size=token_size,
            chunk_overlap=0,
        )
        source_text_chunks = text_splitter.split_text(document)
        self.add_documents(source_text_chunks)

    def search(self, query, top_k=5, threshold=0.3):
        print(f"\n=== 开始搜索 ===")
        print(f"查询文本: {query}")
        
        # 获取所有文档
        all_docs = self.collection.get()
        total_docs = len(all_docs.get('documents', []))
        
        results = self.collection.query(
            query_texts=[query],
            n_results=5,
            include=['documents', 'distances', 'metadatas']
        )
        
        print("\n原始搜索结果:")
        print(f"Raw results: {results}")
        
        documents = results['documents'][0]
        distances = results['distances'][0] if 'distances' in results else [0] * len(documents)
        
        # 创建包含更多信息的结果列表
        search_results = []
        for dist, doc in zip(distances, documents):
            # 计算文档与查询词的相关性分数
            relevance_score = 0
            query_terms = query.lower().split()
            doc_lower = doc.lower()
            
            # 1. 基于关键词匹配计算相关性 (0-1分)
            for term in query_terms:
                if term in doc_lower:
                    relevance_score += 1
            if query_terms:
                relevance_score = relevance_score / len(query_terms)
            
            # 2. 向量相似度分数 (0-1分，1最相似)
            vector_score = 1 - dist
            
            # 3. 组合两个分数 (0-1分，1最相关)
            final_score = (vector_score * 0.7 + relevance_score * 0.3)
            
            search_results.append({
                'distance': dist,
                'document': doc,
                'relevance_score': relevance_score,
                'vector_score': vector_score,
                'final_score': final_score
            })
        
        # 按最终分数排序（分数越高越相关）
        search_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        print("\n处理后的结果:")
        for i, result in enumerate(search_results[:top_k]):
            print(f"结果 {i+1}:")
            print(f"原始距离: {result['distance']} (越小越相似)")
            print(f"向量相似度: {result['vector_score']:.3f} (越大越相似)")
            print(f"关键词匹配分数: {result['relevance_score']:.3f} (越大越相似)")
            print(f"最终相关度: {result['final_score']:.3f} (越大越相关)")
            print(f"文档: {result['document'][:200]}...")
            print("---")
        
        # 返回最相关的结果
        filtered_results = [
            (result['distance'], result['document'])
            for result in search_results[:top_k]
            if result['final_score'] > threshold
        ]
        
        return filtered_results

    def display_all_documents(self):
        if self.collection.count() == 0:
            return []
        
        results = self.collection.get()
        return results['documents']

    def calculate_chunk_size(self, token_count: int, token_limit: int) -> int:
        """
        根据令牌计数和令牌限制计算块大小。
        """
        if token_count <= token_limit:
            return token_count

        num_chunks = (token_count + token_limit - 1) // token_limit
        chunk_size = token_count // num_chunks

        remaining_tokens = token_count % token_limit
        if remaining_tokens > 0:
            chunk_size += remaining_tokens // num_chunks

        return chunk_size

    def num_tokens_in_string(self,
        input_str: str, encoding_name: str = "cl100k_base"
    ) -> int:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(input_str))
        return num_tokens

    def check_documents(self):
        """检查所有文档内容"""
        print("\n=== 检查所有文档 ===")
        # 清除可能的缓存
        self.collection = self.client.get_collection(
            name=self.collection.name,
            embedding_function=self.embedding_function
        )
        
        all_docs = self.collection.get()
        for i, doc in enumerate(all_docs['documents']):
            print(f"\n文档 {i+1}:")
            print(f"内容: {doc[:200]}...")  # 只打印前200个字符
            if "赌博" in doc or "资金" in doc:
                print("*** 包含目标关键词 ***")
        print("=== 检查结束 ===\n")

# 使用示例
if __name__ == "__main__":
    api_key = "your-google-api-key"
    es = EmbeddingSearchV2(api_key=api_key)
    
    # 添加文档
    documents = [
        "这是第一个文档的内容",
        "第二个文档讲述了不同的内容",
        "第三个文档与第一个有些相似",
        "这是完全不相关的第四个文档"
    ]
    es.add_documents(documents)
    
    # 搜索相似内容
    query = "相似的文档"
    results = es.search(query)
    
    for distance, document in results:
        print(f"距离: {distance}, 文档: {document}")