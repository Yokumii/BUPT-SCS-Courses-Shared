"""
离线信息抽取构建脚本：解析文档并运行多方法抽取管线，保存结果到 JSON。

用法:
    python build_ie.py                          # 运行 L1-L3 全量抽取
    python build_ie.py --methods regex          # 仅运行正则抽取
    python build_ie.py --methods regex spacy    # 运行正则 + spaCy
    python build_ie.py --limit 100              # 仅处理前 100 篇
    python build_ie.py --ensemble               # 运行集成抽取
    python build_ie.py --knowledge-graph        # 构建知识图谱
"""

import argparse
import json
import os
import time
from itertools import islice

from src.parser import iter_documents
from src.ie_storage import IEStorage


DATA_DIR = "data"
OUTPUT_DIR = "index/ie"


def batched(iterable, batch_size: int):
    """将迭代器按固定大小分批。"""
    iterator = iter(iterable)
    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            return
        yield batch


def get_extractor(method: str):
    """按名称获取抽取器实例。"""
    if method == "regex":
        from src.regex_extractor import RegexExtractor
        return RegexExtractor()
    elif method == "spacy":
        from src.spacy_extractor import SpacyExtractor
        return SpacyExtractor()
    elif method == "ner":
        from src.ner_extractor import NERExtractor
        return NERExtractor()
    elif method == "llm":
        from src.llm_extractor import LLMExtractor
        return LLMExtractor()
    else:
        raise ValueError(f"未知方法: {method}")


def run_extraction(
    data_dir: str,
    methods: list[str],
    storage: IEStorage,
    limit: int = 0,
    batch_size: int = 50,
    verbose: bool = True,
):
    """
    运行指定方法的抽取，按批写入 SQLite。
    """
    methods_to_run = [method for method in methods if not storage.has_method(method)]

    if not methods_to_run:
        if verbose:
            print("[抽取] 所有方法结果已存在，跳过")
        return

    extractors = {method: get_extractor(method) for method in methods_to_run}
    storage.conn.execute("BEGIN")
    writers = {
        method: storage.open_writer(method, autocommit=False)
        for method in methods_to_run
    }
    start_times = {method: time.time() for method in methods_to_run}
    processed = 0

    try:
        doc_stream = iter_documents(data_dir, verbose=verbose, limit=limit)
        for batch in batched(doc_stream, batch_size):
            for method in methods_to_run:
                events = extractors[method].extract_batch(batch, verbose=False)
                writers[method].append(events)
            processed += len(batch)
            if verbose:
                print(f"[抽取] 已写入 {processed} 篇文档 × {len(methods_to_run)} 种方法")
    except Exception:
        storage.conn.rollback()
        raise
    else:
        for method, writer in writers.items():
            summary = writer.finish()
            if verbose:
                elapsed = time.time() - start_times[method]
                print(
                    f"[{method}] 完成! 耗时 {elapsed:.1f}s, "
                    f"文档数: {summary.total_docs}, 平均填充字段: {summary.avg_fields:.1f}"
                )
        storage.conn.commit()


def run_ensemble(
    storage: IEStorage,
    methods: list[str],
    strategy: str = "merge",
    verbose: bool = True,
) -> str:
    """运行集成抽取。"""
    method_name = f"ensemble_{strategy}"
    if storage.has_method(method_name):
        if verbose:
            print(f"[集成] 已有缓存: {method_name}")
        return method_name

    if verbose:
        print(f"\n[集成] 合并 {len(methods)} 种方法的结果 (策略: {strategy})...")

    writer = storage.open_writer(method_name)
    batch = []
    iterators = [storage.iter_events(method) for method in methods]
    for method_events in zip(*iterators):
        merged = method_events[0]
        for event in method_events[1:]:
            merged = merged.merge(event)
        merged.extraction_method = f"ensemble({'+'.join(methods)})"
        batch.append(merged)

        if len(batch) >= 100:
            writer.append(batch)
            batch = []

    if batch:
        writer.append(batch)
    summary = writer.finish()

    if verbose:
        print(
            f"[集成] 完成! 文档数: {summary.total_docs}, "
            f"平均填充字段: {summary.avg_fields:.1f}"
        )

    return method_name


