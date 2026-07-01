"""
基于 DOI 离线补全论文关联媒体缓存。
"""

import argparse
import os
import pickle
import time

from src.media import (
    MEDIA_DB_FILENAME,
    MediaAssetStore,
    extract_media_assets,
    provider_from_url,
    resolve_doi_page,
)


def _load_doc_meta(index_dir: str) -> list[dict]:
    meta_path = os.path.join(index_dir, "doc_meta.pkl")
    with open(meta_path, "rb") as f:
        return pickle.load(f)


def build(
    index_dir: str = "index",
    limit: int | None = None,
    start: int = 0,
    sleep_s: float = 0.5,
    refresh: bool = False,
    resolver=resolve_doi_page,
):
    """批量抓取 DOI 对应页面的媒体信息并写入缓存。"""
    doc_meta = _load_doc_meta(index_dir)
    selected = doc_meta[start:]
    if limit is not None:
        selected = selected[:limit]

    db_path = os.path.join(index_dir, MEDIA_DB_FILENAME)
    store = MediaAssetStore(db_path)

    total = len(selected)
    ok_count = 0
    missing_count = 0
    failed_count = 0
    skipped_count = 0

    for i, doc in enumerate(selected, 1):
        doc_id = doc.get("doc_id")
        doi = (doc.get("doi") or "").strip()

        if not refresh and store.has_doc(doc_id):
            skipped_count += 1
            print(f"[{i}/{total}] 跳过 doc_id={doc_id}（已缓存）")
            continue

        if not doi:
            store.replace_for_doc(
                doc_id=doc_id,
                doi="",
                page_url="",
                provider=doc.get("journal", ""),
                status="missing",
                assets=[],
                error_message="Missing DOI",
            )
            missing_count += 1
            print(f"[{i}/{total}] doc_id={doc_id} 缺少 DOI")
            continue

        try:
            page_url, html = resolver(doi)
            provider = provider_from_url(page_url) or doc.get("journal", "")
            assets = extract_media_assets(html, page_url=page_url, provider=provider)
            status = "ok" if assets else "missing"
            store.replace_for_doc(
                doc_id=doc_id,
                doi=doi,
                page_url=page_url,
                provider=provider,
                status=status,
                assets=assets,
                error_message="" if assets else "No media discovered on publisher page",
            )
            if assets:
                ok_count += 1
                print(f"[{i}/{total}] doc_id={doc_id} 抽取 {len(assets)} 条媒体")
            else:
                missing_count += 1
                print(f"[{i}/{total}] doc_id={doc_id} 页面无可用媒体")
        except Exception as e:
            store.replace_for_doc(
                doc_id=doc_id,
                doi=doi,
                page_url="",
                provider=doc.get("journal", ""),
                status="failed",
                assets=[],
                error_message=str(e),
            )
            failed_count += 1
            print(f"[{i}/{total}] doc_id={doc_id} 抽取失败: {e}")

        if sleep_s > 0:
            time.sleep(sleep_s)

    print("=" * 60)
    print(f"媒体缓存已更新: {db_path}")
    print(
        f"成功: {ok_count} | 无媒体: {missing_count} | "
        f"失败: {failed_count} | 跳过: {skipped_count}"
    )
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="构建论文关联媒体缓存")
    parser.add_argument("--index-dir", default="index", help="索引目录")
    parser.add_argument("--limit", type=int, default=None, help="最多处理多少篇论文")
    parser.add_argument("--start", type=int, default=0, help="从第几篇论文开始")
    parser.add_argument("--sleep", type=float, default=0.5, help="请求间隔秒数")
    parser.add_argument("--refresh", action="store_true", help="忽略已有缓存并重抓")
    args = parser.parse_args()

    build(
        index_dir=args.index_dir,
        limit=args.limit,
        start=args.start,
        sleep_s=args.sleep,
        refresh=args.refresh,
    )
