"""
Streamlit Web UI：搜索界面 + 模型选择 + 结果展示 + 人工评价 + 多模型对比。

用法:
    streamlit run app.py
"""

import base64
import html as html_module
import os
import pickle
import time
from collections import defaultdict

import streamlit as st

from src.indexer import InvertedIndex
from src.retriever import TFIDFRetriever, BM25Retriever, expand_query_wordnet
from src.semantic import SemanticRetriever, semantic_assets_exist
from src.snippet import generate_snippet, highlight_snippet
from src.evaluator import Evaluator
from src.storage import load_doc_texts as _load_doc_texts
from src.wordcloud_gen import generate_wordcloud
from src.media import (
    load_media_assets as _load_media_assets,
    group_media_assets,
)
from src.feedback import (
    RocchioConfig, RocchioTFIDF, RocchioSemantic, RocchioBM25,
    pseudo_relevance_feedback,
)
from src.ui_styles import inject_styles, get_homepage_css, get_results_css


def safe_html(text: str) -> str:
    return html_module.escape(str(text))


def _b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


# ==================== 数据加载（缓存） ====================

@st.cache_resource
def load_index(index_dir: str = "index"):
    """加载倒排索引。"""
    return InvertedIndex.load(index_dir)


@st.cache_resource
def load_doc_store(index_dir: str = "index"):
    """加载文档元数据（轻量，不含正文）。"""
    meta_path = f"{index_dir}/doc_meta.pkl"
    with open(meta_path, "rb") as f:
        doc_list = pickle.load(f)
    return {d["doc_id"]: d for d in doc_list}


@st.cache_resource
def load_doc_texts(index_dir: str = "index"):
    """加载文档正文（SQLite 按需查询 / pkl 降级）。"""
    return _load_doc_texts(index_dir)


@st.cache_resource
def load_media_store(index_dir: str = "index"):
    """加载 DOI 关联媒体缓存。"""
    return _load_media_assets(index_dir)


@st.cache_resource
def load_tfidf_retriever(_index):
    """加载 TF-IDF 检索器（预计算文档向量模长）。"""
    return TFIDFRetriever(_index)


@st.cache_resource
def load_semantic_retriever(_index, index_dir: str = "index"):
    """尝试加载语义检索器（加载失败时返回 None，不崩溃）。"""
    if not semantic_assets_exist(index_dir):
        return None
    try:
        model_path = os.path.join(index_dir, "w2v.model")
        sem = SemanticRetriever(
            _index,
            model_path=model_path,
            doc_vectors_path=os.path.join(index_dir, "doc_vectors.npy"),
        )
        sem.load()
        return sem
    except Exception as e:
        print(f"[警告] 语义检索器加载失败，已跳过: {e}")
        return None


# ==================== 页面配置 ====================

st.set_page_config(
    page_title="IREngine - Academic Paper Search",
    page_icon="🔍",
    layout="wide",
)

# Google Search 风格 CSS
inject_styles()

# ==================== 初始化 ====================

index = load_index()
doc_store = load_doc_store()
doc_texts = load_doc_texts()
media_store = load_media_store()
tfidf_retriever = load_tfidf_retriever(index)
bm25_retriever = BM25Retriever(index)
evaluator = Evaluator()

# 词云缓存
@st.cache_data(show_spinner=False)
def get_wordcloud_bytes(doc_id: int, text: str) -> bytes:
    """缓存词云图片字节流，避免重复生成。"""
    return generate_wordcloud(text)

# 构建可用模型列表
available_models = ["BM25", "TF-IDF"]
if semantic_assets_exist("index"):
    available_models.append("Semantic (Word2Vec)")

# ==================== 页面选择 ====================

page = st.sidebar.selectbox("页面", ["搜索", "模型对比", "评价历史"])

# ==================== 侧边栏 ====================

