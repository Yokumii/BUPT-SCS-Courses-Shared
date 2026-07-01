"""
信息抽取命令行界面 (CLI)：支持单文档抽取、结果查询、评价。

用法:
    python cli_ie.py                          # 交互模式
    python cli_ie.py search --query "transformer"
    python cli_ie.py show --doc-id 42
    python cli_ie.py stats
    python cli_ie.py export --format csv --output results.csv
"""

import argparse
import csv
import json
import os
import sys

from src.schema import AcademicPaperEvent
from src.ie_storage import IEStorage
from src.media import load_media_assets, summarize_media_assets

IE_DIR = "index/ie"


def get_storage() -> IEStorage:
    """获取 IE 结果存储。"""
    if not os.path.exists(IE_DIR):
        print(f"错误: 未找到抽取结果目录 {IE_DIR}，请先运行 python build_ie.py")
        sys.exit(1)

    return IEStorage(IE_DIR)


def resolve_method(storage: IEStorage, method: str = None) -> str:
    """选择实际使用的方法名。"""
    available = storage.list_method_summaries()
    if not available:
        print("错误: 无可用抽取结果")
        sys.exit(1)

    if method and method in available:
        return method

    # 优先选择集成结果，否则选最后一个
    for pref in ["ensemble_merge", "ensemble_vote"]:
        if pref in available:
            return pref

    return list(available.keys())[-1]


def format_event(
    event: AcademicPaperEvent,
    verbose: bool = False,
    media_store=None,
) -> str:
    """格式化单个事件为可读文本。"""
    lines = []
    lines.append(f"{'=' * 70}")
    lines.append(f"Doc #{event.doc_id}: {event.title[:70]}")
    if event.doi:
        lines.append(f"DOI:        {event.doi}")
    lines.append(f"Method: {event.extraction_method}")
    lines.append(f"{'-' * 70}")

    if media_store is not None:
        media = media_store.get_for_event(event)
        if media:
            media_summary = summarize_media_assets(media.get("assets", []))
            if media_summary:
                lines.append(f"  {media_summary.replace('Media:', 'Media:     ')}")

    if event.methods:
        lines.append(f"  Methods:    {', '.join(event.methods[:5])}")
    if event.datasets:
        lines.append(f"  Datasets:   {', '.join(event.datasets[:5])}")
    if event.metrics:
        metric_strs = [f"{m.name}={m.value}" for m in event.metrics[:5]]
        lines.append(f"  Metrics:    {', '.join(metric_strs)}")
    if event.domain_keywords:
        lines.append(f"  Keywords:   {', '.join(event.domain_keywords[:5])}")
    if event.affiliations:
        lines.append(f"  Affiliations: {', '.join(event.affiliations[:3])}")
    if event.findings:
        for f in event.findings[:2]:
            lines.append(f"  Finding:    {f[:100]}")
    if event.study_characteristics:
        chars = ", ".join(f"{k}={v}" for k, v in event.study_characteristics.items())
        lines.append(f"  Study:      {chars}")

    if verbose and event.metrics:
        lines.append(f"  --- Detailed Metrics ---")
        for m in event.metrics:
            lines.append(f"    {m.name} = {m.value}")
            if m.context:
                lines.append(f"      Context: {m.context[:120]}")

    return "\n".join(lines)


def cmd_show(args):
    """显示指定文档的抽取结果。"""
    storage = get_storage()
    media_store = load_media_assets(IE_DIR)
    method = resolve_method(storage, args.method)
    print(f"[Method: {method}]")

    event = storage.get_event(method, args.doc_id)
    total_docs = storage.list_method_summaries()[method]["total_docs"]
    if event is None:
        print(f"错误: doc_id {args.doc_id} 超出范围 (0-{total_docs - 1})")
        return

    print(format_event(event, verbose=True, media_store=media_store))


def cmd_search(args):
    """搜索抽取结果。"""
    storage = get_storage()
    media_store = load_media_assets(IE_DIR)
    method = resolve_method(storage, args.method)
    query = args.query.lower()

    matches = []
    for event in storage.iter_events(method):
        if query in event.title.lower():
            matches.append(event)
        elif any(query in m.lower() for m in event.methods):
            matches.append(event)
        elif any(query in d.lower() for d in event.datasets):
            matches.append(event)
        elif any(query in k.lower() for k in event.domain_keywords):
            matches.append(event)

    print(f"[Method: {method}] Found {len(matches)} matches for '{args.query}'")
    for event in matches[:args.top_k]:
        print(format_event(event, media_store=media_store))


