from app_ie import get_event_media_summary
from src.schema import AcademicPaperEvent


class _Store:
    def get_for_event(self, event):
        assert event.doi == "10.123/demo"
        return {
            "assets": [
                {
                    "media_type": "image",
                    "title": "Figure 1",
                    "asset_url": "https://example.org/figure1.jpg",
                    "thumbnail_url": "https://example.org/figure1.jpg",
                }
            ]
        }


def test_get_event_media_summary_returns_counts():
    event = AcademicPaperEvent(doc_id=1, title="Demo", doi="10.123/demo")

    assert get_event_media_summary(event, _Store()) == "Media: 1 image"
