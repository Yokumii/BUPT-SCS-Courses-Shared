"""
测试 indexer 模块。
"""

import os
import tempfile

import numpy as np

from src.indexer import InvertedIndex


class TestInvertedIndex:
    """测试 InvertedIndex 类。"""

    def test_build(self, sample_index, sample_documents):
        """索引构建后应包含正确的文档数和词项。"""
        assert sample_index.doc_count == len(sample_documents)
        assert len(sample_index.index) > 0
        assert sample_index.avg_doc_length > 0

    def test_doc_lengths(self, sample_index, sample_documents):
        """每篇文档应有对应的长度记录。"""
        for doc in sample_documents:
            assert doc.doc_id < len(sample_index.doc_lengths)
            assert sample_index.doc_lengths[doc.doc_id] > 0

    def test_tf_calculation(self, sample_index):
        """词频应为正整数。"""
        for term in sample_index.index:
            for posting in sample_index.get_postings(term):
                assert posting.tf > 0
                assert isinstance(posting.tf, int)

    def test_df_calculation(self, sample_index):
        """文档频率应在合理范围内。"""
        for term in sample_index.index:
            df = sample_index.get_df(term)
            assert 1 <= df <= sample_index.doc_count

    def test_idf_calculation(self, sample_index):
        """IDF 值应为正数。"""
        for term in sample_index.index:
            idf = sample_index.get_idf(term)
            assert idf > 0

    def test_idf_unknown_term(self, sample_index):
        """未知词项的 IDF 应为 0。"""
        assert sample_index.get_idf("xyznonexistent") == 0.0

    def test_get_postings_unknown(self, sample_index):
        """未知词项的倒排列表应为空。"""
        assert sample_index.get_postings("xyznonexistent") == []

    def test_serialize_deserialize(self, sample_index):
        """序列化和反序列化后索引应一致。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sample_index.save(tmpdir)
            loaded = InvertedIndex.load(tmpdir)

            assert loaded.doc_count == sample_index.doc_count
            assert len(loaded.index) == len(sample_index.index)
            assert loaded.avg_doc_length == sample_index.avg_doc_length

    def test_save_uses_compact_postings_files(self, sample_index):
        """索引保存应产出紧凑数组文件，供在线查询内存映射加载。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sample_index.save(tmpdir)

            assert os.path.exists(os.path.join(tmpdir, "postings_doc_ids.npy"))
            assert os.path.exists(os.path.join(tmpdir, "postings_tfs.npy"))
            assert os.path.exists(os.path.join(tmpdir, "lexicon.pkl"))

    def test_load_uses_array_backed_metadata(self, sample_index):
        """索引加载后应使用数组化元数据，而不是 Python 字典。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sample_index.save(tmpdir)
            loaded = InvertedIndex.load(tmpdir)

            assert isinstance(loaded.doc_lengths, np.ndarray)
            assert isinstance(loaded.doc_norms, np.ndarray)
            assert loaded.doc_lengths.shape[0] == sample_index.doc_count