def build_knowledge_graph(
    storage: IEStorage,
    method: str,
    output_dir: str,
    min_freq: int = 3,
    verbose: bool = True,
):
    """构建并导出知识图谱。"""
    from src.knowledge_graph import KnowledgeGraph

    if verbose:
        print(f"\n[知识图谱] 从方法 {method} 构建...")

    kg = KnowledgeGraph()
    kg.build_from_event_source(
        lambda: storage.iter_events(method),
        min_entity_freq=min_freq,
    )

    stats = kg.get_stats()
    if verbose:
        print(f"  节点: {stats['total_nodes']}, 边: {stats['total_edges']}, "
              f"连通分量: {stats['components']}")
        for ntype, count in stats["node_types"].items():
            print(f"    {ntype}: {count}")

    # 导出 HTML
    html_path = os.path.join(output_dir, "knowledge_graph.html")
    kg.to_pyvis_html(html_path)
    stats_path = os.path.join(output_dir, "knowledge_graph_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "stats": stats,
                "top_entities": {
                    etype: kg.get_top_entities(etype, top_k=10)
                    for etype in ["method", "dataset", "institution", "domain"]
                },
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    if verbose:
        print(f"  HTML 已保存: {html_path}")

    # 打印高频实体
    if verbose:
        for etype in ["method", "dataset", "institution", "domain"]:
            top = kg.get_top_entities(etype, top_k=10)
            if top:
                print(f"\n  Top {etype}:")
                for name, freq in top:
                    print(f"    {name}: {freq}")


def main():
    parser = argparse.ArgumentParser(description="信息抽取构建脚本")
    parser.add_argument(
        "--methods", nargs="+",
        default=["regex", "spacy", "ner"],
        choices=["regex", "spacy", "ner", "llm"],
        help="抽取方法 (默认: regex spacy ner)",
    )
    parser.add_argument("--limit", type=int, default=0, help="限制处理文档数量 (0=全部)")
    parser.add_argument("--data-dir", default=DATA_DIR, help="数据目录")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="输出目录")
    parser.add_argument("--ensemble", action="store_true", help="运行集成抽取")
    parser.add_argument("--knowledge-graph", action="store_true", help="构建知识图谱")
    parser.add_argument("--kg-min-freq", type=int, default=3, help="知识图谱最小实体频率")
    parser.add_argument("--force", action="store_true", help="忽略缓存重新运行")
    parser.add_argument("--quiet", action="store_true", help="静默模式")
    args = parser.parse_args()

    verbose = not args.quiet

    # 如果 force，删除缓存
    if args.force and os.path.exists(args.output_dir):
        import shutil
        shutil.rmtree(args.output_dir)
        if verbose:
            print(f"已清除缓存: {args.output_dir}")

    # 解析文档
    if verbose:
        print("=" * 60)
        print("信息抽取构建脚本 (IREngine V2)")
        print("=" * 60)
        print(f"\n[解析] 加载文档 ({args.data_dir})...")

    if args.limit > 0 and verbose:
        print(f"  限制处理前 {args.limit} 篇有效文档")

    storage = IEStorage(args.output_dir)

    # 运行抽取
    run_extraction(
        args.data_dir,
        args.methods,
        storage,
        limit=args.limit,
        verbose=verbose,
    )

    # 集成
    ensemble_method = None
    if args.ensemble and len(args.methods) > 1:
        ensemble_method = run_ensemble(
            storage,
            args.methods,
            verbose=verbose,
        )

    # 知识图谱
    if args.knowledge_graph:
        build_knowledge_graph(
            storage,
            ensemble_method or args.methods[-1],
            args.output_dir,
            min_freq=args.kg_min_freq,
            verbose=verbose,
        )

    if verbose:
        print(f"\n{'=' * 60}")
        print("完成!")
        print(f"结果保存在: {args.output_dir}/")


if __name__ == "__main__":
    main()
