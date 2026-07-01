"""
信息抽取 Web UI (Streamlit)：提供 IE 结果浏览、人工标注、知识图谱可视化。

用法:
    streamlit run app_ie.py
"""

import json
import os
import html as html_module

import streamlit as st

from src.schema import AcademicPaperEvent
from src.ie_evaluator import IEEvaluator
from src.ie_storage import IEStorage
from src.media import group_media_assets, load_media_assets, summarize_media_assets
from src.ui_styles import inject_styles

IE_DIR = "index/ie"
GOLD_PATH = "index/ie/gold_standard.json"


def _esc(value) -> str:
    return html_module.escape(str(value))


def _section(label: str) -> str:
    return f'<div class="ie-section-label">{label}</div>'


def _chips(items, cls: str = "ie-chip") -> str:
    return "".join(f'<span class="{cls}">{_esc(i)}</span>' for i in items)


# ── 数据加载 ─────────────────────────────────

@st.cache_resource
def get_storage() -> IEStorage:
    return IEStorage(IE_DIR)


@st.cache_resource
def get_media_store():
    return load_media_assets(IE_DIR)


@st.cache_data
def load_method_summaries() -> dict[str, dict]:
    return get_storage().list_method_summaries()


def get_evaluator() -> IEEvaluator:
    return IEEvaluator(gold_path=GOLD_PATH)


def get_event_media_summary(event: AcademicPaperEvent, media_store=None) -> str:
    """返回事件关联媒体摘要。"""
    store = media_store or get_media_store()
    media = store.get_for_event(event)
    if not media:
        return ""
    return summarize_media_assets(media.get("assets", []))


def _render_event_media(event: AcademicPaperEvent):
    """渲染 DOI 关联媒体折叠区。"""
    media = get_media_store().get_for_event(event)
    if not media or not media.get("assets"):
        return

    summary = summarize_media_assets(media["assets"])
    with st.expander(f"关联媒体 · {summary.replace('Media: ', '')}", expanded=False):
        grouped = group_media_assets(media["assets"])

        if grouped["image"]:
            st.markdown("**图片**")
            for asset in grouped["image"][:3]:
                image_url = asset.get("thumbnail_url") or asset.get("asset_url")
                if image_url:
                    st.image(
                        image_url,
                        caption=asset.get("title") or asset.get("caption") or "Image",
                        width="stretch",
                    )

        for media_type, title in (("video", "视频"), ("supplementary", "补充材料")):
            if grouped[media_type]:
                st.markdown(f"**{title}**")
                for asset in grouped[media_type][:5]:
                    label = asset.get("title") or asset.get("asset_url")
                    st.markdown(f"- [{label}]({asset.get('asset_url')})")


# ── 页面：结果浏览 ───────────────────────────