with st.sidebar:
    st.divider()
    st.caption(f"索引文档: {index.doc_count:,} 篇 | 词项: {len(index.index):,} 个")

    if page == "搜索":
        model_choice = st.radio(
            "检索模型",
            available_models,
            index=0,
        )

        top_k = st.slider("返回结果数", min_value=5, max_value=50, value=10, step=5)

        use_query_expansion = st.checkbox(
            "WordNet 查询扩展",
            value=False,
            help="使用 WordNet 同义词自动扩展查询以提高召回率",
        )

        st.divider()

        # 相关性反馈设置
        st.subheader("相关性反馈")
        feedback_mode = st.radio(
            "反馈模式",
            ["关闭", "伪相关反馈 (PRF)", "交互式反馈"],
            index=0,
            help="Rocchio 相关性反馈：PRF 自动取 Top-N 文档作为相关反馈，交互式需手动标注",
        )

        prf_top_n = 5
        if feedback_mode == "伪相关反馈 (PRF)":
            prf_top_n = st.slider("PRF Top-N", min_value=3, max_value=10, value=5,
                                  help="假设相关的文档数")

        with st.expander("Rocchio 参数"):
            rocchio_alpha = st.number_input("α (原始查询)", value=1.0, min_value=0.0,
                                            max_value=5.0, step=0.1)
            rocchio_beta = st.number_input("β (相关文档)", value=0.75, min_value=0.0,
                                           max_value=5.0, step=0.05)
            rocchio_gamma = st.number_input("γ (不相关文档)", value=0.15, min_value=0.0,
                                            max_value=5.0, step=0.05)

        st.divider()

        # 评价汇总
        st.subheader("评价统计")
        summary = evaluator.get_summary()
        if summary:
            for model, metrics in summary.items():
                st.metric(
                    label=f"{model} (n={metrics['num_queries']})",
                    value=f"P@10: {metrics['avg_P@10']:.2f}",
                    delta=f"P@5: {metrics['avg_P@5']:.2f}",
                )
        else:
            st.info("暂无评价记录。")


def get_retriever(model_name):
    """根据模型名称获取检索器。"""
    if model_name == "TF-IDF":
        return tfidf_retriever
    if model_name == "BM25":
        return bm25_retriever
    if model_name == "Semantic (Word2Vec)":
        semantic_retriever = load_semantic_retriever(index)
        if semantic_retriever:
            return semantic_retriever
    return bm25_retriever


def render_media_section(doc_id: int):
    """渲染单篇论文的 DOI 关联媒体。"""
    payload = media_store.get(doc_id)
    if not payload:
        return

    assets = payload.get("assets", [])
    grouped = group_media_assets(assets)
    page_url = payload.get("page_url", "")
    provider = payload.get("provider", "")

    with st.expander("关联媒体", expanded=False):
        if page_url:
            label = provider or "论文原页"
            st.markdown(f"[查看出版社页面]({page_url})  \n<small>{label}</small>",
                        unsafe_allow_html=True)

        if payload.get("status") != "ok" or not assets:
            message = payload.get("message") or "出版社页面未发现可用媒体。"
            st.caption(message)
            return

        if grouped["image"]:
            st.markdown("**图片预览**")
            images = grouped["image"][:2]
            cols = st.columns(len(images))
            for col, asset in zip(cols, images):
                preview_url = asset.get("thumbnail_url") or asset.get("asset_url")
                if preview_url:
                    col.image(preview_url, width="stretch")
                title = asset.get("title", "Publisher image")[:60]
                col.markdown(f"[{title}]({asset.get('asset_url', preview_url)})")
                caption = asset.get("caption", "")
                if caption:
                    col.caption(caption[:100])

        if grouped["video"]:
            st.markdown("**视频链接**")
            for asset in grouped["video"][:3]:
                title = asset.get("title", "Publisher video")
                st.markdown(f"[{title}]({asset.get('asset_url', '')})")
                caption = asset.get("caption", "")
                if caption:
                    st.caption(caption[:120])

        if grouped["supplementary"]:
            st.markdown("**补充材料**")
            for asset in grouped["supplementary"][:3]:
                title = asset.get("title", "Supplementary material")
                st.markdown(f"[{title}]({asset.get('asset_url', '')})")
                caption = asset.get("caption", "")
                if caption:
                    st.caption(caption[:120])


