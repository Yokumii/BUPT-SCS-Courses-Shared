"""
倒排索引构建器：使用紧凑数组保存倒排表，
降低在线查询阶段的 Python 对象数量与启动内存占用。
"""

import math
import os
import pickle
from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np


_LEXICON_FILE = "lexicon.pkl"
_POSTINGS_DOC_IDS_FILE = "postings_doc_ids.npy"
_POSTINGS_TFS_FILE = "postings_tfs.npy"
_LEGACY_INDEX_FILE = "inverted_index.pkl"


@dataclass
class Posting:
    """倒排列表中的一条记录。"""

    doc_id: int
    tf: int
    # 保留该字段以兼容旧 pickle 中的 Posting 结构。
    positions: list | tuple = field(default_factory=tuple)


class PostingListView:
    """基于数组切片的倒排列表视图。"""

    __slots__ = ("_doc_ids", "_tfs")

    def __init__(self, doc_ids: np.ndarray, tfs: np.ndarray):
        self._doc_ids = doc_ids
        self._tfs = tfs

    def __len__(self) -> int:
        return int(self._doc_ids.shape[0])

    def __iter__(self):
        for doc_id, tf in zip(self._doc_ids, self._tfs):
            yield Posting(doc_id=int(doc_id), tf=int(tf))

    def __getitem__(self, item):
        if isinstance(item, slice):
            return [
                Posting(doc_id=int(doc_id), tf=int(tf))
                for doc_id, tf in zip(self._doc_ids[item], self._tfs[item])
            ]

        return Posting(
            doc_id=int(self._doc_ids[item]),
            tf=int(self._tfs[item]),
        )

    def doc_ids(self) -> np.ndarray:
        """返回当前倒排列表对应的文档 ID 数组视图。"""
        return self._doc_ids

    def tfs(self) -> np.ndarray:
        """返回当前倒排列表对应的词频数组视图。"""
        return self._tfs


