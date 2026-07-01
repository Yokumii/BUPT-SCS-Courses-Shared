"""
Google Search 风格 CSS 注入模块。
"""

import streamlit as st


def get_base_css() -> str:
    """所有页面通用的 Google Search 风格 CSS。"""
    return """<style>
/* ===== 全局 ===== */
[data-testid="stAppViewContainer"] {
    font-family: 'Google Sans', 'Segoe UI', Roboto, -apple-system,
                 BlinkMacSystemFont, sans-serif;
    color: #202124;
    background: #fff;
}

footer { display: none !important; }

[data-testid="stMainBlockContainer"] {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 100%;
}

/* ===== 搜索栏 ===== */
/* 去掉 Streamlit 默认的输入框容器样式 */
[data-testid="stMainBlockContainer"] [data-testid="stTextInput"] {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    overflow: visible !important;
    padding: 4px 2px !important;
}
[data-testid="stMainBlockContainer"] [data-testid="stTextInput"] > div,
[data-testid="stMainBlockContainer"] [data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stMainBlockContainer"] [data-testid="stTextInput"] [data-baseweb="base-input"] {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    background-color: transparent !important;
    overflow: visible !important;
}
[data-testid="stMainBlockContainer"] input[type="text"] {
    border: 1px solid #dfe1e5;
    border-radius: 24px;
    padding: 10px 20px 10px 44px;
    font-size: 1.05rem;
    height: 46px;
    width: 100% !important;
    background-color: #fff;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%239aa0a6' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: 14px center;
    box-shadow: none;
    transition: box-shadow 0.2s ease;
}
[data-testid="stMainBlockContainer"] input[type="text"]:focus {
    border-color: transparent;
    box-shadow: 0 1px 6px rgba(32,33,36,.28);
    outline: none;
}
/* 隐藏搜索栏 label */
[data-testid="stMainBlockContainer"] [data-testid="stTextInput"]
    label { display: none !important; }

/* ===== 结果卡片 ===== */
.google-result-card {
    margin-bottom: 8px;
    line-height: 1.58;
}
.result-url {
    color: #006621;
    font-size: 0.82rem;
    line-height: 1.4;
    margin-bottom: 2px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.result-title {
    color: #1a0dab;
    font-size: 1.15rem;
    line-height: 1.3;
    text-decoration: none;
    cursor: pointer;
    display: block;
    margin-bottom: 4px;
}
.result-title:hover { text-decoration: underline; }
.result-snippet {
    color: #545454;
    font-size: 0.875rem;
    line-height: 1.58;
}
.result-snippet b { color: #202124; font-weight: 700; }
.result-meta {
    color: #70757a;
    font-size: 0.75rem;
    margin-top: 2px;
}
.result-wordcloud {
    float: left;
    width: 22%;
    max-width: 180px;
    min-width: 100px;
    margin: 0 1em 0.5em 0;
    border-radius: 8px;
}
.google-result-card::after {
    content: "";
    display: table;
    clear: both;
}

/* 分隔线 */
.google-divider {
    border: none;
    border-top: 1px solid #e8eaed;
    margin: 12px 0 20px 0;
}

/* ===== 侧边栏 ===== */
section[data-testid="stSidebar"] {
    background-color: #f8f9fa !important;
}
section[data-testid="stSidebar"] > div:first-child {
    border-right: 1px solid #e0e0e0;
}
[data-testid="stSidebarUserContent"] {
    padding: 16px 14px;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .st-emotion-cache-10o4qdq {
    font-size: 0.82rem;
    color: #5f6368;
    font-weight: 500;
}
[data-testid="stSidebar"] [data-testid="stDivider"] {
    border-top-color: #dadce0;
    margin: 10px 0;
}

/* ===== 按钮 ===== */
.stApp button[kind="primary"] {
    background-color: #4285f4 !important;
    color: #fff !important;
    border-radius: 6px !important;
    border: none !important;
    font-weight: 500 !important;
    padding: 8px 24px !important;
    font-size: 0.875rem !important;
}
.stApp button[kind="primary"]:hover {
    background-color: #3367d6 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.2);
}
.stApp button[kind="secondary"] {
    background-color: #f8f9fa !important;
    color: #3c4043 !important;
    border: 1px solid #f8f9fa !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
}
.stApp button[kind="secondary"]:hover {
    border-color: #dadce0 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.1);
}

/* ===== Alert ===== */
[data-testid="stAlert"] { border-radius: 8px; }

/* ===== Expander ===== */
[data-testid="stExpander"] details {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    margin-bottom: 8px;
    background: #fff;
}
[data-testid="stExpander"] summary {
    padding: 10px 14px;
    font-weight: 500;
    color: #202124;
}
[data-testid="stExpander"] details[open] {
    border-color: #4285f4;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
}

/* ===== Metric 卡片 ===== */
[data-testid="stMetric"] {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 14px 16px;
    border: 1px solid #e0e0e0;
}
[data-testid="stMetricValue"] {
    color: #1a73e8 !important;
    font-size: 1.3rem !important;
    font-weight: 600 !important;
}

/* ===== 页面标题 ===== */
.google-page-title {
    font-size: 1.6rem;
    color: #202124;
    font-weight: 400;
    margin-bottom: 20px;
    padding-bottom: 8px;
    border-bottom: 1px solid #e8eaed;
}

/* ===== Badge ===== */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
    vertical-align: middle;
}
.badge-relevant { background: #e6f4ea; color: #1e8e3e; }
.badge-irrelevant { background: #fce8e6; color: #d93025; }

/* ===== Logo ===== */
.google-logo { text-align: center; margin-bottom: 24px; }
.google-logo span {
    font-size: 4rem;
    font-weight: bold;
    letter-spacing: -2px;
    font-family: 'Google Sans', 'Product Sans', Arial, sans-serif;
}

/* ===== 统计行 ===== */
.result-stats {
    color: #70757a;
    font-size: 0.82rem;
    margin-bottom: 16px;
}

.homepage-stats {
    text-align: center;
    color: #70757a;
    font-size: 0.8rem;
    margin-top: 20px;
}
</style>"""


def get_homepage_css() -> str:
    """首页（无查询）：Logo 偏下，搜索框居中收窄。"""
    return """<style>
.google-logo {
    margin-top: 18vh;
}
[data-testid="stMainBlockContainer"] [data-testid="stTextInput"] {
    max-width: 580px;
    margin-left: auto !important;
    margin-right: auto !important;
}
</style>"""


def get_results_css() -> str:
    """结果页：搜索框紧凑。"""
    return """<style>
[data-testid="stMainBlockContainer"] input[type="text"] {
    font-size: 0.95rem;
    height: 40px;
    border-radius: 20px;
}
</style>"""


def inject_styles():
    st.markdown(get_base_css(), unsafe_allow_html=True)
