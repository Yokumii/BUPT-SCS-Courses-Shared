"""
Snippet 生成器：从文档中提取包含最多查询词的句子作为摘要片段，
并高亮匹配词。
"""

import html as _html
import re

from nltk.tokenize import sent_tokenize
from src.preprocessor import preprocess


def generate_snippet(doc_text: str, query: str, max_sentences: int = 2,
                     max_length: int = 300, query_stems: set = None) -> str:
    """
    从文档文本中提取与查询最相关的句子片段。

    参数:
        doc_text: 文档原文（abstract 或 body）
        query: 用户查询字符串
        max_sentences: 最多返回几个句子
        max_length: snippet 最大字符数
        query_stems: 预处理后的查询词干集合（可选，避免重复预处理）

    返回:
        高亮匹配词的文本片段
    """
    if not doc_text or not query:
        return doc_text[:max_length] if doc_text else ""

    # 使用传入的词干集合或现场计算
    if query_stems is None:
        query_stems = set(preprocess(query))
    if not query_stems:
        return doc_text[:max_length]

    # 分句
    sentences = sent_tokenize(doc_text)
    if not sentences:
        return doc_text[:max_length]

    # 对每个句子打分：包含多少查询词（词干匹配）
    scored = []
    for i, sent in enumerate(sentences):
        sent_stems = set(preprocess(sent))
        overlap = len(query_stems & sent_stems)
        # 加入位置偏好：靠前的句子有微小加分
        score = overlap + (0.001 * (len(sentences) - i))
        scored.append((score, i, sent))

    # 按分数降序排列，取 top 句子
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:max_sentences]
    # 按原文顺序排列
    top.sort(key=lambda x: x[1])

    snippet = " ... ".join(s[2].strip() for s in top)

    # 截断过长的 snippet
    if len(snippet) > max_length:
        snippet = snippet[:max_length - 3] + "..."

    return snippet


def highlight_snippet(snippet: str, query: str, html: bool = False) -> str:
    """
    在 snippet 中高亮查询关键词。

    参数:
        snippet: 文本片段
        query: 用户查询字符串
        html: True 时输出 <b> 标签，False 时输出 **bold**（Streamlit markdown）

    返回:
        带高亮标记的文本
    """
    if not snippet or not query:
        return _html.escape(snippet) if html and snippet else snippet

    # html 模式下先转义文本，防止文档原文中的标签被当作 HTML 注入
    if html:
        snippet = _html.escape(snippet)

    # 提取原始查询词（不做词干提取，直接匹配原词）
    query_words = re.findall(r'\b[a-zA-Z]+\b', query.lower())
    if not query_words:
        return snippet

    # 构建高亮正则（大小写不敏感，匹配完整词）
    pattern = r'\b(' + '|'.join(re.escape(w) for w in query_words) + r')\b'

    def replacer(match):
        word = match.group(0)
        return f"<b>{word}</b>" if html else f"**{word}**"

    return re.sub(pattern, replacer, snippet, flags=re.IGNORECASE)
