import sqlite3

from cli_ie import format_event
from src.media import MediaAssetStore
from src.schema import AcademicPaperEvent


def test_format_event_includes_media_summary(tmp_path):
    db_path = tmp_path / "media_assets.db"
    conn = sqlite3.connect(db_path)
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
    conn.execute(
        """
        INSERT INTO media_assets (
            doc_id, doi, page_url, media_type, title, asset_url,
            thumbnail_url, provider, caption, fetched_at, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            1,
            "10.123/demo",
            "https://example.org/paper",
            "image",
            "Figure 1",
            "https://example.org/figure1.jpg",
            "https://example.org/figure1.jpg",
            "example.org",
            "",
            "2026-01-01T00:00:00",
            "ok",
        ),
    )
    conn.commit()
    conn.close()

    event = AcademicPaperEvent(doc_id=1, title="Demo Paper", doi="10.123/demo")
    output = format_event(event, media_store=MediaAssetStore(db_path))

    assert "DOI:        10.123/demo" in output
    assert "Media:      1 image" in output
