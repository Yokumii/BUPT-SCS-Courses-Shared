"""
Rocchio 相关性反馈：支持 TF-IDF、BM25、Semantic 三种检索模型的
相关性反馈，包括交互式反馈和伪相关反馈（PRF）。
"""

import math
from collections import defaultdict
from dataclasses import dataclass

import numpy as np


@dataclass
class RocchioConfig:
    """Rocchio 算法参数配置。"""
    alpha: float = 1.0    # 原始查询权重
    beta: float = 0.75    # 相关文档权重
    gamma: float = 0.15   # 不相关文档权重


class RocchioTFIDF:
    """基于 TF-IDF 向量空间的 Rocchio 反馈。"""

    def __init__(self, index, config: RocchioConfig = None):
        self.index = index
        self.config = config or RocchioConfig()

    def _build_doc_vectors_batch(self, doc_ids: set) -> dict:
        """
        批量重建多篇文档的稀疏 TF-IDF 向量。

        单次遍历倒排索引，避免按文档逐一查询。

        参数:
            doc_ids: 需要重建向量的文档 ID 集合

        返回:
            {doc_id: {term: tfidf_weight, ...}, ...}
        """
        vectors = {did: {} for did in doc_ids}
        for term, (posting_doc_ids, posting_tfs) in self.index.iter_postings_arrays():
            idf = self.index.get_idf(term)
            for posting_doc_id, posting_tf in zip(posting_doc_ids, posting_tfs):
                posting_doc_id = int(posting_doc_id)
                if posting_doc_id in doc_ids:
                    tf_weight = 1 + math.log(int(posting_tf)) if posting_tf > 0 else 0
                    vectors[posting_doc_id][term] = tf_weight * idf
        return vectors

    def apply_feedback(self, query_weights: dict,
                       relevant_ids: set, non_relevant_ids: set) -> dict:
        """
        执行 Rocchio 公式调整查询向量。

        q' = α·q + β·centroid(rel) - γ·centroid(nrel)
        负权重截断为 0。

        参数:
            query_weights: 原始查询权重字典
            relevant_ids: 相关文档 ID 集合
            non_relevant_ids: 不相关文档 ID 集合

        返回:
            调整后的查询权重字典
        """
        # 收集需要重建向量的所有文档
        all_ids = relevant_ids | non_relevant_ids
        if not all_ids:
            return dict(query_weights)

        doc_vectors = self._build_doc_vectors_batch(all_ids)

        # 计算相关文档质心
        rel_centroid = defaultdict(float)
        if relevant_ids:
            for did in relevant_ids:
                for term, weight in doc_vectors[did].items():
                    rel_centroid[term] += weight
            n_rel = len(relevant_ids)
            for term in rel_centroid:
                rel_centroid[term] /= n_rel

        # 计算不相关文档质心
        nrel_centroid = defaultdict(float)
        if non_relevant_ids:
            for did in non_relevant_ids:
                for term, weight in doc_vectors[did].items():
                    nrel_centroid[term] += weight
            n_nrel = len(non_relevant_ids)
            for term in nrel_centroid:
                nrel_centroid[term] /= n_nrel

        # Rocchio 公式
        all_terms = set(query_weights) | set(rel_centroid) | set(nrel_centroid)
        new_weights = {}
        for term in all_terms:
            w = (self.config.alpha * query_weights.get(term, 0.0)
                 + self.config.beta * rel_centroid.get(term, 0.0)
                 - self.config.gamma * nrel_centroid.get(term, 0.0))
            if w > 0:
                new_weights[term] = w

        return new_weights

    def search_with_feedback(self, retriever, query: str,
                             relevant_ids: set, non_relevant_ids: set,
                             top_k: int = 10) -> list:
        """
        执行带 Rocchio 反馈的 TF-IDF 检索。

        参数:
            retriever: TFIDFRetriever 实例
            query: 查询字符串
            relevant_ids: 相关文档 ID 集合
            non_relevant_ids: 不相关文档 ID 集合
            top_k: 返回结果数量

        返回:
            [(doc_id, score), ...] 按分数降序排列
        """
        query_weights = retriever.build_query_weights(query)
        new_weights = self.apply_feedback(query_weights, relevant_ids, non_relevant_ids)
        return retriever.search_with_weights(new_weights, top_k)


