"""
共享 fixtures：构造小型测试文档集。
"""

import pytest
from src.parser import Document


@pytest.fixture
def sample_documents():
    """构造小型测试文档集。"""
    docs = [
        Document(
            doc_id=0,
            filename="doc0.txt",
            title="Machine Learning in Healthcare",
            abstract="This paper explores machine learning applications in healthcare systems.",
            body="We propose a novel deep learning approach for medical diagnosis.",
        ),
        Document(
            doc_id=1,
            filename="doc1.txt",
            title="Climate Change and Policy",
            abstract="Climate change poses significant challenges to global policy makers.",
            body="Rising temperatures affect agriculture and water resources worldwide.",
        ),
        Document(
            doc_id=2,
            filename="doc2.txt",
            title="Natural Language Processing",
            abstract="Recent advances in natural language processing have transformed text analysis.",
            body="Transformer models achieve state of the art results on many NLP benchmarks.",
        ),
    ]
    return docs
