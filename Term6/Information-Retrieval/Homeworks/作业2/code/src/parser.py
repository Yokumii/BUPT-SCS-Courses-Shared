"""
文档解析器：解析 data/ 目录下的 .txt 学术论文文件，
提取 title, journal, abstract, body, doi, date, authors 等结构化字段。
"""

import os
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Document:
    """表示一篇解析后的学术论文。"""
    doc_id: int
    filename: str
    title: str = ""
    journal: str = ""
    abstract: str = ""
    body: str = ""
    doi: str = ""
    date: str = ""
    authors: str = ""
    # 预处理后的词项列表（由 preprocessor 填充）
    tokens: list = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """返回标题 + 摘要 + 正文的合并文本，用于索引。"""
        parts = []
        if self.title:
            parts.append(self.title)
        if self.abstract:
            parts.append(self.abstract)
        if self.body:
            parts.append(self.body)
        return "\n".join(parts)

    @property
    def is_substantive(self) -> bool:
        """判断文档是否有实质内容（非封面页/勘误等）。"""
        text = self.full_text
        # 过滤过短的文档
        if len(text) < 200:
            return False
        # 过滤已知的无实质内容标题
        lower_title = self.title.lower()
        skip_patterns = [
            "front matter", "back matter", "cover and front matter",
            "cover and back matter", "table of contents",
            "editorial board", "erratum", "corrigendum",
            "correction to", "retraction", "index to volume",
        ]
        for pat in skip_patterns:
            if pat in lower_title:
                return False
        # 过滤摘要占位文本
        if self.abstract and "an abstract is not available" in self.abstract.lower():
            if len(self.body) < 100:
                return False
        return True


def _extract_field(text: str, label: str) -> Optional[str]:
    """从文本中提取 'Label: value' 格式的字段值（支持多行）。"""
    # 已知的字段标签列表
    known_labels = ["Title", "Journal", "Publication Date", "DOI", "Authors", "Abstract"]
    # 构建终止模式：下一个已知标签或空行
    other_labels = [l for l in known_labels if l != label]
    stop_pattern = r'(?:^(?:' + '|'.join(re.escape(l) for l in other_labels) + r'):\s|\n\n)'

    # 匹配 "Label:" 后面跟随的内容
    pattern = rf'^{re.escape(label)}:\s*(.*?)(?={stop_pattern}|\Z)'
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if match:
        value = match.group(1).strip()
        # 合并多行为单行（去除多余换行）
        value = re.sub(r'\s*\n\s*', ' ', value)
        return value if value else None
    return None


def _extract_abstract(text: str) -> str:
    """提取 Abstract: 标签后的内容。"""
    # 查找 "Abstract:" 标签
    match = re.search(r'^Abstract:\s*\n?', text, re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    # 摘要持续到下一个章节标签（罗马数字编号或 DOI: 或 Authors: 或 References:）
    # 或者连续两个空行
    end_patterns = [
        r'\n(?:I{1,3}V?|VI{0,3}|IX|X)\.\s+',  # 罗马数字章节编号（如 I. Introduction）
        r'\nDOI:\s',
        r'\nAuthors:\s',
        r'\nReferences:\s*\n',
        r'\n\n\n',  # 三个换行（两个空行）
    ]
    end_pos = len(text)
    for pat in end_patterns:
        m = re.search(pat, text[start:])
        if m and (start + m.start()) < end_pos:
            end_pos = start + m.start()
    abstract = text[start:end_pos].strip()
    return abstract


def _extract_body(text: str) -> str:
    """提取正文内容（Abstract 之后到 References/DOI 之前）。"""
    # 查找正文开始位置：第一个罗马数字章节标题
    body_start = re.search(
        r'^(?:I{1,3}V?|VI{0,3}|IX|X)[.\s]+\s*\w',
        text, re.MULTILINE
    )
    if not body_start:
        # 如果没有章节标题，尝试查找 Abstract 之后的内容
        abstract_end = re.search(r'^Abstract:\s*\n?.*?\n\n', text, re.MULTILINE | re.DOTALL)
        if abstract_end:
            body_start_pos = abstract_end.end()
        else:
            return ""
    else:
        body_start_pos = body_start.start()

    # 查找正文结束位置
    end_patterns = [
        r'\nReferences:\s*\n',
        r'\nDOI:\s',
        r'\nAuthors:\s',
    ]
    end_pos = len(text)
    for pat in end_patterns:
        m = re.search(pat, text[body_start_pos:])
        if m and (body_start_pos + m.start()) < end_pos:
            end_pos = body_start_pos + m.start()

    body = text[body_start_pos:end_pos].strip()
    return body


def parse_document(filepath: str, doc_id: int) -> Document:
    """解析单个 .txt 文件并返回 Document 对象。"""
    filename = os.path.basename(filepath)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        with open(filepath, "r", encoding="latin-1") as f:
            text = f.read()

    doc = Document(doc_id=doc_id, filename=filename)

    # 提取结构化字段
    doc.title = _extract_field(text, "Title") or ""
    doc.journal = _extract_field(text, "Journal") or ""
    doc.date = _extract_field(text, "Publication Date") or ""
    doc.doi = _extract_field(text, "DOI") or ""
    doc.authors = _extract_field(text, "Authors") or ""

    # 如果 Title 字段缺失，用第一行作为标题
    if not doc.title:
        first_line = text.split("\n")[0].strip()
        if first_line:
            doc.title = first_line

    # 如果 DOI 缺失，从文件名推断
    if not doc.doi:
        doi_from_name = filename.replace(".txt", "").replace("_", "/")
        doc.doi = doi_from_name

    # 提取摘要
    doc.abstract = _extract_abstract(text)

    # 提取正文
    doc.body = _extract_body(text)

    return doc


def parse_all_documents(data_dir: str, verbose: bool = True) -> list:
    """
    解析 data_dir 下所有 .txt 文件，返回有实质内容的 Document 列表。

    参数:
        data_dir: 数据目录路径
        verbose: 是否显示解析进度

    返回:
        Document 列表（已过滤无实质内容的文档）
    """
    files = sorted([
        f for f in os.listdir(data_dir)
        if f.endswith(".txt")
    ])
    total = len(files)
    documents = []
    skipped = 0

    for i, filename in enumerate(files):
        filepath = os.path.join(data_dir, filename)
        doc = parse_document(filepath, doc_id=i)

        if doc.is_substantive:
            # 重新分配连续 doc_id
            doc.doc_id = len(documents)
            documents.append(doc)
        else:
            skipped += 1

        if verbose and (i + 1) % 2000 == 0:
            print(f"  已解析 {i + 1}/{total} 个文件，"
                  f"有效: {len(documents)}，跳过: {skipped}")

    if verbose:
        print(f"解析完成: 共 {total} 个文件，"
              f"有效文档: {len(documents)}，跳过: {skipped}")

    return documents
