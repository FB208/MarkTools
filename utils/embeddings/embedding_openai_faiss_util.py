import os
import faiss
import numpy as np
from typing import List, Dict, Any, Optional
from openai import OpenAI
import pickle
import tiktoken
from datetime import datetime

class OpenAIFaissUtil:
    @staticmethod
    def get_embedding_dimension(client: Optional[OpenAI] = None) -> int:
        """
        获取embedding模型输出的向量维度
        
        Args:
            client: OpenAI客户端实例，如果不提供则创建新的
            
        Returns:
            int: 向量维度
        """
        temp_client = client if client is not None else OpenAI()
        response = temp_client.embeddings.create(
            input="测试文本",
            model="text-embedding-3-small"
        )
        return len(response.data[0].embedding)
    
    def __init__(self, index_file_path: str = "static/embedding/faiss_index", client: Optional[OpenAI] = None):
        """
        初始化OpenAI和FAISS工具类
        
        Args:
            index_file_path: FAISS索引文件保存路径（不需要包含扩展名）
            client: OpenAI客户端实例，如果不提供则创建新的
        """
        self.index_dir = os.path.dirname(index_file_path)
        self.index_name = os.path.basename(index_file_path)
        os.makedirs(self.index_dir, exist_ok=True)  # 确保目录存在
        
        self.client = client if client is not None else OpenAI()
        self.index = None
        self.texts = []  # 存储原始文本
        self.text_set = set()  # 用于快速查找文本是否存在
        self.encoding = tiktoken.get_encoding("cl100k_base")  # OpenAI的默认编码器
        self.dimension = 1536 #self.get_embedding_dimension(self.client)  # 获取向量维度
        self.load_or_create_index()
        
    def load_or_create_index(self):
        """加载或创建FAISS索引"""
        index_file = os.path.join(self.index_dir, f"{self.index_name}.index")
        meta_file = os.path.join(self.index_dir, f"{self.index_name}.meta")
        
        if os.path.exists(index_file) and os.path.exists(meta_file):
            # 加载FAISS索引
            self.index = faiss.read_index(index_file)
            
            # 加载元数据（文本内容）
            with open(meta_file, 'rb') as f:
                meta_data = pickle.load(f)
                self.texts = meta_data['texts']
                self.text_set = set(self.texts)
        else:
            # 创建一个新的FAISS索引，使用欧几里得距离（L2）
            self.index = faiss.IndexFlatL2(self.dimension)  # 使用动态获取的维度
            self.text_set = set()
    
    def save_index(self):
        """保存FAISS索引到文件"""
        # 保存FAISS索引
        index_file = os.path.join(self.index_dir, f"{self.index_name}.index")
        faiss.write_index(self.index, index_file)
        
        # 保存元数据（文本内容）
        meta_file = os.path.join(self.index_dir, f"{self.index_name}.meta")
        with open(meta_file, 'wb') as f:
            meta_data = {
                'texts': self.texts,
                'created_at': datetime.now().isoformat()
            }
            pickle.dump(meta_data, f)
    
    def get_embedding(self, text: str) -> List[float]:
        """
        获取文本的embedding向量
        
        Args:
            text: 输入文本
            
        Returns:
            embedding向量
        """
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    
    def add_texts(self, texts: List[str]) -> Dict[str, Any]:
        """
        添加多个文本到向量数据库，自动去重
        
        Args:
            texts: 文本列表
            
        Returns:
            Dict[str, Any]: 包含添加信息的字典
                - added_texts: 实际添加的文本列表
                - added_count: 新添加的文本数量
                - total_count: 添加后数据库中的总文本数量
                - skipped_count: 因重复而跳过的文本数量
        """
        # 过滤掉已存在的文本
        new_texts = [text for text in texts if text not in self.text_set]
        skipped_count = len(texts) - len(new_texts)
        
        if not new_texts:
            return {
                "added_texts": [],
                "added_count": 0,
                "total_count": len(self.texts),
                "skipped_count": skipped_count
            }
            
        embeddings = []
        for text in new_texts:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
            
        embeddings_array = np.array(embeddings).astype('float32')
        self.index.add(embeddings_array)
        self.texts.extend(new_texts)
        self.text_set.update(new_texts)  # 更新文本集合
        self.save_index()
        
        return {
            "added_texts": new_texts,
            "added_count": len(new_texts),
            "total_count": len(self.texts),
            "skipped_count": skipped_count
        }
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索相似文本
        
        Args:
            query: 查询文本
            top_k: 返回最相似的结果数量
            
        Returns:
            包含相似度得分和原始文本的结果列表
        """
        if len(self.texts) == 0:
            return []
            
        query_embedding = self.get_embedding(query)
        query_embedding_array = np.array([query_embedding]).astype('float32')
        
        # 执行搜索
        distances, indices = self.index.search(query_embedding_array, min(top_k, len(self.texts)))
        
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.texts):  # 确保索引有效
                results.append({
                    'text': self.texts[idx],
                    'score': float(dist),  # 转换numpy float32为Python float
                    'rank': i + 1
                })
                
        return results
    
    def split_text(self, text: str, chunk_tokens: int = 1000) -> List[str]:
        """
        将长文本按句子和token数量智能分段
        
        Args:
            text: 长文本内容
            chunk_tokens: 每段文本的最大token数量，默认1000
            
        Returns:
            List[str]: 分段后的文本列表
        """
        # 清理文本，去除多余的空白字符
        text = ' '.join(text.split())
        
        # 使用句号、问号、感叹号等作为分割点，分割成句子
        sentence_delimiters = ['。', '！', '？', '!', '?', '.', ';', '；']
        sentences = []
        current_sentence = ""
        
        # 更智能的句子分割
        for char in text:
            current_sentence += char
            if char in sentence_delimiters:
                # 处理可能的引号结尾
                next_idx = text.find(current_sentence) + len(current_sentence)
                if next_idx < len(text) and text[next_idx] in ['"', '"', ''', ''']:
                    continue
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        # 处理最后一个可能没有标点符号的句子
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # 将句子组合成chunks，确保每个chunk的token数不超过限制
        chunks = []
        current_chunk = []
        current_chunk_tokens = []
        
        for sentence in sentences:
            # 获取当前句子的tokens
            sentence_tokens = self.encoding.encode(sentence)
            
            # 如果单个句子的tokens就超过了限制
            if len(sentence_tokens) > chunk_tokens:
                # 先处理当前chunk中的内容
                if current_chunk:
                    chunk_text = ''.join(current_chunk)
                    chunks.append(chunk_text)
                    current_chunk = []
                    current_chunk_tokens = []
                
                # 尝试在标点符号处分割长句子
                sub_sentences = []
                temp = ""
                for char in sentence:
                    temp += char
                    if char in [',', '，', '、', '；', ';']:
                        if temp.strip():
                            sub_sentences.append(temp.strip())
                            temp = ""
                if temp.strip():
                    sub_sentences.append(temp.strip())
                
                # 处理子句
                current_sub_chunk = []
                current_sub_tokens = []
                
                for sub_sentence in sub_sentences:
                    sub_tokens = self.encoding.encode(sub_sentence)
                    if current_sub_tokens and len(current_sub_tokens) + len(sub_tokens) > chunk_tokens:
                        # 当前子句组合达到限制，保存并创建新的
                        sub_text = ''.join(current_sub_chunk)
                        chunks.append(sub_text)
                        current_sub_chunk = []
                        current_sub_tokens = []
                    
                    current_sub_chunk.append(sub_sentence)
                    current_sub_tokens.extend(sub_tokens)
                
                # 处理剩余的子句
                if current_sub_chunk:
                    sub_text = ''.join(current_sub_chunk)
                    chunks.append(sub_text)
                continue
            
            # 检查添加当前句子是否会超过token限制
            if current_chunk_tokens and len(current_chunk_tokens) + len(sentence_tokens) > chunk_tokens:
                # 当前chunk已满，保存并创建新chunk
                chunk_text = ''.join(current_chunk)
                chunks.append(chunk_text)
                current_chunk = []
                current_chunk_tokens = []
            
            # 添加句子到当前chunk
            current_chunk.append(sentence)
            current_chunk_tokens.extend(sentence_tokens)
        
        # 处理最后一个chunk
        if current_chunk:
            chunk_text = ''.join(current_chunk)
            chunks.append(chunk_text)
        
        return chunks
    
    def add_long_text(self, text: str, chunk_tokens: int = 1000) -> Dict[str, Any]:
        """
        添加长文本到向量数据库，会自动按句子和token数量分段
        
        Args:
            text: 长文本内容
            chunk_tokens: 每段文本的最大token数量，默认1000
            
        Returns:
            Dict[str, Any]: 包含添加信息的字典
                - total_chunks: 总分段数
                - total_tokens: 总token数
                - chunks_info: 每段文本的token数统计
                以及add_texts的所有返回信息
        """
        # 分割文本
        chunks = self.split_text(text, chunk_tokens)
        
        # 计算每段的token数
        chunks_info = [len(self.encoding.encode(chunk)) for chunk in chunks]
        total_tokens = sum(chunks_info)
        
        # 添加所有文本段到向量数据库
        add_result = self.add_texts(chunks)
        
        # 合并返回信息
        return {
            **add_result,  # 包含add_texts的所有返回信息
            "total_chunks": len(chunks),
            "total_tokens": total_tokens,
            "chunks_info": chunks_info
        }
    
    def search_fast(self, query: str, texts: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        快速搜索方法，不保存向量到数据库，直接从提供的文本列表中查找最相似的结果
        
        Args:
            query: 查询文本
            texts: 要搜索的文本列表
            top_k: 返回最相似的结果数量
            
        Returns:
            包含相似度得分和原始文本的结果列表
        """
        if not texts:
            return []
        
        # 创建临时索引
        temp_index = faiss.IndexFlatL2(1536)  # OpenAI text-embedding-3-small 模型输出1536维向量
        
        # 获取所有文本的embedding
        embeddings = []
        for text in texts:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
        
        # 将embeddings添加到临时索引
        embeddings_array = np.array(embeddings).astype('float32')
        temp_index.add(embeddings_array)
        
        # 获取查询文本的embedding
        query_embedding = self.get_embedding(query)
        query_embedding_array = np.array([query_embedding]).astype('float32')
        
        # 执行搜索
        distances, indices = temp_index.search(query_embedding_array, min(top_k, len(texts)))
        
        # 构建结果
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(texts):  # 确保索引有效
                results.append({
                    'text': texts[idx],
                    'score': float(dist),  # 转换numpy float32为Python float
                    'rank': i + 1
                })
        
        return results