def cmd_stats(args):
    """显示抽取统计。"""
    if not os.path.exists(IE_DIR):
        print(f"未找到结果目录: {IE_DIR}")
        return

    storage = IEStorage(IE_DIR)
    for method, summary in storage.list_method_summaries().items():
        total = summary["total_docs"]
        has_methods = summary["has_methods"]
        has_datasets = summary["has_datasets"]
        has_metrics = summary["has_metrics"]
        has_affiliations = summary["has_affiliations"]
        has_findings = summary["has_findings"]
        has_chars = summary["has_study_characteristics"]
        avg_fields = summary["avg_fields"]

        print(f"\n{'=' * 50}")
        print(f"Method: {method}  ({total} documents)")
        print(f"{'=' * 50}")
        print(f"  Methods:          {has_methods:>6} ({has_methods / total * 100:.1f}%)")
        print(f"  Datasets:         {has_datasets:>6} ({has_datasets / total * 100:.1f}%)")
        print(f"  Metrics:          {has_metrics:>6} ({has_metrics / total * 100:.1f}%)")
        print(f"  Affiliations:     {has_affiliations:>6} ({has_affiliations / total * 100:.1f}%)")
        print(f"  Findings:         {has_findings:>6} ({has_findings / total * 100:.1f}%)")
        print(f"  Study Chars:      {has_chars:>6} ({has_chars / total * 100:.1f}%)")
        print(f"  Avg filled fields: {avg_fields:.2f} / 7")


def cmd_export(args):
    """导出抽取结果。"""
    storage = get_storage()
    method = resolve_method(storage, args.method)
    events = storage.iter_events(method)
    total_docs = storage.list_method_summaries()[method]["total_docs"]

    if args.format == "json":
        data = [e.to_dict() for e in events]
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    elif args.format == "csv":
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "doc_id", "title", "methods", "datasets", "metrics",
                "domain_keywords", "affiliations", "findings", "study_characteristics",
            ])
            for e in storage.iter_events(method):
                metrics_str = "; ".join(f"{m.name}={m.value}" for m in e.metrics)
                writer.writerow([
                    e.doc_id, e.title,
                    "; ".join(e.methods), "; ".join(e.datasets), metrics_str,
                    "; ".join(e.domain_keywords), "; ".join(e.affiliations),
                    "; ".join(e.findings), json.dumps(e.study_characteristics),
                ])

    print(f"[{method}] Exported {total_docs} events to {args.output}")


def cmd_interactive(args):
    """交互模式。"""
    storage = get_storage()
    media_store = load_media_assets(IE_DIR)
    method = resolve_method(storage, args.method)
    events = list(storage.iter_events(method))
    print(f"IREngine V2 - Information Extraction CLI")
    print(f"Method: {method}, Documents: {len(events)}")
    print(f"Commands: show <id>, search <query>, stats, field <name>, quit")
    print()

    while True:
        try:
            raw = input("ie> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not raw:
            continue

        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd in ("quit", "exit", "q"):
            print("Bye!")
            break
        elif cmd == "show":
            try:
                doc_id = int(arg)
                if 0 <= doc_id < len(events):
                    print(format_event(events[doc_id], verbose=True, media_store=media_store))
                else:
                    print(f"doc_id 范围: 0-{len(events) - 1}")
            except ValueError:
                print("用法: show <doc_id>")
        elif cmd == "search":
            if not arg:
                print("用法: search <query>")
                continue
            q = arg.lower()
            matches = [
                e for e in events
                if q in e.title.lower()
                or any(q in m.lower() for m in e.methods)
                or any(q in d.lower() for d in e.datasets)
            ]
            print(f"Found {len(matches)} matches")
            for e in matches[:10]:
                print(format_event(e, media_store=media_store))
        elif cmd == "stats":
            total = len(events)
            print(f"Documents: {total}")
            for field in ["methods", "datasets", "metrics", "domain_keywords", "affiliations", "findings"]:
                has = sum(1 for e in events if getattr(e, field, []))
                print(f"  {field}: {has} ({has / total * 100:.1f}%)")
        elif cmd == "field":
            if not arg:
                print("用法: field <methods|datasets|metrics|...>")
                continue
            # 统计某字段的高频值
            from collections import Counter
            counter = Counter()
            for e in events:
                vals = getattr(e, arg, [])
                if isinstance(vals, list):
                    for v in vals:
                        key = v.lower() if isinstance(v, str) else str(v)
                        counter[key] += 1
            print(f"Top {arg}:")
            for val, freq in counter.most_common(20):
                print(f"  {val}: {freq}")
        else:
            print(f"未知命令: {cmd}")


def main():
    parser = argparse.ArgumentParser(description="IREngine V2 - Information Extraction CLI")
    parser.add_argument("--method", default=None, help="指定方法 (默认: 自动选择)")
    subparsers = parser.add_subparsers(dest="command")

    # show
    p_show = subparsers.add_parser("show", help="显示指定文档的抽取结果")
    p_show.add_argument("--doc-id", type=int, required=True)
    p_show.set_defaults(func=cmd_show)

    # search
    p_search = subparsers.add_parser("search", help="搜索抽取结果")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--top-k", type=int, default=10)
    p_search.set_defaults(func=cmd_search)

    # stats
    p_stats = subparsers.add_parser("stats", help="显示统计信息")
    p_stats.set_defaults(func=cmd_stats)

    # export
    p_export = subparsers.add_parser("export", help="导出抽取结果")
    p_export.add_argument("--format", choices=["json", "csv"], default="json")
    p_export.add_argument("--output", default="ie_results.json")
    p_export.set_defaults(func=cmd_export)

    args = parser.parse_args()

    if args.command and hasattr(args, "func"):
        args.func(args)
    else:
        cmd_interactive(args)


if __name__ == "__main__":
    main()