def render_results(results, query, model_name, enable_eval=True):
    """渲染检索结果列表（Google Search 风格）。"""
    if not results:
        st.warning("未找到相关文档。请尝试其他查询词。")
        return

    eval_key = f"eval_{query}_{model_name}"
    if eval_key not in st.session_state:
        st.session_state[eval_key] = {}

    for rank, (doc_id, score) in enumerate(results, 1):
        doc = doc_store.get(doc_id, {})
        title = doc.get("title", "Untitled")
        journal = doc.get("journal", "N/A")
        date = doc.get("date", "N/A")
        authors = doc.get("authors", "N/A")
        doi = doc.get("doi", "")
        doi_url = f"https://doi.org/{doi}" if doi else ""

        snippet_source = doc_texts.get(doc_id, {}).get("abstract") or \
            doc_texts.get(doc_id, {}).get("body", "")
        snippet = generate_snippet(snippet_source, query, max_sentences=2, max_length=300)
        highlighted = highlight_snippet(snippet, query, html=True)

        with st.container():
            wc_bytes = get_wordcloud_bytes(doc_id, snippet_source[:2000])
            wc_b64 = _b64encode(wc_bytes)

            url_display = f"DOI: {safe_html(doi)}" if doi else safe_html(journal)
            title_html = (
                f'<a class="result-title" href="{safe_html(doi_url)}" target="_blank">'
                f'{safe_html(title)}</a>' if doi_url
                else f'<span class="result-title">{safe_html(title)}</span>'
            )
            st.markdown(
                f'<div class="google-result-card">'
                f'  <img class="result-wordcloud" src="data:image/png;base64,{wc_b64}"'
                f'       alt="word cloud">'
                f'  <div class="result-url">{url_display} — {safe_html(journal)}</div>'
                f'  {title_html}'
                f'  <div class="result-snippet">{highlighted}</div>'
                f'  <div class="result-meta">Score: {score:.4f} | {safe_html(date)} | '
                f'{safe_html(authors[:80])}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            if enable_eval:
                relevant = st.checkbox(
                    "相关",
                    key=f"rel_{eval_key}_{rank}",
                    value=st.session_state[eval_key].get(rank, False),
                    help="标记此结果为相关",
                )
                st.session_state[eval_key][rank] = relevant

            render_media_section(doc_id)

            st.markdown('<hr class="google-divider">', unsafe_allow_html=True)

    if enable_eval:
        if st.button("保存评价记录", type="primary", key=f"save_{eval_key}"):
            judgments = [
                st.session_state[eval_key].get(r, False)
                for r in range(1, len(results) + 1)
            ]
            result_tuples = [
                (doc_id, score, doc_store.get(doc_id, {}).get("title", ""))
                for doc_id, score in results
            ]
            evaluator.add_evaluation(query, model_name, result_tuples, judgments)
            metrics = evaluator.compute_metrics(judgments)
            st.success(
                f"评价已保存! "
                f"**P@5**: {metrics['P@5']:.2f} | "
                f"**P@10**: {metrics['P@10']:.2f} | "
                f"相关文档: {metrics['relevant_count']}/{metrics['total']}"
            )
            st.rerun()


# ==================== 搜索页面 ====================

if page == "搜索":
    # 首页状态由已提交的查询决定，使 Logo 能渲染在搜索框之上（Google 布局）
    is_home = not st.session_state.get("search_query", "")

    if is_home:
        st.markdown(get_homepage_css(), unsafe_allow_html=True)
        st.markdown(
            '<div class="google-logo">'
            '<span style="color:#4285f4">I</span>'
            '<span style="color:#ea4335">R</span>'
            '<span style="color:#fbbc05">E</span>'
            '<span style="color:#4285f4">n</span>'
            '<span style="color:#34a853">g</span>'
            '<span style="color:#ea4335">i</span>'
            '<span style="color:#fbbc05">n</span>'
            '<span style="color:#34a853">e</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    query = st.text_input(
        "输入检索查询",
        placeholder="例如: machine learning healthcare, climate change policy ...",
        key="search_query",
        label_visibility="collapsed",
    )

    if not query:
        st.markdown(
            f'<div class="homepage-stats">已索引 {index.doc_count:,} 篇学术论文</div>',
            unsafe_allow_html=True,
        )
    else:
        # ---------- 结果状态：紧凑头部 + 结果列表 ----------
        st.markdown(get_results_css(), unsafe_allow_html=True)

        # 查询扩展
        search_query = query
        if use_query_expansion:
            search_query = expand_query_wordnet(query)
            if search_query != query:
                st.info(f"扩展查询: {search_query}")

        retriever = get_retriever(model_choice)
        rocchio_config = RocchioConfig(
            alpha=rocchio_alpha, beta=rocchio_beta, gamma=rocchio_gamma
        )

        # PRF 模式
        if feedback_mode == "伪相关反馈 (PRF)":
            start = time.time()
            results = pseudo_relevance_feedback(
                retriever, search_query, index,
                prf_top_n=prf_top_n, top_k=top_k,
                config=rocchio_config,
            )
            elapsed = (time.time() - start) * 1000
            st.markdown(
                f'<div class="result-stats">'
                f'{model_choice} (PRF Top-{prf_top_n}) | '
                f'{len(results)} 条结果 | {elapsed:.1f} ms</div>',
                unsafe_allow_html=True,
            )
            render_results(results, query, model_choice, enable_eval=True)
        else:
            start = time.time()
            results = retriever.search(search_query, top_k=top_k)
            elapsed = (time.time() - start) * 1000
            st.markdown(
                f'<div class="result-stats">'
                f'{model_choice} | {len(results)} 条结果 | {elapsed:.1f} ms</div>',
                unsafe_allow_html=True,
            )
            render_results(results, query, model_choice, enable_eval=True)

            # 交互式反馈按钮
            if feedback_mode == "交互式反馈" and results:
                eval_key = f"eval_{query}_{model_choice}"
                if st.button("Rocchio 反馈检索", type="secondary",
                             key=f"rocchio_{eval_key}"):
                    relevant_ids = set()
                    non_relevant_ids = set()
                    for rank, (doc_id, score) in enumerate(results, 1):
                        if st.session_state.get(f"rel_{eval_key}_{rank}", False):
                            relevant_ids.add(doc_id)
                        else:
                            non_relevant_ids.add(doc_id)

                    if not relevant_ids:
                        st.warning("请先勾选至少一条相关结果，再执行反馈检索。")
                    else:
                        st.divider()
                        st.subheader("反馈结果")
                        st.caption(
                            f"Rocchio 参数: α={rocchio_config.alpha}, "
                            f"β={rocchio_config.beta}, γ={rocchio_config.gamma} | "
                            f"相关: {len(relevant_ids)} 篇, "
                            f"不相关: {len(non_relevant_ids)} 篇"
                        )

                        start_fb = time.time()
                        if isinstance(retriever, TFIDFRetriever):
                            rocchio = RocchioTFIDF(index, rocchio_config)
                            fb_results = rocchio.search_with_feedback(
                                retriever, search_query,
                                relevant_ids, non_relevant_ids, top_k)
                        elif isinstance(retriever, BM25Retriever):
                            rocchio = RocchioBM25(index, rocchio_config)
                            fb_results = rocchio.search_with_feedback(
                                retriever, search_query,
                                relevant_ids, non_relevant_ids, top_k)
                        elif isinstance(retriever, SemanticRetriever):
                            rocchio = RocchioSemantic(retriever, rocchio_config)
                            fb_results = rocchio.search_with_feedback(
                                search_query,
                                relevant_ids, non_relevant_ids, top_k)
                        else:
                            fb_results = results

                        elapsed_fb = (time.time() - start_fb) * 1000
                        st.caption(
                            f"{len(fb_results)} 条反馈结果 | {elapsed_fb:.1f} ms"
                        )
                        render_results(
                            fb_results, query,
                            f"{model_choice} (Rocchio)",
                            enable_eval=False,
                        )

# ==================== 模型对比页面 ====================

elif page == "模型对比":
    st.markdown('<h1 class="google-page-title">多模型对比分析</h1>',
                unsafe_allow_html=True)

    compare_query = st.text_input(
        "输入对比查询",
        placeholder="输入查询以对比不同模型的检索结果...",
        key="compare_query",
    )

    compare_k = st.slider("对比结果数", min_value=5, max_value=20, value=10, step=5,
                           key="compare_k")

    if compare_query:
        # 运行所有可用模型
        all_results = {}
        for model_name in available_models:
            retriever = get_retriever(model_name)
            start = time.time()
            results = retriever.search(compare_query, top_k=compare_k)
            elapsed = (time.time() - start) * 1000
            all_results[model_name] = {
                "results": results,
                "time_ms": elapsed,
            }

        # 结果对比表格
        st.subheader("检索结果对比")

        # 概览指标
        cols = st.columns(len(available_models))
        for col, model_name in zip(cols, available_models):
            data = all_results[model_name]
            with col:
                st.metric(model_name, f"{len(data['results'])} 条结果",
                          f"{data['time_ms']:.1f} ms")

        # 重叠分析
        st.subheader("结果重叠分析")
        if len(available_models) >= 2:
            result_sets = {}
            for model_name in available_models:
                doc_ids = set(doc_id for doc_id, _ in all_results[model_name]["results"])
                result_sets[model_name] = doc_ids

            # 两两对比
            model_list = list(available_models)
            for i in range(len(model_list)):
                for j in range(i + 1, len(model_list)):
                    m1, m2 = model_list[i], model_list[j]
                    overlap = result_sets[m1] & result_sets[m2]
                    total = result_sets[m1] | result_sets[m2]
                    jaccard = len(overlap) / len(total) if total else 0
                    st.caption(
                        f"{m1} vs {m2}: "
                        f"{len(overlap)} 篇重叠 / "
                        f"Jaccard={jaccard:.2f}"
                    )

        # 并排展示每个模型的 Top-5
        st.subheader("Top-5 结果对比")
        cols = st.columns(len(available_models))
        for col, model_name in zip(cols, available_models):
            with col:
                st.markdown(f"**{model_name}**")
                for rank, (doc_id, score) in enumerate(
                    all_results[model_name]["results"][:5], 1
                ):
                    doc = doc_store.get(doc_id, {})
                    title = doc.get("title", "Untitled")
                    st.markdown(f"{rank}. {title[:60]}...  \n"
                                f"<small>Score: {score:.4f}</small>",
                                unsafe_allow_html=True)

# ==================== 评价历史页面 ====================

elif page == "评价历史":
    st.markdown('<h1 class="google-page-title">评价历史记录</h1>',
                unsafe_allow_html=True)

    if not evaluator.evaluations:
        st.info("暂无评价记录。请先在搜索页面中标注结果相关性。")
    else:
        # 汇总统计
        summary = evaluator.get_summary()
        st.subheader("汇总统计")
        cols = st.columns(len(summary))
        for col, (model, metrics) in zip(cols, summary.items()):
            with col:
                st.metric(
                    label=f"{model}",
                    value=f"Avg P@10: {metrics['avg_P@10']:.3f}",
                )
                st.caption(
                    f"Avg P@5: {metrics['avg_P@5']:.3f} | "
                    f"查询数: {metrics['num_queries']}"
                )

        st.divider()

        # 详细记录
        st.subheader("详细评价记录")
        for i, record in enumerate(reversed(evaluator.evaluations)):
            judgments = [r["relevant"] for r in record["results"]]
            metrics = evaluator.compute_metrics(judgments)
            with st.expander(
                f"[{record['model']}] \"{record['query']}\" — "
                f"P@5={metrics['P@5']:.2f}, P@10={metrics['P@10']:.2f}  "
                f"({record['timestamp'][:16]})"
            ):
                for r in record["results"]:
                    badge = (
                        '<span class="badge badge-relevant">相关</span>'
                        if r["relevant"]
                        else '<span class="badge badge-irrelevant">不相关</span>'
                    )
                    st.markdown(
                        f'{badge} <strong>{r["rank"]}.</strong> '
                        f'{safe_html(r["title"][:80])} '
                        f'(score: {r["score"]:.4f})',
                        unsafe_allow_html=True,
                    )
