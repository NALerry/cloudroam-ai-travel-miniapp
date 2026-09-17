# database/vector_client.py
import os
import ssl
import numpy as np
import hashlib
import pickle
from typing import List, Dict, Optional

# ========== 解决 SSL 证书问题和网络问题 ==========
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMER_AVAILABLE = True
    print("✅ sentence-transformers 已加载")
except ImportError as e:
    SENTENCE_TRANSFORMER_AVAILABLE = False
    print(f"⚠️ sentence-transformers 未安装: {e}")

from config import Config


class VectorDBClient:
    """基于 SentenceTransformer 的向量数据库，使用 FAISS 进行高效检索"""

    def __init__(self):
        self.vector_path = Config.VECTOR_DB_PATH
        os.makedirs(self.vector_path, exist_ok=True)

        self.model = None
        self._init_model()

        self.documents = []
        self.metadatas = []
        self.ids = []
        self.embeddings = None

        self._init_empty_index()
        self._load_index()

    def _init_model(self):
        """初始化 embedding 模型"""
        if not SENTENCE_TRANSFORMER_AVAILABLE:
            print("❌ sentence-transformers 不可用")
            return

        print(f"📥 加载 Embedding 模型: {Config.EMBEDDING_MODEL}")
        print(f"🌐 使用镜像: {os.environ.get('HF_ENDPOINT', 'https://huggingface.co')}")

        try:
            self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
            test_embedding = self.model.encode("测试")
            dimension = len(test_embedding)
            print(f"✅ 模型加载成功！")
            print(f"   - 向量维度: {dimension}")
            print(f"   - 模型名称: {Config.EMBEDDING_MODEL}")
        except Exception as e:
            print(f"❌ 加载模型失败: {e}")
            raise

    def _init_empty_index(self):
        """初始化空 FAISS 索引"""
        try:
            import faiss
            if self.model is None:
                print("⚠️ 模型未初始化，无法创建索引")
                return
            sample_embedding = self.model.encode("test")
            dimension = len(sample_embedding)
            self.embeddings = faiss.IndexFlatIP(dimension)
            print(f"✅ FAISS 索引已创建，维度: {dimension}")
        except ImportError:
            print("⚠️ FAISS 未安装，使用 numpy 方案")
            self.embeddings = None

    def _normalize_vector(self, vector):
        norm = np.linalg.norm(vector)
        if norm > 0:
            return vector / norm
        return vector

    def _load_index(self):
        """加载已有的索引"""
        index_file = os.path.join(self.vector_path, 'faiss_index.bin')
        docs_file = os.path.join(self.vector_path, 'documents.pkl')

        if os.path.exists(index_file) and os.path.exists(docs_file):
            try:
                import faiss
                self.embeddings = faiss.read_index(index_file)
                with open(docs_file, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.metadatas = data.get('metadatas', [])
                    self.ids = data.get('ids', [])
                print(f"✅ 加载已有索引，共 {len(self.documents)} 个文档块")
            except Exception as e:
                print(f"⚠️ 加载索引失败: {e}，将创建新索引")
                self._init_empty_index()

    def _save_index(self):
        """保存索引到磁盘"""
        try:
            import faiss
            if self.embeddings is not None:
                index_file = os.path.join(self.vector_path, 'faiss_index.bin')
                faiss.write_index(self.embeddings, index_file)

            docs_file = os.path.join(self.vector_path, 'documents.pkl')
            with open(docs_file, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'metadatas': self.metadatas,
                    'ids': self.ids
                }, f)
            print(f"💾 索引已保存，共 {len(self.documents)} 个文档块")
        except Exception as e:
            print(f"❌ 保存索引失败: {e}")

    def add_documents(self, chunks: List[Dict]) -> List[str]:
        """添加文档块到向量数据库"""
        if self.model is None:
            print("❌ 模型未初始化，无法添加文档")
            return []

        added_ids = []
        embeddings_list = []

        for chunk in chunks:
            content_hash = hashlib.md5(chunk['content'].encode()).hexdigest()[:16]
            source_name = chunk['metadata'].get('source', 'unknown')
            source_name = source_name.replace('/', '_').replace('\\', '_')
            doc_id = f"{source_name}_{content_hash}"

            if doc_id in self.ids:
                print(f"⏭️ 文档块已存在: {doc_id[:30]}...")
                continue

            print(f"🔄 计算向量: {doc_id[:30]}...")
            try:
                embedding = self.model.encode(chunk['content'])
                embedding = self._normalize_vector(embedding)
            except Exception as e:
                print(f"❌ 向量计算失败: {e}")
                continue

            self.documents.append(chunk['content'])
            self.metadatas.append(chunk['metadata'])
            self.ids.append(doc_id)
            embeddings_list.append(embedding)
            added_ids.append(doc_id)

        if embeddings_list and self.embeddings is not None:
            import faiss
            embeddings_array = np.array(embeddings_list).astype('float32')
            self.embeddings.add(embeddings_array)
            self._save_index()
            print(f"✅ 成功添加 {len(added_ids)} 个文档块")

        return added_ids

    def search(self, query: str, top_k: int = Config.TOP_K_RETRIEVAL) -> List[Dict]:
        """向量检索（语义相似度）"""
        if self.model is None:
            print("❌ 模型未初始化，无法检索")
            return []

        if len(self.documents) == 0:
            print("⚠️ 知识库为空，请先上传文档")
            return []

        try:
            print(f"🔍 检索: {query[:50]}...")
            query_embedding = self.model.encode(query)
            query_embedding = self._normalize_vector(query_embedding)
            query_embedding = np.array([query_embedding]).astype('float32')

            k = min(top_k, len(self.documents))

            if self.embeddings is not None:
                distances, indices = self.embeddings.search(query_embedding, k)
                indices = indices[0]
                distances = distances[0]
            else:
                indices = []
                distances = []
                print("⚠️ FAISS 不可用，检索效果可能不佳")

            search_results = []
            for i, idx in enumerate(indices):
                if idx >= 0 and idx < len(self.documents):
                    similarity = float(distances[i])
                    if similarity > Config.SIMILARITY_THRESHOLD:
                        search_results.append({
                            'content': self.documents[idx],
                            'metadata': self.metadatas[idx],
                            'similarity': similarity,
                            'id': self.ids[idx] if idx < len(self.ids) else None
                        })

            search_results.sort(key=lambda x: x['similarity'], reverse=True)

            if search_results:
                print(f"✅ 找到 {len(search_results)} 条结果，最高相似度: {search_results[0]['similarity']:.3f}")
            else:
                print("❌ 未找到相关结果")

            return search_results

        except Exception as e:
            print(f"❌ 向量检索失败: {e}")
            return []

    def get_collection_stats(self) -> Dict:
        """获取统计信息"""
        stats = {
            "total_chunks": len(self.documents),
            "collection_name": "knowledge_base",
            "status": "active",
            "mode": "semantic_search"
        }
        if self.embeddings is not None and hasattr(self.embeddings, 'd'):
            stats["vector_dimension"] = self.embeddings.d
        return stats

    def list_sources(self) -> List[str]:
        """列出所有知识来源"""
        sources = set()
        for meta in self.metadatas:
            if meta and 'source' in meta:
                sources.add(meta['source'])
        return list(sources)

    def delete_by_source(self, source: str) -> bool:
        """删除指定来源的所有文档块"""
        try:
            import faiss

            keep_documents = []
            keep_metadatas = []
            keep_ids = []
            embeddings_to_keep = []

            for i, meta in enumerate(self.metadatas):
                if meta.get('source') != source:
                    keep_documents.append(self.documents[i])
                    keep_metadatas.append(self.metadatas[i])
                    keep_ids.append(self.ids[i])
                    emb = self.model.encode(self.documents[i])
                    emb = self._normalize_vector(emb)
                    embeddings_to_keep.append(emb)

            if embeddings_to_keep:
                embeddings_array = np.array(embeddings_to_keep).astype('float32')
                dimension = len(embeddings_array[0])
                new_index = faiss.IndexFlatIP(dimension)
                new_index.add(embeddings_array)

                self.embeddings = new_index
                self.documents = keep_documents
                self.metadatas = keep_metadatas
                self.ids = keep_ids
            else:
                self._init_empty_index()
                self.documents = []
                self.metadatas = []
                self.ids = []

            self._save_index()
            print(f"🗑️ 删除来源 '{source}'，剩余 {len(self.documents)} 个文档块")
            return True

        except Exception as e:
            print(f"❌ 删除失败: {e}")
            return False

    def delete_collection(self) -> bool:
        """删除所有数据"""
        self._init_empty_index()
        self.documents = []
        self.metadatas = []
        self.ids = []
        self._save_index()
        print("🗑️ 已清空所有向量数据")
        return True

    # ========== 辅助方法 ==========

    def is_loaded(self) -> bool:
        """检查索引是否已加载且有数据"""
        return len(self.documents) > 0

    def get_chunk_count(self) -> int:
        """获取文档块数量"""
        return len(self.documents)

    def force_reload(self):
        """强制重新加载索引"""
        print("🔄 强制重新加载向量索引...")
        self._load_index()
        print(f"   ✅ 加载完成，共 {len(self.documents)} 个文档块")

    def get_all_sources(self) -> List[str]:
        """获取所有知识来源"""
        return self.list_sources()