"""
词云生成器：从文档文本生成词云缩略图。
"""

import io
import matplotlib
matplotlib.use('Agg')  # 无 GUI 后端
import matplotlib.pyplot as plt
from wordcloud import WordCloud


def generate_wordcloud(text: str, max_words: int = 80) -> bytes:
    """
    生成词云图片并返回 PNG 字节流。

    参数:
        text: 文档文本（abstract 或 body）
        max_words: 词云最大词数

    返回:
        PNG 图片字节流
    """
    if not text or len(text.strip()) < 20:
        # 文本过短，返回空白图
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.text(0.5, 0.5, "No content", ha='center', va='center', fontsize=12, color='gray')
        ax.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=80)
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    # 生成词云（冷色调学术风格）
    wc = WordCloud(
        width=400,
        height=300,
        max_words=max_words,
        background_color='white',
        colormap='Blues',  # 冷色调
        relative_scaling=0.5,
        min_font_size=8,
    ).generate(text)

    # 渲染为 PNG
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=80)
    plt.close(fig)
    buf.seek(0)
    return buf.read()
