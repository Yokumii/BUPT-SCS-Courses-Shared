"""
测试 Streamlit 界面参数兼容性。
"""

from pathlib import Path


def test_app_does_not_use_deprecated_use_container_width_flag():
    """界面代码应使用新版 width 参数，避免 Streamlit 警告。"""
    app_source = Path("app.py").read_text(encoding="utf-8")
    assert "use_container_width=True" not in app_source
    assert "use_container_width=False" not in app_source
