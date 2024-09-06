from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter





class EmbeddingSearch:
    def __init__(self, model_name='distilbert-base-nli-mean-tokens', 
                 index_file='faiss_index.idx', 
                 documents_file='documents.pkl',
                 storage_dir='static/embedding'):
        self.model = SentenceTransformer(model_name)
        self.storage_dir = storage_dir
        self.index_file = os.path.join(storage_dir, index_file)
        self.documents_file = os.path.join(storage_dir, documents_file)
        self.index = None
        self.documents = []

        # 确保存储目录存在
        os.makedirs(self.storage_dir, exist_ok=True)
        self.load()

            
    def add_documents(self, documents):
        print(f"添加文档数量: {len(documents)}")
        self.documents.extend(documents)
        embeddings = self.model.encode(documents)
        
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
        
        self.index.add(embeddings.astype('float32'))
        self.save()  # 每次添加文档后自动保存
        print(f"当前文档总数: {len(self.documents)}")
        print(f"当前索引大小: {self.index.ntotal}")
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
        # 添加分割后的段落到文档集
        self.add_documents(source_text_chunks)
    def save(self):
        print("保存索引和文档...")
        faiss.write_index(self.index, self.index_file)
        with open(self.documents_file, 'wb') as f:
            pickle.dump(self.documents, f)
        print("保存完成。")

    def load(self):
        if os.path.exists(self.index_file) and os.path.exists(self.documents_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.documents_file, 'rb') as f:
                self.documents = pickle.load(f)
            print(f"加载索引和文档完成。文档数量: {len(self.documents)}")
        else:
            print(f"索引文件或文档文件不存在。将创建新的索引和文档列表。")
            self.index = None
            self.documents = []

    def search(self, query, top_k=2):
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(query_vector.astype('float32'), top_k)
        results = [(distances[0][i], self.documents[indices[0][i]]) for i in range(len(indices[0]))]
        return results

    def display_all_documents(self):
        if not self.documents:
            # print("没有文档可显示。")
            return
        
        return self.documents
        for i, doc in enumerate(self.documents):
            print(f"文档 {i+1}: {doc}")
    def calculate_chunk_size(self,token_count: int, token_limit: int) -> int:
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
# 使用示例
if __name__ == "__main__":
    es = EmbeddingSearch()
    
    # 添加文档
    documents = [
        "这是第一个文档的内容",
        "第二个文档讲述了不同的内容",
        "第三个文档与第一个有些相似",
        "这是完全不相关的第四个文档"
    ]
    es.add_documents(documents)
    
    # 保存索引和文档
    es.save()
    
    # 加载索引和文档
    es.load()
    
    # 搜索相似内容
    query = "相似的文档"
    results = es.search(query)
    
    for distance, document in results:
        print(f"距离: {distance}, 文档: {document}")