class InvertedIndex:
    """
    紧凑倒排索引。

    结构:
        index: {term: (offset, length)}
        postings_doc_ids: 所有倒排项的文档 ID 连续数组
        postings_tfs: 所有倒排项的词频连续数组
        doc_lengths: 每篇文档的长度数组
        doc_norms: 每篇文档的 TF-IDF 模长数组
        idf: {term: IDF 值}
    """

    def __init__(self):
        self.index = {}
        self.postings_doc_ids = np.array([], dtype=np.int32)
        self.postings_tfs = np.array([], dtype=np.int32)
        self.doc_lengths = np.array([], dtype=np.int32)
        self.doc_norms = np.array([], dtype=np.float32)
        self.doc_count = 0
        self.avg_doc_length = 0.0
        self.idf = {}

    def build(self, documents: list, verbose: bool = True):
        """
        从文档列表构建倒排索引。

        参数:
            documents: Document 对象列表（需已完成预处理，doc.tokens 不为空）
            verbose: 是否显示进度
        """
        self.doc_count = len(documents)
        self.doc_lengths = np.zeros(self.doc_count, dtype=np.int32)
        doc_norm_sq = np.zeros(self.doc_count, dtype=np.float64)

        total_length = 0
        temp_index = defaultdict(lambda: defaultdict(int))

        for i, doc in enumerate(documents):
            tokens = doc.tokens
            doc_length = len(tokens)
            self.doc_lengths[doc.doc_id] = doc_length
            total_length += doc_length

            for token in tokens:
                temp_index[token][doc.doc_id] += 1

            if verbose and (i + 1) % 2000 == 0:
                print(f"  索引构建中... {i + 1}/{self.doc_count}")

        self.avg_doc_length = total_length / self.doc_count if self.doc_count > 0 else 0.0

        lexicon = {}
        doc_id_chunks = []
        tf_chunks = []
        offset = 0

        for term, doc_postings in temp_index.items():
            items = sorted(doc_postings.items())
            df = len(items)
            idf = math.log((self.doc_count + 1) / (df + 1)) + 1.0
            self.idf[term] = idf

            doc_ids = np.fromiter((doc_id for doc_id, _ in items), dtype=np.int32, count=df)
            tfs = np.fromiter((tf for _, tf in items), dtype=np.int32, count=df)

            lexicon[term] = (offset, df)
            doc_id_chunks.append(doc_ids)
            tf_chunks.append(tfs)
            offset += df

            tf_weights = 1.0 + np.log(tfs.astype(np.float64))
            doc_norm_sq[doc_ids] += np.square(tf_weights * idf)

        self.index = lexicon
        self.postings_doc_ids = (
            np.concatenate(doc_id_chunks).astype(np.int32, copy=False)
            if doc_id_chunks
            else np.array([], dtype=np.int32)
        )
        self.postings_tfs = (
            np.concatenate(tf_chunks).astype(np.int32, copy=False)
            if tf_chunks
            else np.array([], dtype=np.int32)
        )
        self.doc_norms = np.sqrt(doc_norm_sq).astype(np.float32)

        if verbose:
            print(
                f"索引构建完成: {self.doc_count} 篇文档，"
                f"{len(self.index)} 个词项，"
                f"平均文档长度: {self.avg_doc_length:.1f}"
            )

    def _slice_for_term(self, term: str):
        span = self.index.get(term)
        if span is None:
            return None
        offset, length = span
        return slice(offset, offset + length)

    def get_postings(self, term: str):
        """获取词项的倒排列表视图。"""
        term_slice = self._slice_for_term(term)
        if term_slice is None:
            return []
        return PostingListView(
            self.postings_doc_ids[term_slice],
            self.postings_tfs[term_slice],
        )

    def get_postings_arrays(self, term: str) -> tuple[np.ndarray, np.ndarray]:
        """获取词项的倒排数组视图。"""
        term_slice = self._slice_for_term(term)
        if term_slice is None:
            return (
                np.array([], dtype=np.int32),
                np.array([], dtype=np.int32),
            )
        return (
            self.postings_doc_ids[term_slice],
            self.postings_tfs[term_slice],
        )

    def iter_postings_items(self):
        """遍历所有词项及其倒排列表视图。"""
        for term in self.index:
            yield term, self.get_postings(term)

    def iter_postings_arrays(self):
        """遍历所有词项及其倒排数组视图。"""
        for term in self.index:
            yield term, self.get_postings_arrays(term)

    def get_df(self, term: str) -> int:
        """获取词项的文档频率。"""
        span = self.index.get(term)
        return 0 if span is None else int(span[1])

    def get_idf(self, term: str) -> float:
        """获取词项的 IDF 值。"""
        return self.idf.get(term, 0.0)

    def get_doc_length(self, doc_id: int) -> int:
        """获取文档长度。"""
        if 0 <= doc_id < len(self.doc_lengths):
            return int(self.doc_lengths[doc_id])
        return 0

    def get_doc_norm(self, doc_id: int) -> float:
        """获取文档 TF-IDF 模长。"""
        if 0 <= doc_id < len(self.doc_norms):
            return float(self.doc_norms[doc_id])
        return 0.0

    def _compute_doc_norms(self) -> np.ndarray:
        """根据当前倒排数组重建文档模长。"""
        if self.doc_count == 0:
            return np.array([], dtype=np.float32)

        norm_sq = np.zeros(self.doc_count, dtype=np.float64)
        for term, (doc_ids, tfs) in self.iter_postings_arrays():
            if len(doc_ids) == 0:
                continue
            idf = self.get_idf(term)
            tf_weights = 1.0 + np.log(tfs.astype(np.float64))
            norm_sq[doc_ids] += np.square(tf_weights * idf)
        return np.sqrt(norm_sq).astype(np.float32)

    def save(self, index_dir: str):
        """
        将索引持久化到磁盘。

        保存文件：
        - lexicon.pkl: 词典与倒排偏移
        - postings_doc_ids.npy: 倒排文档 ID 数组
        - postings_tfs.npy: 倒排词频数组
        - doc_metadata.pkl: 文档长度、统计信息、预计算范数
        - idf.pkl: IDF 值
        """
        os.makedirs(index_dir, exist_ok=True)

        with open(os.path.join(index_dir, _LEXICON_FILE), "wb") as f:
            pickle.dump(self.index, f, protocol=pickle.HIGHEST_PROTOCOL)

        np.save(os.path.join(index_dir, _POSTINGS_DOC_IDS_FILE), self.postings_doc_ids)
        np.save(os.path.join(index_dir, _POSTINGS_TFS_FILE), self.postings_tfs)

        metadata = {
            "doc_lengths": self.doc_lengths,
            "doc_norms": self.doc_norms,
            "doc_count": self.doc_count,
            "avg_doc_length": self.avg_doc_length,
        }
        with open(os.path.join(index_dir, "doc_metadata.pkl"), "wb") as f:
            pickle.dump(metadata, f, protocol=pickle.HIGHEST_PROTOCOL)

        with open(os.path.join(index_dir, "idf.pkl"), "wb") as f:
            pickle.dump(self.idf, f, protocol=pickle.HIGHEST_PROTOCOL)

        print(f"索引已保存到 {index_dir}/")

    @staticmethod
    def _normalize_doc_lengths(doc_lengths, doc_count: int) -> np.ndarray:
        """将旧字典格式或新数组格式统一转换为数组。"""
        if isinstance(doc_lengths, np.ndarray):
            return doc_lengths.astype(np.int32, copy=False)

        if isinstance(doc_lengths, dict):
            arr = np.zeros(doc_count, dtype=np.int32)
            for doc_id, length in doc_lengths.items():
                if 0 <= doc_id < doc_count:
                    arr[doc_id] = int(length)
            return arr

        return np.asarray(doc_lengths, dtype=np.int32)

    def _load_compact_postings(self, index_dir: str):
        """加载新格式的紧凑倒排表。"""
        with open(os.path.join(index_dir, _LEXICON_FILE), "rb") as f:
            self.index = pickle.load(f)

        self.postings_doc_ids = np.load(
            os.path.join(index_dir, _POSTINGS_DOC_IDS_FILE),
            mmap_mode="r",
        )
        self.postings_tfs = np.load(
            os.path.join(index_dir, _POSTINGS_TFS_FILE),
            mmap_mode="r",
        )

    def _load_legacy_postings(self, legacy_index: dict):
        """将旧 pickle 倒排表转换为紧凑数组表示。"""
        lexicon = {}
        doc_id_chunks = []
        tf_chunks = []
        offset = 0

        for term, postings in legacy_index.items():
            length = len(postings)
            doc_ids = np.fromiter(
                (int(posting.doc_id) for posting in postings),
                dtype=np.int32,
                count=length,
            )
            tfs = np.fromiter(
                (int(posting.tf) for posting in postings),
                dtype=np.int32,
                count=length,
            )
            lexicon[term] = (offset, length)
            doc_id_chunks.append(doc_ids)
            tf_chunks.append(tfs)
            offset += length

        self.index = lexicon
        self.postings_doc_ids = (
            np.concatenate(doc_id_chunks).astype(np.int32, copy=False)
            if doc_id_chunks
            else np.array([], dtype=np.int32)
        )
        self.postings_tfs = (
            np.concatenate(tf_chunks).astype(np.int32, copy=False)
            if tf_chunks
            else np.array([], dtype=np.int32)
        )

    @classmethod
    def load(cls, index_dir: str) -> "InvertedIndex":
        """从磁盘加载索引。"""
        idx = cls()

        compact_index_path = os.path.join(index_dir, _LEXICON_FILE)
        legacy_index_path = os.path.join(index_dir, _LEGACY_INDEX_FILE)

        if os.path.exists(compact_index_path):
            idx._load_compact_postings(index_dir)
        elif os.path.exists(legacy_index_path):
            with open(legacy_index_path, "rb") as f:
                legacy_index = pickle.load(f)
            idx._load_legacy_postings(legacy_index)
        else:
            raise FileNotFoundError(f"未找到索引文件: {index_dir}")

        with open(os.path.join(index_dir, "doc_metadata.pkl"), "rb") as f:
            metadata = pickle.load(f)
        idx.doc_count = int(metadata["doc_count"])
        idx.avg_doc_length = float(metadata["avg_doc_length"])
        idx.doc_lengths = cls._normalize_doc_lengths(
            metadata["doc_lengths"],
            idx.doc_count,
        )
        doc_norms = metadata.get("doc_norms")
        idx.doc_norms = (
            np.asarray(doc_norms, dtype=np.float32)
            if doc_norms is not None
            else idx._compute_doc_norms()
        )

        with open(os.path.join(index_dir, "idf.pkl"), "rb") as f:
            idx.idf = pickle.load(f)

        if idx.doc_norms.shape[0] != idx.doc_count:
            idx.doc_norms = idx._compute_doc_norms()

        print(f"索引已加载: {idx.doc_count} 篇文档，{len(idx.index)} 个词项")
        return idx
