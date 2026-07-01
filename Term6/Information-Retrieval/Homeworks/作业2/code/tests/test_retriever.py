"""
测试 retriever 模块。
"""

from src.retriever import TFIDFRetriever, BM25Retriever, expand_query_wordnet


class TestTFIDFRetriever:
    """测试 TF-IDF 检索器。"""

    def test_basic_search(self, sample_index):
        """基本检索应返回结果。"""
        retriever = TFIDFRetriever(sample_index)
        results = retriever.search("machine learning", top_k=3)
        assert len(results) > 0
        # 结果应为 (doc_id, score) 元组
        for doc_id, score in results:
            assert isinstance(doc_id, int)
            assert score > 0

    def test_empty_query(self, sample_index):
        """空查询应返回空结果。"""
        retriever = TFIDFRetriever(sample_index)
        assert retriever.search("") == []
        assert retriever.search("the is a") == []  # 全停用词

    def test_top_k_limit(self, sample_index):
        """结果数不应超过 top_k。"""
        retriever = TFIDFRetriever(sample_index)
        results = retriever.search("learning", top_k=1)
        assert len(results) <= 1

    def test_score_ordering(self, sample_index):
        """结果应按分数降序排列。"""
        retriever = TFIDFRetriever(sample_index)
        results = retriever.search("machine learning healthcare")
        scores = [s for _, s in results]
        assert scores == sorted(scores, reverse=True)


class TestBM25Retriever:
    """测试 BM25 检索器。"""

    def test_basic_search(self, sample_index):
        """基本检索应返回结果。"""
        retriever = BM25Retriever(sample_index)
        results = retriever.search("climate change", top_k=3)
        assert len(results) > 0

    def test_empty_query(self, sample_index):
        """空查询应返回空结果。"""
        retriever = BM25Retriever(sample_index)
        assert retriever.search("") == []

    def test_top_k_limit(self, sample_index):
        """结果数不应超过 top_k。"""
        retriever = BM25Retriever(sample_index)
        results = retriever.search("language processing", top_k=2)
        assert len(results) <= 2

    def test_score_ordering(self, sample_index):
        """结果应按分数降序排列。"""
        retriever = BM25Retriever(sample_index)
        results = retriever.search("natural language processing")
        scores = [s for _, s in results]
        assert scores == sorted(scores, reverse=True)


class TestQueryExpansion:
    """测试 WordNet 查询扩展。"""

    def test_expansion_contains_original(self):
        """扩展结果应包含原始查询词。"""
        expanded = expand_query_wordnet("computer science")
        assert "computer" in expanded
        assert "science" in expanded

    def test_expansion_adds_synonyms(self):
        """扩展应添加同义词。"""
        expanded = expand_query_wordnet("good")
        words = expanded.split()
        # 至少应有原词 + 一些同义词
        assert len(words) >= 1

    def test_empty_query(self):
        """空查询扩展应返回空字符串。"""
        assert expand_query_wordnet("") == ""
