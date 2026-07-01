"""
测试 preprocessor 模块。
"""

from src.preprocessor import preprocess


class TestPreprocess:
    """测试 preprocess() 函数。"""

    def test_empty_input(self):
        """空输入返回空列表。"""
        assert preprocess("") == []
        assert preprocess(None) == []

    def test_stopword_filtering(self):
        """停用词应被过滤。"""
        tokens = preprocess("the is a an", use_stemming=False)
        assert len(tokens) == 0

    def test_stemming(self):
        """词干提取应正常工作。"""
        tokens = preprocess("running computers")
        # PorterStemmer: running -> run, computers -> comput
        assert "run" in tokens
        assert "comput" in tokens

    def test_no_stemming(self):
        """关闭词干提取时保留原词。"""
        tokens = preprocess("running computers", use_stemming=False)
        assert "running" in tokens
        assert "computers" in tokens

    def test_digit_filtering(self):
        """纯数字应被过滤。"""
        tokens = preprocess("hello 123 world 42")
        # 数字被过滤，hello 和 world 保留
        assert all(not t.isdigit() for t in tokens)
        assert len(tokens) >= 2

    def test_punctuation_removal(self):
        """标点符号应被去除。"""
        tokens = preprocess("hello, world! test.", use_stemming=False)
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens

    def test_short_token_filtering(self):
        """长度小于 2 的 token 应被过滤。"""
        tokens = preprocess("I a am good", use_stemming=False)
        assert "i" not in tokens
        assert "a" not in tokens
