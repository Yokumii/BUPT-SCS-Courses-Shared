"""
测试 Rocchio 相关性反馈模块。
"""

import math

import pytest
from src.retriever import TFIDFRetriever, BM25Retriever
from src.feedback import (
    RocchioConfig, RocchioTFIDF, RocchioSemantic, RocchioBM25,
    pseudo_relevance_feedback,
)


class TestRocchioConfig:
    """测试 Rocchio 配置。"""

    def test_default_values(self):
        """默认参数值应正确。"""
        cfg = RocchioConfig()
        assert cfg.alpha == 1.0
        assert cfg.beta == 0.75
        assert cfg.gamma == 0.15

    def test_custom_values(self):
        """自定义参数值应正确。"""
        cfg = RocchioConfig(alpha=2.0, beta=0.5, gamma=0.3)
        assert cfg.alpha == 2.0
        assert cfg.beta == 0.5
        assert cfg.gamma == 0.3


class TestRocchioTFIDF:
    """测试 TF-IDF Rocchio 反馈。"""

    def test_apply_feedback_positive_only(self, sample_index):
        """仅正反馈应增强查询。"""
        retriever = TFIDFRetriever(sample_index)
        rocchio = RocchioTFIDF(sample_index)

        query_weights = retriever.build_query_weights("machine learning")
        assert len(query_weights) > 0

        # doc 0 是 machine learning 相关的
        new_weights = rocchio.apply_feedback(query_weights, relevant_ids={0}, non_relevant_ids=set())
        # 反馈后应至少包含原始词项
        for term in query_weights:
            assert term in new_weights

    def test_apply_feedback_mixed(self, sample_index):
        """正负混合反馈应调整权重。"""
        rocchio = RocchioTFIDF(sample_index)
        retriever = TFIDFRetriever(sample_index)

        query_weights = retriever.build_query_weights("learning")
        new_weights = rocchio.apply_feedback(
            query_weights, relevant_ids={0}, non_relevant_ids={1})

        # 结果应有效（所有权重为正）
        for w in new_weights.values():
            assert w > 0

    def test_apply_feedback_no_negative_weights(self, sample_index):
        """反馈后不应有负权重。"""
        rocchio = RocchioTFIDF(sample_index, RocchioConfig(gamma=10.0))
        retriever = TFIDFRetriever(sample_index)

        query_weights = retriever.build_query_weights("learning")
        new_weights = rocchio.apply_feedback(
            query_weights, relevant_ids=set(), non_relevant_ids={0, 1, 2})

        for w in new_weights.values():
            assert w > 0

    def test_search_with_feedback(self, sample_index):
        """反馈检索应返回有效结果。"""
        retriever = TFIDFRetriever(sample_index)
        rocchio = RocchioTFIDF(sample_index)

        results = rocchio.search_with_feedback(
            retriever, "machine learning",
            relevant_ids={0}, non_relevant_ids={1}, top_k=3)

        assert len(results) > 0
        for doc_id, score in results:
            assert isinstance(doc_id, int)
            assert score > 0

    def test_empty_feedback(self, sample_index):
        """空反馈应返回与原始查询相同的权重。"""
        retriever = TFIDFRetriever(sample_index)
        rocchio = RocchioTFIDF(sample_index)

        query_weights = retriever.build_query_weights("machine learning")
        new_weights = rocchio.apply_feedback(query_weights, set(), set())

        # alpha=1.0 且无反馈，权重应与原始相同
        for term, w in query_weights.items():
            assert abs(new_weights[term] - w) < 1e-6


class TestTFIDFSearchWithWeights:
    """测试 TFIDFRetriever.search_with_weights 一致性。"""

    def test_consistency_with_search(self, sample_index):
        """search_with_weights 应与 search 结果一致。"""
        retriever = TFIDFRetriever(sample_index)
        query = "machine learning healthcare"

        # 两种方式应产生相同结果
        results_direct = retriever.search(query, top_k=10)
        weights = retriever.build_query_weights(query)
        results_weights = retriever.search_with_weights(weights, top_k=10)

        assert len(results_direct) == len(results_weights)
        for (d1, s1), (d2, s2) in zip(results_direct, results_weights):
            assert d1 == d2
            assert abs(s1 - s2) < 1e-6

    def test_empty_weights(self, sample_index):
        """空权重应返回空结果。"""
        retriever = TFIDFRetriever(sample_index)
        assert retriever.search_with_weights({}) == []


class TestRocchioBM25:
    """测试 BM25 Rocchio 反馈。"""

    def test_extract_expansion_terms(self, sample_index):
        """扩展词应包含相关文档中的高权重词项。"""
        rocchio = RocchioBM25(sample_index)
        terms = rocchio.extract_expansion_terms(
            relevant_ids={0}, non_relevant_ids={1},
            original_terms={"machin", "learn"}, max_terms=10)
        assert len(terms) > 0

    def test_search_with_feedback(self, sample_index):
        """BM25 反馈检索应返回有效结果。"""
        retriever = BM25Retriever(sample_index)
        rocchio = RocchioBM25(sample_index)

        results = rocchio.search_with_feedback(
            retriever, "machine learning",
            relevant_ids={0}, non_relevant_ids={1}, top_k=3)

        assert len(results) > 0
        for doc_id, score in results:
            assert isinstance(doc_id, int)
            assert score > 0


class TestPseudoRelevanceFeedback:
    """测试伪相关反馈（PRF）。"""

    def test_prf_tfidf(self, sample_index):
        """PRF 对 TF-IDF 应返回有效结果。"""
        retriever = TFIDFRetriever(sample_index)
        results = pseudo_relevance_feedback(
            retriever, "machine learning", sample_index,
            prf_top_n=2, top_k=3)
        assert len(results) > 0

    def test_prf_bm25(self, sample_index):
        """PRF 对 BM25 应返回有效结果。"""
        retriever = BM25Retriever(sample_index)
        results = pseudo_relevance_feedback(
            retriever, "climate change", sample_index,
            prf_top_n=2, top_k=3)
        assert len(results) > 0

    def test_prf_empty_query(self, sample_index):
        """空查询 PRF 应返回空结果。"""
        retriever = TFIDFRetriever(sample_index)
        results = pseudo_relevance_feedback(
            retriever, "", sample_index, prf_top_n=2, top_k=3)
        assert results == []

    def test_prf_no_results_query(self, sample_index):
        """无结果查询 PRF 应返回空。"""
        retriever = BM25Retriever(sample_index)
        results = pseudo_relevance_feedback(
            retriever, "xyznonexistent", sample_index,
            prf_top_n=2, top_k=3)
        assert results == []
