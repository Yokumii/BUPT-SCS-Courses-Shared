"""
检索引擎：实现 TF-IDF VSM 和 BM25 两种检索模型，
以及 WordNet 同义词查询扩展。
"""

import math
from collections import defaultdict

import nltk
import ssl
import numpy as np

ssl._create_default_https_context = ssl._create_unverified_context

from src.preprocessor import preprocess, _stemmer
from src.indexer import InvertedIndex

# 确保 WordNet 数据已下载
for _res in ["wordnet", "omw-1.4"]:
    try:
        nltk.data.find(f"corpora/{_res}")
    except LookupError:
        nltk.download(_res, quiet=True)

from nltk.corpus import wordnet


class TFIDFRetriever:
    """基于 TF-IDF 向量空间模型的检索器。"""

    def __init__(self, index: InvertedIndex):
        self.index = index
        # 优先复用索引构建阶段写入的文档模长，避免启动时全量扫描。
        self._doc_norms = (
            index.doc_norms
            if getattr(index, "doc_norms", None) is not None and len(index.doc_norms) > 0
            else self._compute_doc_norms()
        )

    def _compute_doc_norms(self) -> dict:
        """预计算每篇文档的 TF-IDF 向量模长。"""
        norm_sq = np.zeros(self.index.doc_count, dtype=np.float64)

        for term, (doc_ids, tfs) in self.index.iter_postings_arrays():
            idf = self.index.get_idf(term)
            tf_weights = 1.0 + np.log(tfs.astype(np.float64))
            norm_sq[doc_ids] += np.square(tf_weights * idf)

        return np.sqrt(norm_sq).astype(np.float32)

    def build_query_weights(self, query: str) -> dict:
        """
        将查询字符串转换为 TF-IDF 权重字典。

        参数:
            query: 查询字符串

        返回:
            {term: weight, ...} 权重字典
        """
        query_tokens = preprocess(query)
        if not query_tokens:
            return {}

        query_tf = defaultdict(int)
        for token in query_tokens:
            query_tf[token] += 1

        weights = {}
        for term, tf in query_tf.items():
            idf = self.index.get_idf(term)
            if idf > 0:
                weights[term] = (1 + math.log(tf)) * idf
        return weights

    def search_with_weights(self, query_weights: dict, top_k: int = 10) -> list:
        """
        使用预构建的权重字典检索文档。

        参数:
            query_weights: {term: weight, ...} 查询权重字典
            top_k: 返回结果数量

        返回:
            [(doc_id, score), ...] 按分数降序排列
        """
        if not query_weights:
            return []

        # 查询向量模长
        query_norm = math.sqrt(sum(w * w for w in query_weights.values()))

        # 累积文档分数
        scores = defaultdict(float)
        for term, q_weight in query_weights.items():
            doc_ids, tfs = self.index.get_postings_arrays(term)
            idf = self.index.get_idf(term)
            for doc_id, tf in zip(doc_ids, tfs):
                tf_weight = 1 + math.log(int(tf)) if tf > 0 else 0
                doc_weight = tf_weight * idf
                scores[int(doc_id)] += q_weight * doc_weight

        # 归一化为余弦相似度
        results = []
        for doc_id, dot_product in scores.items():
            doc_norm = float(self._doc_norms[doc_id]) if doc_id < len(self._doc_norms) else 1.0
            if doc_norm > 0 and query_norm > 0:
                cosine_sim = dot_product / (doc_norm * query_norm)
                results.append((doc_id, cosine_sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def search(self, query: str, top_k: int = 10) -> list:
        """
        检索与查询最相关的文档。

        参数:
            query: 查询字符串
            top_k: 返回结果数量

        返回:
            [(doc_id, score), ...] 按分数降序排列
        """
        query_weights = self.build_query_weights(query)
        return self.search_with_weights(query_weights, top_k)


class BM25Retriever:
    """BM25 检索器。"""

    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        self.index = index
        self.k1 = k1
        self.b = b

    def search(self, query: str, top_k: int = 10) -> list:
        """
        使用 BM25 算法检索文档。

        参数:
            query: 查询字符串
            top_k: 返回结果数量

        返回:
            [(doc_id, score), ...] 按分数降序排列
        """
        query_tokens = preprocess(query)
        if not query_tokens:
            return []

        # 查询词频
        query_tf = defaultdict(int)
        for token in query_tokens:
            query_tf[token] += 1

        N = self.index.doc_count
        avgdl = self.index.avg_doc_length

        scores = defaultdict(float)
        for term, qtf in query_tf.items():
            doc_ids, tfs = self.index.get_postings_arrays(term)
            if len(doc_ids) == 0:
                continue

            df = len(doc_ids)
            # BM25 IDF: log((N - df + 0.5) / (df + 0.5) + 1)
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1.0)

            for doc_id, tf in zip(doc_ids, tfs):
                doc_id = int(doc_id)
                tf = int(tf)
                dl = self.index.get_doc_length(doc_id)
                # BM25 TF 归一化
                tf_norm = (tf * (self.k1 + 1)) / (
                    tf + self.k1 * (1 - self.b + self.b * dl / avgdl)
                )
                scores[doc_id] += idf * tf_norm

        results = [(doc_id, score) for doc_id, score in scores.items()]
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


def expand_query_wordnet(query: str, max_synonyms_per_word: int = 2) -> str:
    """
    使用 WordNet 同义词扩展查询。

    对查询中的每个词找到同义词，添加到查询中以提高召回率。

    参数:
        query: 原始查询字符串
        max_synonyms_per_word: 每个词最多添加几个同义词

    返回:
        扩展后的查询字符串
    """
    import re
    words = re.findall(r'\b[a-zA-Z]+\b', query.lower())
    expanded = list(words)

    for word in words:
        synonyms = set()
        for synset in wordnet.synsets(word):
            for lemma in synset.lemmas():
                name = lemma.name().lower().replace("_", " ")
                if name != word and name not in synonyms:
                    synonyms.add(name)
                    if len(synonyms) >= max_synonyms_per_word:
                        break
            if len(synonyms) >= max_synonyms_per_word:
                break
        expanded.extend(synonyms)

    return " ".join(expanded)
