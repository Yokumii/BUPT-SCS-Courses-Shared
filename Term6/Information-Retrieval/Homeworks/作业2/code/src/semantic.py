"""
语义检索：Word2Vec + TF-IDF 加权文档向量。

在线查询阶段使用单份矩阵与文档 ID 数组，
支持 `numpy.load(..., mmap_mode="r")` 降低常驻内存。
"""

import os
import pickle

import numpy as np

from src.preprocessor import preprocess
from src.indexer import InvertedIndex


_LEGACY_DOC_VECTORS_FILE = "doc_vectors.pkl"
_DOC_VECTOR_IDS_FILE = "doc_vector_ids.npy"


def semantic_assets_exist(index_dir: str = "index") -> bool:
    """判断语义检索所需资产是否存在。"""
    return os.path.exists(os.path.join(index_dir, "w2v.model")) and (
        os.path.exists(os.path.join(index_dir, "doc_vectors.npy"))
        or os.path.exists(os.path.join(index_dir, _LEGACY_DOC_VECTORS_FILE))
    )


class SemanticRetriever:
    """基于 Word2Vec + TF-IDF 加权的语义检索器。"""

    def __init__(
        self,
        index: InvertedIndex,
        model_path: str = "index/w2v.model",
        doc_vectors_path: str = "index/doc_vectors.npy",
    ):
        self.index = index
        self.model_path = model_path
        self.doc_vectors_path = doc_vectors_path
        self.doc_ids_path = self._doc_ids_path_from_vectors_path(doc_vectors_path)
        self.w2v_model = None
        self.doc_ids = np.array([], dtype=np.int32)
        self.doc_matrix = None
        self.doc_id_to_row = {}
        self.vector_dim = 100

    @staticmethod
    def _doc_ids_path_from_vectors_path(doc_vectors_path: str) -> str:
        base, _ = os.path.splitext(doc_vectors_path)
        return f"{base.replace('doc_vectors', 'doc_vector_ids')}.npy"

    def _rebuild_doc_id_lookup(self):
        self.doc_id_to_row = {
            int(doc_id): row
            for row, doc_id in enumerate(self.doc_ids.tolist())
        }

    def train(
        self,
        documents: list,
        vector_size: int = 100,
        window: int = 5,
        min_count: int = 5,
        epochs: int = 10,
        verbose: bool = True,
    ):
        """
        训练 Word2Vec 模型并构建文档向量。

        参数:
            documents: Document 对象列表（需已完成预处理）
            vector_size: 词向量维度
            window: 上下文窗口大小
            min_count: 最小词频
            epochs: 训练轮数
        """
        from gensim.models import Word2Vec

        self.vector_dim = vector_size

        if verbose:
            print("准备训练语料...")
        corpus = [doc.tokens for doc in documents if doc.tokens]

        if verbose:
            print(f"训练 Word2Vec (dim={vector_size}, window={window})...")
        self.w2v_model = Word2Vec(
            sentences=corpus,
            vector_size=vector_size,
            window=window,
            min_count=min_count,
            workers=4,
            epochs=epochs,
        )

        if verbose:
            print(f"词汇量: {len(self.w2v_model.wv)}")
            print("构建文档向量...")

        doc_ids = []
        doc_rows = []
        for doc in documents:
            vec = self._compute_doc_vector(doc.tokens)
            if vec is not None:
                doc_ids.append(doc.doc_id)
                doc_rows.append(vec.astype(np.float32, copy=False))

        self.doc_ids = np.asarray(doc_ids, dtype=np.int32)
        self.doc_matrix = (
            np.vstack(doc_rows).astype(np.float32, copy=False)
            if doc_rows
            else np.empty((0, vector_size), dtype=np.float32)
        )
        self._rebuild_doc_id_lookup()

        if verbose:
            print(f"文档向量: {len(self.doc_ids)} 篇")

    def _compute_doc_vector(self, tokens: list) -> np.ndarray:
        """计算单篇文档的 TF-IDF 加权词向量。"""
        if not tokens or self.w2v_model is None:
            return None

        vec = np.zeros(self.vector_dim, dtype=np.float32)
        weight_sum = 0.0

        for token in tokens:
            if token in self.w2v_model.wv:
                idf = self.index.get_idf(token)
                vec += idf * self.w2v_model.wv[token]
                weight_sum += idf

        if weight_sum > 0:
            vec /= weight_sum
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            return vec
        return None

    def build_query_vector(self, query: str) -> np.ndarray:
        """
        将查询字符串转换为 TF-IDF 加权的 Word2Vec 向量。

        参数:
            query: 查询字符串

        返回:
            L2 归一化后的查询向量，失败时返回 None
        """
        query_tokens = preprocess(query)
        if not query_tokens or self.w2v_model is None:
            return None

        q_vec = np.zeros(self.vector_dim, dtype=np.float32)
        weight_sum = 0.0
        for token in query_tokens:
            if token in self.w2v_model.wv:
                idf = self.index.get_idf(token)
                q_vec += idf * self.w2v_model.wv[token]
                weight_sum += idf

        if weight_sum == 0:
            return None
        q_vec /= weight_sum
        norm = np.linalg.norm(q_vec)
        if norm > 0:
            q_vec /= norm
        return q_vec

    def get_doc_vector(self, doc_id: int) -> np.ndarray | None:
        """按文档 ID 读取单条语义向量。"""
        row = self.doc_id_to_row.get(doc_id)
        if row is None or self.doc_matrix is None:
            return None
        return self.doc_matrix[row]

    def search_with_vector(self, q_vec: np.ndarray, top_k: int = 10) -> list:
        """
        使用预构建的查询向量检索文档。

        参数:
            q_vec: 查询向量（应已 L2 归一化）
            top_k: 返回结果数量

        返回:
            [(doc_id, score), ...] 按分数降序排列
        """
        if q_vec is None or self.doc_matrix is None or len(self.doc_ids) == 0:
            return []

        sims = self.doc_matrix @ q_vec
        top_indices = np.argsort(sims)[::-1][:top_k]
        results = [
            (int(self.doc_ids[i]), float(sims[i]))
            for i in top_indices
            if sims[i] > 0
        ]
        return results

    def search(self, query: str, top_k: int = 10) -> list:
        """
        语义检索：计算查询向量与文档向量的余弦相似度。
        """
        if self.doc_matrix is None:
            return []
        q_vec = self.build_query_vector(query)
        return self.search_with_vector(q_vec, top_k)

    def save(self):
        """保存 Word2Vec 模型和文档向量矩阵。"""
        if self.w2v_model:
            self.w2v_model.save(self.model_path)

        if self.doc_matrix is None:
            matrix = np.empty((0, self.vector_dim), dtype=np.float32)
        else:
            matrix = np.asarray(self.doc_matrix, dtype=np.float32)

        np.save(self.doc_vectors_path, matrix)
        np.save(self.doc_ids_path, np.asarray(self.doc_ids, dtype=np.int32))
        print(f"语义模型已保存: {self.model_path}")

    def _load_legacy_doc_vectors(self):
        """兼容旧的 doc_vectors.pkl 格式。"""
        legacy_path = (
            self.doc_vectors_path
            if self.doc_vectors_path.endswith(".pkl")
            else os.path.join(os.path.dirname(self.doc_vectors_path), _LEGACY_DOC_VECTORS_FILE)
        )
        if not os.path.exists(legacy_path):
            return False

        with open(legacy_path, "rb") as f:
            data = pickle.load(f)
        legacy_vectors = data.get("doc_vectors", {})
        self.vector_dim = int(data.get("vector_dim", self.vector_dim))

        if legacy_vectors:
            ordered_ids = sorted(legacy_vectors.keys())
            self.doc_ids = np.asarray(ordered_ids, dtype=np.int32)
            self.doc_matrix = np.vstack(
                [np.asarray(legacy_vectors[doc_id], dtype=np.float32) for doc_id in ordered_ids]
            ).astype(np.float32, copy=False)
        else:
            self.doc_ids = np.array([], dtype=np.int32)
            self.doc_matrix = np.empty((0, self.vector_dim), dtype=np.float32)

        self._rebuild_doc_id_lookup()
        return True

    def load(self):
        """加载 Word2Vec 模型和文档向量矩阵。"""
        try:
            from gensim.models import Word2Vec

            if os.path.exists(self.model_path):
                self.w2v_model = Word2Vec.load(self.model_path)
        except Exception as e:
            print(f"[警告] Word2Vec 模型加载失败: {e}")
            self.w2v_model = None

        try:
            if os.path.exists(self.doc_vectors_path) and os.path.exists(self.doc_ids_path):
                self.doc_matrix = np.load(self.doc_vectors_path, mmap_mode="r")
                self.doc_ids = np.load(self.doc_ids_path, mmap_mode="r")
                if self.doc_matrix.ndim == 2 and self.doc_matrix.shape[1] > 0:
                    self.vector_dim = int(self.doc_matrix.shape[1])
                self._rebuild_doc_id_lookup()
            elif self._load_legacy_doc_vectors():
                pass
            else:
                self.doc_ids = np.array([], dtype=np.int32)
                self.doc_matrix = np.empty((0, self.vector_dim), dtype=np.float32)

            print(f"语义模型已加载: {len(self.doc_ids)} 篇文档向量")
        except Exception as e:
            print(f"[警告] 文档向量加载失败: {e}")
            self.doc_ids = np.array([], dtype=np.int32)
            self.doc_matrix = None
            self.doc_id_to_row = {}

        return self
