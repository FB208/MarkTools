import os
import numpy as np
import faiss
import google.generativeai as genai
import pickle
from typing import List, Tuple, Optional
from flask import current_app as app
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

class EmbeddingSearchV2:
    def __init__(self, 
                 index_path='static/embedding/faiss',
                 docs_path='static/embedding/documents.pkl'):
        # 初始化 Google AI
        api_key = app.config['SIMPLE_GOOGLE_API_KEY']
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/text-embedding-004')
        
        # 创建存储目录
        os.makedirs(index_path, exist_ok=True)
        self.index_path = os.path.join(index_path, 'index.faiss')
        self.docs_path = docs_path
        
        # 加载或创建索引
        self.documents = self._load_documents()
        self.index = self._load_or_create_index()
        
        print(f"当前文档数量: {len(self.documents)}")

    def _get_embedding(self, text: str) -> np.ndarray:
        """获取文本的向量嵌入"""
        try:
            embedding = self.model.embed_content_info(
                content=text,
                task_type="retrieval_document",
            )
            return np.array(embedding.embeddings[0]).astype('float32')
        except Exception as e:
            print(f"获取嵌入向量失败: {e}")
            return None

    def _load_or_create_index(self) -> faiss.Index:
        """加载或创建FAISS索引"""
        dimension = 768  # text-embedding-004 的向量维度
        
        if os.path.exists(self.index_path):
            print("加载现有索引...")
            return faiss.read_index(self.index_path)
        
        print("创建新索引...")
        index = faiss.IndexFlatL2(dimension)  # 使用L2距离度量
        
        # 如果有现有文档，添加到索引中
        if self.documents:
            embeddings = []
            for doc in self.documents:
                embedding = self._get_embedding(doc)
                if embedding is not None:
                    embeddings.append(embedding)
            
            if embeddings:
                embeddings_array = np.array(embeddings)
                index.add(embeddings_array)
                
        return index

    def _load_documents(self) -> List[str]:
        """加载保存的文档"""
        if os.path.exists(self.docs_path):
            with open(self.docs_path, 'rb') as f:
                return pickle.load(f)
        return []

    def _save_documents(self):
        """保存文档列表"""
        with open(self.docs_path, 'wb') as f:
            pickle.dump(self.documents, f)

    def _save_index(self):
        """保存FAISS索引"""
        faiss.write_index(self.index, self.index_path)

    def add_documents(self, documents: List[str]):
        """添加新文档到索引"""
        if not documents:
            print("没有文档需要添加")
            return
        
        print(f"\n=== 开始添加文档 ===")
        print(f"准备添加文档数量: {len(documents)}")
        
        new_embeddings = []
        new_documents = []
        
        for doc in documents:
            # 检查重复
            if doc in self.documents:
                print("文档已存在，跳过")
                continue
                
            embedding = self._get_embedding(doc)
            if embedding is not None:
                new_embeddings.append(embedding)
                new_documents.append(doc)
                self.documents.append(doc)
        
        if new_embeddings:
            embeddings_array = np.array(new_embeddings)
            self.index.add(embeddings_array)
            self._save_documents()
            self._save_index()
            
            print(f"成功添加新文档: {len(new_documents)}")
            print(f"当前文档总数: {len(self.documents)}")
        else:
            print("没有新文档被添加")

    def add_long_document(self, document: str, max_tokens: int = 1024):
        """处理长文档"""
        num_tokens = self.num_tokens_in_string(document)
        chunk_size = self.calculate_chunk_size(num_tokens, max_tokens)
        
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name="gpt-3.5-turbo",
            chunk_size=chunk_size,
            chunk_overlap=0,
        )
        chunks = splitter.split_text(document)
        self.add_documents(chunks)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[float, str]]:
        """搜索相似文档"""
        print(f"\n=== 开始搜索 ===")
        print(f"查询文本: {query}")
        
        # 获取查询的向量表示
        query_vector = self._get_embedding(query)
        if query_vector is None:
            print("无法获取查询向量")
            return []
        
        # 搜索最相似的文档
        distances, indices = self.index.search(
            np.array([query_vector]), 
            min(top_k, len(self.documents))
        )
        
        # 准备结果
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0 and idx < len(self.documents):  # 确保索引有效
                doc = self.documents[idx]
                
                # 计算关键词匹配
                query_terms = query.lower().split()
                doc_lower = doc.lower()
                matches = [term for term in query_terms if term in doc_lower]
                match_score = len(matches) / len(query_terms) if query_terms else 0
                
                # 归一化距离分数（转换为相似度）
                similarity = 1 / (1 + dist)
                
                # 组合分数
                final_score = similarity * 0.7 + match_score * 0.3
                
                results.append((dist, doc, similarity, match_score, final_score))
        
        # 按最终分数排序
        results.sort(key=lambda x: x[4], reverse=True)
        
        # 打印详细结果
        print("\n搜索结果:")
        for i, (dist, doc, sim, match, final) in enumerate(results):
            print(f"\n结果 {i+1}:")
            print(f"原始距离: {dist:.4f}")
            print(f"相似度分数: {sim:.4f}")
            print(f"关键词匹配: {match:.4f}")
            print(f"最终分数: {final:.4f}")
            print(f"文档片段: {doc[:200]}...")
        
        return [(r[0], r[1]) for r in results]  # 返回 (distance, document) 对

    def calculate_chunk_size(self, token_count: int, token_limit: int) -> int:
        if token_count <= token_limit:
            return token_count
        num_chunks = (token_count + token_limit - 1) // token_limit
        chunk_size = token_count // num_chunks
        remaining_tokens = token_count % token_limit
        if remaining_tokens > 0:
            chunk_size += remaining_tokens // num_chunks
        return chunk_size

    def num_tokens_in_string(self, 
        input_str: str, 
        encoding_name: str = "cl100k_base"
    ) -> int:
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(input_str))