class RocchioSemantic:
    """基于 Word2Vec 密集向量空间的 Rocchio 反馈。"""

    def __init__(self, semantic_retriever, config: RocchioConfig = None):
        self.retriever = semantic_retriever
        self.config = config or RocchioConfig()

    def apply_feedback(self, query_vec: np.ndarray,
                       relevant_ids: set, non_relevant_ids: set) -> np.ndarray:
        """
        在密集向量空间执行 Rocchio 公式。

        参数:
            query_vec: 原始查询向量
            relevant_ids: 相关文档 ID 集合
            non_relevant_ids: 不相关文档 ID 集合

        返回:
            调整后的查询向量（L2 归一化）
        """
        dim = len(query_vec)

        # 计算相关文档质心
        rel_centroid = np.zeros(dim)
        if relevant_ids:
            count = 0
            for did in relevant_ids:
                doc_vec = self.retriever.get_doc_vector(did)
                if doc_vec is not None:
                    rel_centroid += doc_vec
                    count += 1
            if count > 0:
                rel_centroid /= count

        # 计算不相关文档质心
        nrel_centroid = np.zeros(dim)
        if non_relevant_ids:
            count = 0
            for did in non_relevant_ids:
                doc_vec = self.retriever.get_doc_vector(did)
                if doc_vec is not None:
                    nrel_centroid += doc_vec
                    count += 1
            if count > 0:
                nrel_centroid /= count

        # Rocchio 公式
        new_vec = (self.config.alpha * query_vec
                   + self.config.beta * rel_centroid
                   - self.config.gamma * nrel_centroid)

        # L2 归一化
        norm = np.linalg.norm(new_vec)
        if norm > 0:
            new_vec /= norm
        return new_vec

    def search_with_feedback(self, query: str,
                             relevant_ids: set, non_relevant_ids: set,
                             top_k: int = 10) -> list:
        """
        执行带 Rocchio 反馈的语义检索。

        参数:
            query: 查询字符串
            relevant_ids: 相关文档 ID 集合
            non_relevant_ids: 不相关文档 ID 集合
            top_k: 返回结果数量

        返回:
            [(doc_id, score), ...] 按分数降序排列
        """
        q_vec = self.retriever.build_query_vector(query)
        if q_vec is None:
            return []
        new_vec = self.apply_feedback(q_vec, relevant_ids, non_relevant_ids)
        return self.retriever.search_with_vector(new_vec, top_k)


