"""
DOI 关联媒体缓存读取与展示过滤。

该模块只读取本地媒体库，不负责抓取外部网页。媒体对象通过 DOI 与论文事件关联，
用于在信息抽取结果中展示图片、视频和补充材料入口。
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from urllib.parse import urlparse


MEDIA_DB_FILENAME = "media_assets.db"
_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
_BAD_ASSET_MARKERS = (
    "erroricon.svg",
    "/_fs-ch-",
    "data:image",
    "logo",
    " icon",
    "search-",
    "person",
    "close-",
    "hamburger",
    "blank.png",
)


def _normalize_doi(doi: str) -> str:
    """标准化 DOI，去除 URL 前缀和首尾空白。"""
    value = (doi or "").strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.lower().startswith(prefix):
            value = value[len(prefix):]
            break
    return value.strip()


def _has_bad_asset_marker(*values: str) -> bool:
    text = " ".join((value or "").lower() for value in values)
    return any(marker in text for marker in _BAD_ASSET_MARKERS)


def is_displayable_asset(asset: dict) -> bool:
    """判断媒体对象是否适合展示。"""
    media_type = asset.get("media_type", "")
    asset_url = asset.get("asset_url", "")
    thumbnail_url = asset.get("thumbnail_url", "")
    title = asset.get("title", "")
    caption = asset.get("caption", "")
    lower_url = asset_url.lower()

    if not lower_url or _has_bad_asset_marker(asset_url, thumbnail_url, title, caption):
        return False

    if media_type == "image":
        return urlparse(lower_url).path.endswith(_IMAGE_EXTENSIONS)

    if media_type == "video":
        return lower_url.startswith("http") and any(
            token in lower_url for token in ("video", "media", "movie", "multimedia")
        )

    if media_type == "supplementary":
        return lower_url.startswith("http") and any(
            token in lower_url for token in ("supp", "appendix", "data", "file")
        )

    return False


def filter_display_assets(assets: list[dict]) -> list[dict]:
    """过滤出可展示媒体对象。"""
    return [asset for asset in assets if is_displayable_asset(asset)]


def group_media_assets(assets: list[dict]) -> dict[str, list[dict]]:
    """按媒体类型分组。"""
    grouped = {"image": [], "video": [], "supplementary": []}
    for asset in filter_display_assets(assets):
        media_type = asset.get("media_type", "")
        if media_type in grouped:
            grouped[media_type].append(asset)
    return grouped


def summarize_media_assets(assets: list[dict]) -> str:
    """生成 CLI 友好的媒体数量摘要。"""
    grouped = group_media_assets(assets)
    parts = []
    labels = {
        "image": "image",
        "video": "video",
        "supplementary": "supplementary",
    }
    for media_type in ("image", "video", "supplementary"):
        count = len(grouped[media_type])
        if count:
            label = labels[media_type]
            suffix = "" if count == 1 else "s"
            parts.append(f"{count} {label}{suffix}")
    return f"Media: {', '.join(parts)}" if parts else ""


class MediaAssetStore:
    """基于 SQLite 的 DOI 关联媒体缓存读取器。"""

    def __init__(self, db_path: str | os.PathLike):
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)

    def _payload_from_rows(self, rows) -> dict | None:
        if not rows:
            return None

        payload = {
            "doc_id": rows[0]["doc_id"],
            "doi": rows[0]["doi"] or "",
            "page_url": rows[0]["page_url"] or "",
            "provider": rows[0]["provider"] or "",
            "status": rows[0]["status"] or "missing",
            "assets": [],
        }

        assets = []
        for row in rows:
            if row["media_type"] == "status":
                payload["status"] = row["status"] or payload["status"]
                continue
            assets.append(
                {
                    "media_type": row["media_type"] or "",
                    "title": row["title"] or "",
                    "asset_url": row["asset_url"] or "",
                    "thumbnail_url": row["thumbnail_url"] or "",
                    "provider": row["provider"] or "",
                    "caption": row["caption"] or "",
                }
            )

        payload["assets"] = filter_display_assets(assets)
        if payload["assets"]:
            payload["status"] = "ok"
        return payload

    def _fetch(self, where_sql: str, params: tuple) -> dict | None:
        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute(
            f"""
            SELECT doc_id, doi, page_url, media_type, title, asset_url,
                   thumbnail_url, provider, caption, status
            FROM media_assets
            WHERE {where_sql}
            ORDER BY id ASC
            """,
            params,
        ).fetchall()
        return self._payload_from_rows(rows)

    def get_by_doi(self, doi: str, default=None):
        """按 DOI 查询媒体对象。"""
        normalized = _normalize_doi(doi)
        if not normalized:
            return default
        return self._fetch("LOWER(doi) = LOWER(?)", (normalized,)) or default

    def get_by_doc_id(self, doc_id: int, default=None):
        """按本地 doc_id 查询媒体对象，作为 DOI 缺失时的后备。"""
        return self._fetch("doc_id = ?", (doc_id,)) or default

    def get_for_event(self, event, default=None):
        """按事件优先使用 DOI 查询，失败后按 doc_id 查询。"""
        by_doi = self.get_by_doi(getattr(event, "doi", ""), default=None)
        if by_doi is not None:
            return by_doi
        return self.get_by_doc_id(getattr(event, "doc_id", -1), default=default)

    def close(self):
        self.conn.close()


class EmptyMediaAssetStore:
    """媒体库缺失时的空实现。"""

    def get_by_doi(self, doi: str, default=None):
        return default

    def get_by_doc_id(self, doc_id: int, default=None):
        return default

    def get_for_event(self, event, default=None):
        return default

    def close(self):
        return None


def load_media_assets(base_dir: str | os.PathLike = "index/ie"):
    """加载本地媒体库，缺失时返回空存储。"""
    base_path = Path(base_dir)
    candidates = [
        base_path / MEDIA_DB_FILENAME,
        Path("index") / MEDIA_DB_FILENAME,
    ]
    for candidate in candidates:
        if candidate.exists():
            return MediaAssetStore(candidate)
    return EmptyMediaAssetStore()
