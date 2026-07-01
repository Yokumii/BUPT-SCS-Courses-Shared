"""
测试 DOI 关联媒体补全模块。
"""

import os
import pickle

from build_media_index import build as build_media_index
from src.media import (
    MediaAssetStore,
    extract_media_assets,
    filter_display_assets,
    group_media_assets,
)


SAMPLE_HTML = """
<html>
  <head>
    <meta property="og:image" content="/assets/cover.png">
    <meta name="citation_journal_title" content="Nature Communications">
  </head>
  <body>
    <figure>
      <img src="/figures/figure1.jpg" alt="Graphical abstract figure">
    </figure>
    <video controls poster="/assets/video-poster.jpg">
      <source src="/media/intro.mp4" type="video/mp4">
    </video>
    <a href="/supplementary/data.zip">Supplementary Material</a>
  </body>
</html>
"""


class TestExtractMediaAssets:
    """测试页面媒体抽取。"""

    def test_extracts_image_video_and_supplementary_assets(self):
        """应从出版社页面中抽取多种媒体对象，并补全绝对地址。"""
        assets = extract_media_assets(
            SAMPLE_HTML,
            page_url="https://www.nature.com/articles/example-paper",
            provider="nature.com",
        )

        assert len(assets) >= 4

        asset_types = {asset["media_type"] for asset in assets}
        assert "image" in asset_types
        assert "video" in asset_types
        assert "supplementary" in asset_types

        asset_urls = {asset["asset_url"] for asset in assets}
        assert "https://www.nature.com/assets/cover.png" in asset_urls
        assert "https://www.nature.com/figures/figure1.jpg" in asset_urls
        assert "https://www.nature.com/media/intro.mp4" in asset_urls
        assert "https://www.nature.com/supplementary/data.zip" in asset_urls


class TestMediaAssetStore:
    """测试媒体缓存读写。"""

    def test_round_trip_groups_assets_by_doc(self, tmp_path):
        """同一论文的多条媒体记录应按 doc_id 聚合读取。"""
        db_path = tmp_path / "media_assets.db"
        store = MediaAssetStore(str(db_path))

        store.replace_for_doc(
            doc_id=7,
            doi="10.1234/example",
            page_url="https://example.org/paper",
            provider="example.org",
            status="ok",
            assets=[
                {
                    "media_type": "image",
                    "title": "Cover image",
                    "asset_url": "https://example.org/cover.png",
                    "thumbnail_url": "https://example.org/cover.png",
                    "caption": "Cover",
                },
                {
                    "media_type": "supplementary",
                    "title": "Supplementary PDF",
                    "asset_url": "https://example.org/supp.pdf",
                    "thumbnail_url": "",
                    "caption": "Appendix",
                },
            ],
        )

        payload = store.get(7)

        assert payload is not None
        assert payload["status"] == "ok"
        assert payload["provider"] == "example.org"
        assert len(payload["assets"]) == 2
        assert payload["assets"][0]["media_type"] == "image"
        assert payload["assets"][1]["media_type"] == "supplementary"


class TestBuildMediaIndex:
    """测试离线媒体补全流程。"""

    def test_build_populates_media_cache_from_doc_meta(self, tmp_path):
        """构建脚本应读取 doc_meta 并写入媒体缓存。"""
        index_dir = tmp_path / "index"
        index_dir.mkdir()

        doc_meta = [
            {
                "doc_id": 0,
                "title": "Example paper",
                "journal": "Nature Communications",
                "doi": "10.1234/example",
                "date": "2024-01-01",
                "authors": "A. Author",
                "filename": "paper.txt",
            }
        ]
        with open(index_dir / "doc_meta.pkl", "wb") as f:
            pickle.dump(doc_meta, f, protocol=pickle.HIGHEST_PROTOCOL)

        def fake_resolver(doi: str, timeout: int = 15):
            assert doi == "10.1234/example"
            return "https://www.nature.com/articles/example-paper", SAMPLE_HTML

        build_media_index(
            index_dir=str(index_dir),
            limit=1,
            sleep_s=0.0,
            resolver=fake_resolver,
        )

        db_path = index_dir / "media_assets.db"
        assert db_path.exists()

        store = MediaAssetStore(str(db_path))
        payload = store.get(0)
        assert payload is not None
        assert payload["status"] == "ok"
        assert len(payload["assets"]) >= 3


class TestGroupMediaAssets:
    """测试展示层分组辅助函数。"""

    def test_groups_assets_by_media_type(self):
        """应按图片、视频、补充材料分组，并忽略未知类型。"""
        grouped = group_media_assets(
            [
                {
                    "media_type": "image",
                    "title": "Image A",
                    "asset_url": "https://example.org/article-image.jpg",
                },
                {
                    "media_type": "video",
                    "title": "Video A",
                    "asset_url": "https://example.org/article-video",
                },
                {
                    "media_type": "supplementary",
                    "title": "Supp A",
                    "asset_url": "https://example.org/doi/suppl/10.1000/example",
                },
                {
                    "media_type": "unknown",
                    "title": "Ignore me",
                    "asset_url": "https://example.org/unknown",
                },
            ]
        )

        assert [asset["title"] for asset in grouped["image"]] == ["Image A"]
        assert [asset["title"] for asset in grouped["video"]] == ["Video A"]
        assert [asset["title"] for asset in grouped["supplementary"]] == ["Supp A"]

    def test_filters_assets_that_are_not_suitable_for_display(self):
        """展示过滤应剔除错误图标、占位图和站点 UI 资源。"""
        assets = [
            {
                "media_type": "image",
                "title": "Nature challenge error",
                "asset_url": "https://www.nature.com/_fs-ch-1T1wmsGaOgGaSxcX/assets/errorIcon.svg",
                "thumbnail_url": "https://www.nature.com/_fs-ch-1T1wmsGaOgGaSxcX/assets/errorIcon.svg",
            },
            {
                "media_type": "image",
                "title": "Search icon",
                "asset_url": "https://example.org/assets/search-icon.svg",
                "thumbnail_url": "https://example.org/assets/search-icon.svg",
            },
            {
                "media_type": "image",
                "title": "Cover",
                "asset_url": "https://example.org/covers/article-cover.png",
                "thumbnail_url": "https://example.org/covers/article-cover.png",
            },
            {
                "media_type": "supplementary",
                "title": "Supplemental Material",
                "asset_url": "https://example.org/doi/suppl/10.1000/example",
                "thumbnail_url": "",
            },
        ]

        filtered = filter_display_assets(assets)

        assert [asset["title"] for asset in filtered] == ["Cover", "Supplemental Material"]