def page_browse():
    st.markdown('<h1 class="google-page-title">IE 结果浏览</h1>',
                unsafe_allow_html=True)

    summaries = load_method_summaries()
    if not summaries:
        st.warning(f"未在 `{IE_DIR}/` 找到抽取结果。请先运行 `python build_ie.py`。")
        return

    storage = get_storage()
    # 方法选择
    methods = list(summaries.keys())
    selected_method = st.selectbox("抽取方法", methods)
    method_summary = summaries[selected_method]

    st.info(
        f"共 **{method_summary['total_docs']}** 篇文档 | "
        f"方法: **{selected_method}**"
    )

    # 统计面板
    st.subheader("字段覆盖统计")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Methods", method_summary["has_methods"])
    col2.metric("Datasets", method_summary["has_datasets"])
    col3.metric("Metrics", method_summary["has_metrics"])
    col4.metric("Findings", method_summary["has_findings"])

    # 搜索
    search = st.text_input("搜索（标题 / 方法 / 数据集）", "")

    # 分页
    page_size = st.slider("每页结果数", 5, 50, 10)
    preview_total = method_summary["total_docs"]
    if search:
        _, preview_total = storage.fetch_events_page(
            selected_method,
            offset=0,
            limit=1,
            search=search,
        )
        st.info(f"找到 **{preview_total}** 条匹配")

    total_pages = max(1, (preview_total + page_size - 1) // page_size)
    page = st.number_input("页码", 1, total_pages, 1)
    start = (page - 1) * page_size
    page_events, _ = storage.fetch_events_page(
        selected_method,
        offset=start,
        limit=page_size,
        search=search,
    )

    # 事件卡片展示
    for event in page_events:
        with st.expander(f"📄 [{event.doc_id}] {event.title[:80]}", expanded=False):
            _render_event(event)


def _render_event(event: AcademicPaperEvent):
    """渲染单个事件的详细信息（chips 卡片样式）。"""
    if event.doi:
        st.caption(f"DOI: {event.doi}")

    cols = st.columns(2)

    with cols[0]:
        if event.methods:
            st.markdown(_section("Methods") + _chips(event.methods),
                        unsafe_allow_html=True)
        if event.datasets:
            st.markdown(
                _section("Datasets") + _chips(event.datasets, "ie-chip ie-chip-dataset"),
                unsafe_allow_html=True,
            )
        if event.metrics:
            rows = "".join(
                f'<div class="ie-metric-row"><b>{_esc(m.name)}</b>: {_esc(m.value)}</div>'
                for m in event.metrics
            )
            st.markdown(_section("Metrics") + rows, unsafe_allow_html=True)

    with cols[1]:
        if event.domain_keywords:
            st.markdown(
                _section("Domain Keywords")
                + _chips(event.domain_keywords, "ie-chip ie-chip-keyword"),
                unsafe_allow_html=True,
            )
        if event.affiliations:
            lines = "".join(f'<div class="ie-line">{_esc(a)}</div>'
                            for a in event.affiliations)
            st.markdown(_section("Affiliations") + lines, unsafe_allow_html=True)
        if event.findings:
            findings = "".join(f'<div class="ie-finding">• {_esc(f[:200])}</div>'
                               for f in event.findings)
            st.markdown(_section("Findings") + findings, unsafe_allow_html=True)
        if event.study_characteristics:
            st.markdown(_section("Study Characteristics"), unsafe_allow_html=True)
            st.json(event.study_characteristics)

    _render_event_media(event)


# ── 页面：方法对比 ───────────────────────────

def page_compare():
    st.markdown('<h1 class="google-page-title">抽取方法对比</h1>',
                unsafe_allow_html=True)

    summaries = load_method_summaries()
    if len(summaries) < 2:
        st.warning("至少需要 2 种方法才能对比。请用 `build_ie.py` 生成多种方法的结果。")
        return

    storage = get_storage()
    methods = list(summaries.keys())

    # 总体统计对比
    st.subheader("覆盖统计")
    stats_data = []
    for method, summary in summaries.items():
        total = summary["total_docs"]
        stats_data.append({
            "方法": method,
            "文档数": total,
            "含 Methods": summary["has_methods"],
            "含 Datasets": summary["has_datasets"],
            "含 Metrics": summary["has_metrics"],
            "含 Affiliations": summary["has_affiliations"],
            "含 Findings": summary["has_findings"],
            "平均字段数": f"{summary['avg_fields']:.2f}" if total else "0",
        })
    st.table(stats_data)

    # 单文档对比
    st.subheader("单文档对比")
    doc_id = st.number_input(
        "文档 ID",
        0,
        max(summary["total_docs"] - 1 for summary in summaries.values()),
        0,
    )

    compare_methods = st.multiselect(
        "选择对比方法（建议 2–3 个，避免过挤）",
        methods,
        default=methods[:2],
    )
    if not compare_methods:
        st.info("请至少选择一种方法进行对比。")
    else:
        cols = st.columns(len(compare_methods))
        for col, method in zip(cols, compare_methods):
            with col:
                st.markdown(
                    f'<div class="compare-method-head">{_esc(method)}</div>',
                    unsafe_allow_html=True,
                )
                event = storage.get_event(method, doc_id)
                if event is not None:
                    _render_event(event)
                else:
                    st.warning("该文档无抽取结果")

    # 评价结果对比
    evaluator = get_evaluator()
    if evaluator.gold_data:
        st.subheader("评价结果 (P/R/F1)")
        eval_data = []
        for method in methods:
            result = evaluator.evaluate_batch(
                storage.iter_events(method),
                match_mode="partial",
            )
            if result["evaluated_count"] > 0:
                row = {"方法": method, "已评价数": result["evaluated_count"]}
                for field, scores in result["per_field"].items():
                    row[f"{field} F1"] = f"{scores['f1']:.3f}"
                row["Macro F1"] = f"{result['macro_f1']:.3f}"
                row["Micro F1"] = f"{result['micro_f1']:.3f}"
                eval_data.append(row)
        if eval_data:
            st.table(eval_data)
        else:
            st.info("暂无已评价文档。")
    else:
        st.info("暂无金标准标注。请在「人工标注」页面创建。")


# ── 页面：人工标注 ───────────────────────────

def page_annotate():
    st.markdown('<h1 class="google-page-title">人工标注</h1>',
                unsafe_allow_html=True)

    summaries = load_method_summaries()
    if not summaries:
        st.warning("未找到抽取结果。请先运行 `build_ie.py`。")
        return

    storage = get_storage()
    evaluator = get_evaluator()
    annotated_ids = set(evaluator.gold_data.keys())
    st.info(f"已标注: **{len(annotated_ids)}** 篇文档")

    # 选择方法作为参考
    methods = list(summaries.keys())
    ref_method = st.selectbox("参考方法（自动填充）", methods)

    # 选择文档
    doc_id = st.number_input(
        "待标注文档 ID",
        0,
        summaries[ref_method]["total_docs"] - 1,
        0,
    )

    event = storage.get_event(ref_method, doc_id)
    if event is None:
        st.error("无效的文档 ID")
        return
    st.markdown(f"### {event.title}")

    # 加载已有标注或使用抽取结果作为默认值
    existing = evaluator.gold_data.get(doc_id, {}).get("annotations", {})

    st.markdown("---")
    st.markdown("编辑下列字段，抽取结果已作为建议预填。")

    # 各字段输入
    fields = {}
    for field in ["methods", "datasets", "domain_keywords", "affiliations", "findings"]:
        default = existing.get(field, getattr(event, field, []))
        value = st.text_area(
            f"**{field}**（每行一个）",
            value="\n".join(default),
            height=100,
            key=f"ann_{field}",
        )
        fields[field] = [v.strip() for v in value.strip().split("\n") if v.strip()]

    # metrics
    default_metrics = existing.get("metrics", [
        {"name": m.name, "value": m.value} for m in event.metrics
    ])
    metrics_text = st.text_area(
        "**metrics**（每行一个，格式: name=value）",
        value="\n".join(f"{m['name']}={m['value']}" if isinstance(m, dict) else str(m) for m in default_metrics),
        height=100,
    )
    metrics_list = []
    for line in metrics_text.strip().split("\n"):
        if "=" in line:
            name, value = line.split("=", 1)
            metrics_list.append({"name": name.strip(), "value": value.strip()})
    fields["metrics"] = metrics_list

    # study_characteristics
    default_chars = existing.get("study_characteristics", event.study_characteristics)
    chars_text = st.text_area(
        "**study_characteristics**（JSON）",
        value=json.dumps(default_chars, indent=2),
        height=100,
    )
    try:
        fields["study_characteristics"] = json.loads(chars_text)
    except json.JSONDecodeError:
        fields["study_characteristics"] = default_chars

    # 保存
    if st.button("保存标注", type="primary"):
        evaluator.add_annotation(doc_id, fields)
        st.success(f"已保存 doc_id={doc_id} 的标注")
        st.rerun()


# ── 页面：知识图谱 ───────────────────────────

def page_knowledge_graph():
    st.markdown('<h1 class="google-page-title">知识图谱</h1>',
                unsafe_allow_html=True)

    html_path = os.path.join(IE_DIR, "knowledge_graph.html")
    if not os.path.exists(html_path):
        st.warning(
            "知识图谱尚未生成。请运行 `python build_ie.py --ensemble --knowledge-graph`。"
        )
        return

    # 显示知识图谱
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    st.components.v1.html(html_content, height=750, scrolling=True)

    stats_path = os.path.join(IE_DIR, "knowledge_graph_stats.json")
    if os.path.exists(stats_path):
        with open(stats_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)
        stats = graph_data["stats"]

        col1, col2, col3 = st.columns(3)
        col1.metric("节点", stats["total_nodes"])
        col2.metric("边", stats["total_edges"])
        col3.metric("连通分量", stats["components"])

        # 高频实体
        for etype, top in graph_data.get("top_entities", {}).items():
            if top:
                st.markdown(f"**高频 {etype}:**")
                chart_data = {name: freq for name, freq in top}
                st.bar_chart(chart_data)


# ── 主应用 ───────────────────────────────────

def main():
    st.set_page_config(
        page_title="IREngine V2 - Information Extraction",
        page_icon="🔬",
        layout="wide",
    )

    # Google Search 风格 CSS
    inject_styles()

    st.sidebar.markdown(
        '<div class="sidebar-logo">'
        '<span style="color:#4285f4">I</span>'
        '<span style="color:#ea4335">R</span>'
        '<span style="color:#fbbc05">E</span>'
        '<span style="color:#4285f4">n</span>'
        '<span style="color:#34a853">g</span>'
        '<span style="color:#ea4335">i</span>'
        '<span style="color:#fbbc05">n</span>'
        '<span style="color:#34a853">e</span>'
        '<span style="color:#5f6368;font-size:1rem"> V2</span>'
        '</div>'
        '<div class="sidebar-subtitle">信息抽取系统</div>',
        unsafe_allow_html=True,
    )

    page = st.sidebar.radio(
        "导航",
        ["结果浏览", "方法对比", "人工标注", "知识图谱"],
    )

    if page == "结果浏览":
        page_browse()
    elif page == "方法对比":
        page_compare()
    elif page == "人工标注":
        page_annotate()
    elif page == "知识图谱":
        page_knowledge_graph()


if __name__ == "__main__":
    main()