class RocchioBM25:
    """基于查询扩展的 BM25 Rocchio 反馈。

    BM25 没有显式查询向量，因此通过 Rocchio 权重选取扩展词项，
    将高权重新词项追加到原始查询后重新检索。
    """

    def __init__(self, index, config: RocchioConfig = None):
        self.index = index
        self.config = config or RocchioConfig()

    def extract_expansion_terms(self, relevant_ids: set, non_relevant_ids: set,
                                original_terms: set,
                                max_terms: int = 10) -> list:
        """
        基于 Rocchio 权重选取扩展词项。

        参数:
            relevant_ids: 相关文档 ID 集合
            non_relevant_ids: 不相关文档 ID 集合
            original_terms: 原始查询词项集合
            max_terms: 最多选取的扩展词数

        返回:
            按权重降序排列的扩展词项列表
        """
        # 计算每个词项在相关/不相关文档中的 TF-IDF 均值
        rel_scores = defaultdict(float)
        nrel_scores = defaultdict(float)

        for term, (posting_doc_ids, posting_tfs) in self.index.iter_postings_arrays():
            idf = self.index.get_idf(term)
            for posting_doc_id, posting_tf in zip(posting_doc_ids, posting_tfs):
                posting_doc_id = int(posting_doc_id)
                posting_tf = int(posting_tf)
                if posting_doc_id in relevant_ids:
                    tf_w = 1 + math.log(posting_tf) if posting_tf > 0 else 0
                    rel_scores[term] += tf_w * idf
                elif posting_doc_id in non_relevant_ids:
                    tf_w = 1 + math.log(posting_tf) if posting_tf > 0 else 0
                    nrel_scores[term] += tf_w * idf

        n_rel = len(relevant_ids) if relevant_ids else 1
        n_nrel = len(non_relevant_ids) if non_relevant_ids else 1

        # 计算 Rocchio 分数（仅文档部分，不含原始查询项）
        term_scores = {}
        all_terms = set(rel_scores) | set(nrel_scores)
        for term in all_terms:
            score = (self.config.beta * rel_scores.get(term, 0.0) / n_rel
                     - self.config.gamma * nrel_scores.get(term, 0.0) / n_nrel)
            if score > 0:
                term_scores[term] = score

        # 按权重排序，选取 top-N（包含原始词项）
        ranked = sorted(term_scores.items(), key=lambda x: x[1], reverse=True)
        expansion = []
        for term, score in ranked:
            expansion.append(term)
            if len(expansion) >= max_terms:
                break

        return expansion

    def search_with_feedback(self, retriever, query: str,
                             relevant_ids: set, non_relevant_ids: set,
                             top_k: int = 10) -> list:
        """
        执行带 Rocchio 查询扩展的 BM25 检索。

        参数:
            retriever: BM25Retriever 实例
            query: 查询字符串
            relevant_ids: 相关文档 ID 集合
            non_relevant_ids: 不相关文档 ID 集合
            top_k: 返回结果数量

        返回:
            [(doc_id, score), ...] 按分数降序排列
        """
        from src.preprocessor import preprocess
        original_terms = set(preprocess(query))

        expansion = self.extract_expansion_terms(
            relevant_ids, non_relevant_ids, original_terms)

        # 将扩展词追加到原始查询
        expanded_query = query + " " + " ".join(expansion)
        return retriever.search(expanded_query, top_k)


def pseudo_relevance_feedback(retriever, query: str, index,
                              prf_top_n: int = 5, top_k: int = 10,
                              config: RocchioConfig = None) -> list:
    """
    伪相关反馈（PRF）：初始检索后假设 Top-N 文档相关，自动执行 Rocchio 反馈。

    参数:
        retriever: 检索器实例（TFIDFRetriever / BM25Retriever / SemanticRetriever）
        query: 查询字符串
        index: 倒排索引（用于构建 Rocchio 实例）
        prf_top_n: 假设相关的文档数
        top_k: 最终返回结果数
        config: Rocchio 参数配置

    返回:
        [(doc_id, score), ...] 反馈后的检索结果
    """
    # 初始检索
    initial_results = retriever.search(query, top_k=prf_top_n)
    if not initial_results:
        return []

    relevant_ids = {doc_id for doc_id, _ in initial_results}
    non_relevant_ids = set()

    # 根据检索器类型分发到对应 Rocchio 类
    from src.retriever import TFIDFRetriever, BM25Retriever

    if isinstance(retriever, TFIDFRetriever):
        rocchio = RocchioTFIDF(index, config)
        return rocchio.search_with_feedback(
            retriever, query, relevant_ids, non_relevant_ids, top_k)
    elif isinstance(retriever, BM25Retriever):
        rocchio = RocchioBM25(index, config)
        return rocchio.search_with_feedback(
            retriever, query, relevant_ids, non_relevant_ids, top_k)
    else:
        # SemanticRetriever
        rocchio = RocchioSemantic(retriever, config)
        return rocchio.search_with_feedback(
            query, relevant_ids, non_relevant_ids, top_k)
