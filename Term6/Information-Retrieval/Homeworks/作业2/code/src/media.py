"""
DOI 关联媒体抽取与本地缓存。
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from html.parser import HTMLParser
from typing import Optional
from urllib.parse import quote, urljoin, urlparse
from urllib.request import Request, urlopen


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
    "cart-",
    "deepdyve",
    "user-guides-and-videos",
    "support-videos",
    "cross-product-footer",
    "publishing-supplementary-material",
    "online/supplemental-material",
    "about-society-video",
    "services/authors",
    "services/about",
    "blank.png",
    "ucp-banner",
    "bluesky",
    "rss-",
    "etoc-",
    "informs-icon",
    "partners-",
)
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)


def provider_from_url(url: str) -> str:
    """从页面地址提取来源域名。"""
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def _normalize_url(base_url: str, value: str) -> str:
    value = (value or "").strip()
    if not value or value.startswith(("javascript:", "mailto:", "#")):
        return ""
    return urljoin(base_url, value)


class _PublisherMediaParser(HTMLParser):
    """从出版社页面提取图片、视频和补充材料链接。"""

    def __init__(self, page_url: str, provider: str = ""):
        super().__init__(convert_charrefs=True)
        self.page_url = page_url
        self.provider = provider or provider_from_url(page_url)
        self.assets = []
        self._seen = set()
        self._anchor = None
        self._video_poster = ""

    def _add_asset(
        self,
        media_type: str,
        asset_url: str,
        title: str = "",
        thumbnail_url: str = "",
        caption: str = "",
    ):
        absolute_url = _normalize_url(self.page_url, asset_url)
        if not absolute_url:
            return

        thumbnail = _normalize_url(self.page_url, thumbnail_url) if thumbnail_url else ""
        key = (media_type, absolute_url)
        if key in self._seen:
            return
        self._seen.add(key)

        self.assets.append(
            {
                "media_type": media_type,
                "title": (title or "").strip() or f"Publisher {media_type}",
                "asset_url": absolute_url,
                "thumbnail_url": thumbnail,
                "caption": (caption or "").strip(),
                "provider": self.provider,
            }
        )

    def handle_starttag(self, tag: str, attrs):
        attr_map = {k.lower(): v for k, v in attrs}
        lower_tag = tag.lower()

        if lower_tag == "meta":
            prop = (attr_map.get("property") or attr_map.get("name") or "").lower()
            content = attr_map.get("content") or ""
            if prop in {"og:image", "twitter:image"}:
                self._add_asset(
                    "image",
                    content,
                    title="Publisher cover image",
                    thumbnail_url=content,
                    caption=prop,
                )
            return

        if lower_tag == "img":
            src = attr_map.get("src") or attr_map.get("data-src") or attr_map.get("data-original")
            alt = attr_map.get("alt") or attr_map.get("title") or "Publisher image"
            self._add_asset("image", src or "", title=alt, thumbnail_url=src or "", caption=alt)
            return

        if lower_tag == "video":
            self._video_poster = attr_map.get("poster") or ""
            src = attr_map.get("src") or ""
            if src:
                self._add_asset(
                    "video",
                    src,
                    title="Publisher video",
                    thumbnail_url=self._video_poster,
                    caption=attr_map.get("title") or "",
                )
            return

        if lower_tag == "source":
            src = attr_map.get("src") or ""
            media_kind = (attr_map.get("type") or "").lower()
            if "video" in media_kind or self._video_poster:
                self._add_asset(
                    "video",
                    src,
                    title="Publisher video",
                    thumbnail_url=self._video_poster,
                    caption=media_kind,
                )
            return

        if lower_tag == "a":
            href = attr_map.get("href") or ""
            self._anchor = {
                "href": href,
                "title": attr_map.get("title") or "",
                "text": [],
            }

    def handle_data(self, data: str):
        if self._anchor is not None:
            self._anchor["text"].append(data)

    def handle_endtag(self, tag: str):
        lower_tag = tag.lower()
        if lower_tag == "video":
            self._video_poster = ""
            return

        if lower_tag != "a" or self._anchor is None:
            return

        href = self._anchor["href"]
        title = self._anchor["title"] or " ".join(self._anchor["text"]).strip()
        text = title.lower()
        href_lower = href.lower()

        if any(token in text or token in href_lower for token in ("supplementary", "supplemental")):
            self._add_asset("supplementary", href, title=title or "Supplementary material", caption=title)
        elif any(token in text or token in href_lower for token in ("video", "multimedia", "movie")):
            self._add_asset("video", href, title=title or "Publisher video", caption=title)
        elif any(token in text or token in href_lower for token in ("figure", "image", "graphical abstract")):
            self._add_asset("image", href, title=title or "Publisher image", thumbnail_url=href, caption=title)

        self._anchor = None


def extract_media_assets(html: str, page_url: str, provider: str = "") -> list[dict]:
    """从论文页面 HTML 中抽取媒体对象。"""
    parser = _PublisherMediaParser(page_url=page_url, provider=provider)
    parser.feed(html or "")
    return parser.assets


def _has_bad_asset_marker(*values: str) -> bool:
    text = " ".join((value or "").lower() for value in values)
    return any(marker in text for marker in _BAD_ASSET_MARKERS)


def is_displayable_asset(asset: dict) -> bool:
    """判断媒体对象是否适合在演示界面展示。"""
    media_type = asset.get("media_type", "")
    asset_url = asset.get("asset_url", "")
    thumbnail_url = asset.get("thumbnail_url", "")
    title = asset.get("title", "")
    caption = asset.get("caption", "")
    lower_url = asset_url.lower()

    if not lower_url or _has_bad_asset_marker(asset_url, thumbnail_url, title, caption):
        return False

    if media_type == "image":
        path = urlparse(lower_url).path
        return path.endswith(_IMAGE_EXTENSIONS)

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
    """过滤出适合检索结果页展示的媒体对象。"""
    return [asset for asset in assets if is_displayable_asset(asset)]


def group_media_assets(assets: list[dict]) -> dict[str, list[dict]]:
    """按媒体类型分组，供展示层使用。"""
    grouped = {
        "image": [],
        "video": [],
        "supplementary": [],
    }
    for asset in filter_display_assets(assets):
        media_type = asset.get("media_type", "")
        if media_type in grouped:
            grouped[media_type].append(asset)
    return grouped


def resolve_doi_page(doi: str, timeout: int = 15) -> tuple[str, str]:
    """根据 DOI 解析出版社页面并返回最终地址和 HTML。"""
    if not doi:
        raise ValueError("DOI is required")

    doi_url = f"https://doi.org/{quote(doi, safe='/')}"
    req = Request(doi_url, headers={"User-Agent": _USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        final_url = resp.geturl()
        charset = resp.headers.get_content_charset() or "utf-8"
        html = resp.read().decode(charset, errors="replace")
    return final_url, html


class MediaAssetStore:
    """基于 SQLite 的论文关联媒体缓存。"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._ensure_schema()

    def _ensure_schema(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS media_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER NOT NULL,
                doi TEXT,
                page_url TEXT,
                media_type TEXT NOT NULL,
                title TEXT,
                asset_url TEXT,
                thumbnail_url TEXT,
                provider TEXT,
                caption TEXT,
                fetched_at TEXT,
                status TEXT NOT NULL
            )
            """
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_media_assets_doc_id ON media_assets (doc_id)"
        )
        self.conn.commit()

    def has_doc(self, doc_id: int) -> bool:
        """判断指定论文是否已有缓存记录。"""
        row = self.conn.execute(
            "SELECT 1 FROM media_assets WHERE doc_id = ? LIMIT 1",
            (doc_id,),
        ).fetchone()
        return row is not None

    def replace_for_doc(
        self,
        doc_id: int,
        doi: str,
        page_url: str,
        provider: str,
        status: str,
        assets: list[dict],
        error_message: str = "",
    ):
        """覆盖写入单篇论文的媒体缓存。"""
        fetched_at = datetime.utcnow().isoformat(timespec="seconds")
        self.conn.execute("DELETE FROM media_assets WHERE doc_id = ?", (doc_id,))

        if assets:
            for asset in assets:
                self.conn.execute(
                    """
                    INSERT INTO media_assets (
                        doc_id, doi, page_url, media_type, title, asset_url,
                        thumbnail_url, provider, caption, fetched_at, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        doc_id,
                        doi,
                        page_url,
                        asset.get("media_type", "status"),
                        asset.get("title", ""),
                        asset.get("asset_url", ""),
                        asset.get("thumbnail_url", ""),
                        provider or asset.get("provider", ""),
                        asset.get("caption", ""),
                        fetched_at,
                        status,
                    ),
                )
        else:
            self.conn.execute(
                """
                INSERT INTO media_assets (
                    doc_id, doi, page_url, media_type, title, asset_url,
                    thumbnail_url, provider, caption, fetched_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc_id,
                    doi,
                    page_url,
                    "status",
                    "",
                    "",
                    "",
                    provider,
                    error_message,
                    fetched_at,
                    status,
                ),
            )

        self.conn.commit()

    def get(self, doc_id: int, default=None):
        """按 doc_id 读取聚合后的媒体信息。"""
        rows = self.conn.execute(
            """
            SELECT doi, page_url, media_type, title, asset_url,
                   thumbnail_url, provider, caption, fetched_at, status
            FROM media_assets
            WHERE doc_id = ?
            ORDER BY id ASC
            """,
            (doc_id,),
        ).fetchall()
        if not rows:
            return default

        payload = {
            "doc_id": doc_id,
            "doi": rows[0][0] or "",
            "page_url": rows[0][1] or "",
            "provider": rows[0][6] or "",
            "status": rows[0][9] or "missing",
            "message": "",
            "fetched_at": rows[0][8] or "",
            "assets": [],
        }

        for row in rows:
            media_type = row[2]
            if media_type == "status":
                payload["status"] = row[9] or payload["status"]
                payload["message"] = row[7] or ""
                continue

            payload["status"] = row[9] or "ok"
            payload["assets"].append(
                {
                    "media_type": media_type,
                    "title": row[3] or "",
                    "asset_url": row[4] or "",
                    "thumbnail_url": row[5] or "",
                    "provider": row[6] or "",
                    "caption": row[7] or "",
                }
            )

        if payload["assets"]:
            payload["status"] = "ok"
        return payload

    def close(self):
        self.conn.close()


class _EmptyMediaAssetStore:
    """媒体缓存缺失时的空实现。"""

    def get(self, doc_id, default=None):
        return default

    def has_doc(self, doc_id: int) -> bool:
        return False

    def close(self):
        return None


def load_media_assets(index_dir: str = "index"):
    """加载媒体缓存；若不存在则返回空存储。"""
    db_path = os.path.join(index_dir, MEDIA_DB_FILENAME)
    if os.path.exists(db_path):
        return MediaAssetStore(db_path)
    return _EmptyMediaAssetStore()
