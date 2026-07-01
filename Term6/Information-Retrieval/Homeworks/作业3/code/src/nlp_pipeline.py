"""
NLP 管线封装：提供 spaCy 管线的单例加载和文本处理接口。

所有需要 spaCy 的抽取器共享同一个 nlp 实例以节省内存。
"""

import spacy
from spacy.language import Language

# 全局单例
_nlp_instances: dict[tuple[str, tuple[str, ...]], Language] = {}


def get_nlp(
    model_name: str = "en_core_web_sm",
    disable: tuple[str, ...] | list[str] = (),
) -> Language:
    """
    获取 spaCy 语言模型实例（单例模式）。

    Args:
        model_name: spaCy 模型名，默认 en_core_web_sm
        disable: 加载时禁用的 pipeline 组件

    Returns:
        spaCy Language 对象
    """
    disable_tuple = tuple(sorted(disable))
    cache_key = (model_name, disable_tuple)

    if cache_key not in _nlp_instances:
        try:
            _nlp_instances[cache_key] = spacy.load(model_name, disable=list(disable_tuple))
        except OSError:
            print(f"模型 {model_name} 未安装，尝试下载...")
            spacy.cli.download(model_name)
            _nlp_instances[cache_key] = spacy.load(model_name, disable=list(disable_tuple))
    return _nlp_instances[cache_key]


def process_text(
    text: str,
    model_name: str = "en_core_web_sm",
    disable: tuple[str, ...] | list[str] = (),
) -> spacy.tokens.Doc:
    """
    对文本进行完整 NLP 处理。

    Args:
        text: 输入文本
        model_name: spaCy 模型名

    Returns:
        spaCy Doc 对象（含 NER、POS、DEP 标注）
    """
    nlp = get_nlp(model_name, disable=disable)
    # 截断超长文本，避免 spaCy 内存问题
    max_chars = nlp.max_length
    if len(text) > max_chars:
        text = text[:max_chars]
    return nlp(text)


def process_batch(
    texts,
    model_name: str = "en_core_web_sm",
    batch_size: int = 50,
    disable: tuple[str, ...] | list[str] = (),
):
    """
    批量处理文本，利用 spaCy 的 pipe 加速。

    Args:
        texts: 文本列表
        model_name: spaCy 模型名
        batch_size: 批处理大小

    Yields:
        spaCy Doc 对象
    """
    nlp = get_nlp(model_name, disable=disable)
    max_chars = nlp.max_length

    def _truncate_stream():
        for text in texts:
            if len(text) > max_chars:
                yield text[:max_chars]
            else:
                yield text

    yield from nlp.pipe(_truncate_stream(), batch_size=batch_size)
