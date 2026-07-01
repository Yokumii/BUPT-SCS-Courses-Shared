"""
Google Search 风格 CSS 注入模块（IE 浏览器版）。

与主分支搜索 UI 共享同一套视觉主题，但保留 wide 布局以容纳
多方法对比的多列视图与表格，故不限制主容器最大宽度。
"""

import streamlit as st


def get_base_css() -> str:
    """IE 浏览器各页面通用的 Google Search 风格 CSS。"""
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
}

/* ===== 搜索/过滤输入框 ===== */
/* 仅美化文本输入（过滤框），保持左对齐并收窄，不撑满 wide 容器 */
[data-testid="stMainBlockContainer"] [data-testid="stTextInput"] {
    max-width: 480px;
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
    font-size: 0.95rem;
    height: 44px;
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
[data-testid="stSidebar"] label {
    font-size: 0.82rem;
    color: #5f6368;
    font-weight: 500;
}
[data-testid="stSidebar"] [data-testid="stDivider"] {
    border-top-color: #dadce0;
    margin: 10px 0;
}

/* ===== 侧边栏 Logo ===== */
.sidebar-logo {
    margin-bottom: 4px;
    line-height: 1.1;
}
.sidebar-logo span {
    font-size: 1.7rem;
    font-weight: bold;
    letter-spacing: -1px;
    font-family: 'Google Sans', 'Product Sans', Arial, sans-serif;
}
.sidebar-subtitle {
    color: #5f6368;
    font-size: 0.78rem;
    margin-bottom: 12px;
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

/* ===== 表格 ===== */
[data-testid="stTable"] table {
    border-radius: 8px;
    overflow: hidden;
    font-size: 0.85rem;
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

/* ===== 抽取结果卡片 ===== */
.ie-section-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #5f6368;
    letter-spacing: 0.3px;
    margin: 10px 0 4px;
}
.ie-chip {
    display: inline-block;
    padding: 2px 10px;
    margin: 2px 4px 2px 0;
    border-radius: 12px;
    font-size: 0.78rem;
    line-height: 1.5;
    background: #e8f0fe;
    color: #1967d2;
    border: 1px solid #d2e3fc;
}
.ie-chip-dataset {
    background: #e6f4ea;
    color: #188038;
    border-color: #ceead6;
}
.ie-chip-keyword {
    background: #f1f3f4;
    color: #5f6368;
    border-color: #e0e0e0;
}
.ie-metric-row {
    font-size: 0.85rem;
    color: #202124;
    padding: 1px 0;
}
.ie-metric-row b { color: #1a73e8; }
.ie-line {
    font-size: 0.85rem;
    color: #3c4043;
    padding: 1px 0;
}
.ie-finding {
    font-size: 0.85rem;
    color: #545454;
    line-height: 1.5;
    padding: 2px 0;
}

/* ===== 方法对比列头 ===== */
.compare-method-head {
    font-size: 0.95rem;
    font-weight: 600;
    color: #fff;
    background: #4285f4;
    border-radius: 6px;
    padding: 6px 12px;
    margin-bottom: 10px;
    text-align: center;
}
</style>"""


def inject_styles():
    st.markdown(get_base_css(), unsafe_allow_html=True)
