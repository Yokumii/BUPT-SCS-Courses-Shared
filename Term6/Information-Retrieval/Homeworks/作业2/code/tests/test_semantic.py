"""
测试 semantic 模块。
"""

import os
import tempfile

import numpy as np

from src.semantic import SemanticRetriever


class TestSemanticRetrieverStorage:
    """测试语义向量的紧凑持久化格式。"""

    def test_save_persists_matrix_files(self, sample_index):
        """保存时应写出矩阵文件与文档 ID 文件。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = SemanticRetriever(
                sample_index,
                model_path=os.path.join(tmpdir, "w2v.model"),
                doc_vectors_path=os.path.join(tmpdir, "doc_vectors.npy"),
            )
            retriever.doc_ids = np.array([0, 2], dtype=np.int32)
            retriever.doc_matrix = np.array(
                [[1.0, 0.0, 0.0], [0.5, 0.5, 0.0]],
                dtype=np.float32,
            )
            retriever.vector_dim = 3

            retriever.save()

            assert os.path.exists(os.path.join(tmpdir, "doc_vectors.npy"))
            assert os.path.exists(os.path.join(tmpdir, "doc_vector_ids.npy"))

    def test_load_restores_mmap_matrix(self, sample_index):
        """加载时应恢复矩阵与文档 ID，并保持按文档查询能力。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = SemanticRetriever(
                sample_index,
                model_path=os.path.join(tmpdir, "w2v.model"),
                doc_vectors_path=os.path.join(tmpdir, "doc_vectors.npy"),
            )
            writer.doc_ids = np.array([0, 2], dtype=np.int32)
            writer.doc_matrix = np.array(
                [[1.0, 0.0, 0.0], [0.5, 0.5, 0.0]],
                dtype=np.float32,
            )
            writer.vector_dim = 3
            writer.save()

            reader = SemanticRetriever(
                sample_index,
                model_path=os.path.join(tmpdir, "w2v.model"),
                doc_vectors_path=os.path.join(tmpdir, "doc_vectors.npy"),
            )
            reader.load()

            assert isinstance(reader.doc_matrix, np.memmap)
            assert reader.doc_ids.tolist() == [0, 2]
            assert np.allclose(reader.get_doc_vector(2), np.array([0.5, 0.5, 0.0]))
