"""
文本预处理器：小写化 → 标点清洗 → 分词 → 停用词过滤 → 词干提取。
"""

import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# 确保 NLTK 数据已下载
for resource in ["punkt", "punkt_tab", "stopwords"]:
    try:
        nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

_stemmer = PorterStemmer()
_stop_words = set(stopwords.words("english"))

# 保留字母和数字的正则（去除标点和特殊字符）
_punct_re = re.compile(r"[^a-z0-9\s]")


def preprocess(text: str, use_stemming: bool = True) -> list:
    """
    对文本进行预处理，返回词项列表。

    管线: 小写化 → 去标点 → 分词 → 过滤短 token → 停用词过滤 → 词干提取

    参数:
        text: 输入文本
        use_stemming: 是否进行词干提取

    返回:
        处理后的 token 列表
    """
    if not text:
        return []

    # 小写化
    text = text.lower()

    # 去除标点和特殊字符
    text = _punct_re.sub(" ", text)

    # 分词
    tokens = word_tokenize(text)

    # 过滤：长度 >= 2 且非纯数字且不是停用词
    tokens = [
        t for t in tokens
        if len(t) >= 2 and not t.isdigit() and t not in _stop_words
    ]

    # 词干提取
    if use_stemming:
        tokens = [_stemmer.stem(t) for t in tokens]

    return tokens


def preprocess_document(doc, use_stemming: bool = True):
    """
    对 Document 对象进行预处理，将结果存入 doc.tokens。

    索引文本 = title(×2 权重提升) + abstract + body
    """
    # 标题给双倍权重（重复一次）
    parts = []
    if doc.title:
        parts.append(doc.title)
        parts.append(doc.title)  # 标题权重提升
    if doc.abstract:
        parts.append(doc.abstract)
    if doc.body:
        parts.append(doc.body)

    text = " ".join(parts)
    doc.tokens = preprocess(text, use_stemming=use_stemming)
    return doc
