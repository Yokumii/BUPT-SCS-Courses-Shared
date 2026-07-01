import sqlite3

from src.media import MediaAssetStore, summarize_media_assets


def _create_media_db(path):
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE media_assets (
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
    rows = [
        (
            10,
            "10.123/demo",
            "https://example.org/paper",
            "image",
            "Figure 1",
            "https://example.org/figure1.jpg",
            "https://example.org/figure1-thumb.jpg",
            "example.org",
            "Main result figure",
            "2026-01-01T00:00:00",
            "ok",
        ),
        (
            10,
            "10.123/demo",
            "https://example.org/paper",
            "image",
            "Blocked icon",
            "https://www.nature.com/_fs-ch-1T1wmsGaOgGaSxcX/assets/errorIcon.svg",
            "",
            "nature.com",
            "error icon",
            "2026-01-01T00:00:00",
            "ok",
        ),
        (
            10,
            "10.123/demo",
            "https://example.org/paper",
            "video",
            "Supplementary video",
            "https://example.org/video-demo",
            "",
            "example.org",
            "",
            "2026-01-01T00:00:00",
            "ok",
        ),
        (
            10,
            "10.123/demo",
            "https://example.org/paper",
            "supplementary",
            "Supplementary data",
            "https://example.org/supplementary-data-file.zip",
            "",
            "example.org",
            "",
            "2026-01-01T00:00:00",
            "ok",
        ),
    ]
    conn.executemany(
        """
        INSERT INTO media_assets (
            doc_id, doi, page_url, media_type, title, asset_url,
            thumbnail_url, provider, caption, fetched_at, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    conn.close()


def test_media_store_filters_displayable_assets_by_doi(tmp_path):
    db_path = tmp_path / "media_assets.db"
    _create_media_db(db_path)

    store = MediaAssetStore(db_path)
    media = store.get_by_doi("10.123/demo")

    assert media is not None
    assert media["doi"] == "10.123/demo"
    assert [asset["media_type"] for asset in media["assets"]] == [
        "image",
        "video",
        "supplementary",
    ]
    assert "errorIcon.svg" not in str(media["assets"])


def test_summarize_media_assets_counts_types(tmp_path):
    db_path = tmp_path / "media_assets.db"
    _create_media_db(db_path)
    store = MediaAssetStore(db_path)

    summary = summarize_media_assets(store.get_by_doi("10.123/demo")["assets"])

    assert summary == "Media: 1 image, 1 video, 1 supplementary"
