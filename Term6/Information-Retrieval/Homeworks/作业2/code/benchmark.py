"""
自动化性能评估脚本：评估各检索配置的查询响应时间和检索质量（AI 评价替代人工标注）。

评估矩阵: 3 模型 (TF-IDF, BM25, Semantic) × 3 模式 (基础, +查询扩展, +PRF) = 9 种配置

用法:
    python benchmark.py --base-url https://xxx --api-key sk-xxx --ai-model glm-5
    python benchmark.py --skip-ai --output benchmark_latency.json
"""

import argparse
import json
import os
import pickle
import resource
import sys
import time
from datetime import datetime, timezone

from openai import OpenAI

from src.indexer import InvertedIndex
from src.retriever import TFIDFRetriever, BM25Retriever, expand_query_wordnet
from src.semantic import SemanticRetriever
from src.snippet import generate_snippet
from src.storage import load_doc_texts
from src.feedback import pseudo_relevance_feedback

# 内置查询集：基于语料库高频主题提取，覆盖不同学科和查询长度
DEFAULT_QUERIES = [
    # 短查询（1-2 词）：语料库高频主题
    "climate change",
    "social media",
    "machine learning",
    # 中查询（3-5 词）：语料库中常见研究方向
    "covid-19 pandemic mental health",
    "air pollution urban environment",
    "supply chain risk management",
    "carbon emissions economic growth",
    # 长查询 / 特定主题：语料库中的具体研究问题
    "impact of monetary policy on income inequality",
    "artificial intelligence sustainable development goals",
    "human mobility social networks influence",
]


def load_doc_store(index_dir: str) -> dict:
    """加载文档元数据（轻量，不含正文）。"""
    meta_path = os.path.join(index_dir, "doc_meta.pkl")
    with open(meta_path, "rb") as f:
        doc_list = pickle.load(f)
    return {d["doc_id"]: d for d in doc_list}


def get_peak_rss_mb() -> float:
    """获取当前进程峰值 RSS，单位 MB。"""
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return peak_rss / (1024 * 1024)
    return peak_rss / 1024


def timed_load(label: str, loader):
    """记录加载步骤耗时和峰值 RSS 增量。"""
    rss_before = get_peak_rss_mb()
    start = time.perf_counter()
    value = loader()
    elapsed_ms = (time.perf_counter() - start) * 1000
    rss_after = get_peak_rss_mb()
    metric = {
        "label": label,
        "time_ms": round(elapsed_ms, 2),
        "peak_rss_delta_mb": round(max(0.0, rss_after - rss_before), 2),
        "peak_rss_mb": round(rss_after, 2),
    }
    print(
        f"  {label}: {metric['time_ms']:.1f}ms | "
        f"Peak RSS +{metric['peak_rss_delta_mb']:.1f}MB "
        f"(当前峰值 {metric['peak_rss_mb']:.1f}MB)"
    )
    return value, metric


def get_result_info(doc_id: int, doc_store: dict, doc_texts: dict,
                    query: str) -> dict:
    """获取单条检索结果的标题和摘要片段。"""
    doc = doc_store.get(doc_id, {})
    text_entry = doc_texts.get(doc_id, doc)
    abstract = text_entry.get("abstract") or text_entry.get("body", "")
    snippet = generate_snippet(abstract, query, max_sentences=2, max_length=250)
    return {
        "title": doc.get("title", "Untitled"),
        "snippet": snippet,
    }


def ai_judge_relevance(client: OpenAI, ai_model: str, query: str,
                       results_info: list[dict]) -> list[dict]:
    """
    调用 AI 对一组检索结果进行相关性评价。

    发送一条 prompt 包含查询和所有结果，要求 AI 返回 JSON 数组。
    每个结果包含 rank、title、snippet，AI 返回每条的 relevant + reason。
    """
    if not results_info:
        return []

    # 构建检索结果描述
    items_text = ""
    for i, info in enumerate(results_info, 1):
        items_text += (
            f"{i}. 标题: {info['title']}\n"
            f"   摘要片段: {info['snippet']}\n"
        )

    system_prompt = (
        "你是一位学术信息检索评价专家。用户输入了一个学术查询，系统返回了若干篇论文。"
        "请判断每篇论文是否与查询相关。只返回 JSON 数组，不要其他内容。"
    )
    user_prompt = (
        f'查询: "{query}"\n\n'
        f"检索结果:\n{items_text}\n"
        "请以 JSON 数组格式返回你的判断，每条一个对象：\n"
        '[{"rank": 1, "relevant": true, "reason": "论文直接讨论了查询主题"}, ...]\n\n'
        "只返回 JSON，不要其他内容。"
    )

    try:
        resp = client.chat.completions.create(
            model=ai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
        )
        content = resp.choices[0].message.content.strip()
        # 去除可能的 markdown 代码块标记
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        judgments = json.loads(content)
        return judgments
    except Exception as e:
        print(f"  [警告] AI 评价失败: {e}")
        # 降级：全部标记为不相关
        return [
            {"rank": i + 1, "relevant": False, "reason": f"AI 评价失败: {e}"}
            for i in range(len(results_info))
        ]


def precision_at_k(relevance_list: list[bool], k: int) -> float:
    """计算 P@K。"""
    top = relevance_list[:k]
    if not top:
        return 0.0
    return sum(1 for r in top if r) / len(top)


def format_metric(value) -> str:
    """格式化汇总表格中的可选数值。"""
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def average_optional(entries: list[dict], key: str):
    """计算可选指标平均值，没有有效数值时返回 None。"""
    values = [e[key] for e in entries if isinstance(e.get(key), (int, float))]
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def round_optional(value, ndigits: int):
    """保留 None，数值则按指定小数位取整。"""
    if value is None:
        return None
    return round(value, ndigits)


def build_configs() -> list[dict]:
    """构建 9 种评估配置。"""
    models = ["tfidf", "bm25", "semantic"]
    modes = ["base", "qe", "prf"]
    configs = []
    for model in models:
        for mode in modes:
            label_model = {"tfidf": "TF-IDF", "bm25": "BM25", "semantic": "Semantic"}[model]
            label_mode = {"base": "", "qe": " + QE", "prf": " + PRF"}[mode]
            configs.append({
                "model": model,
                "mode": mode,
                "label": f"{label_model}{label_mode}",
            })
    return configs


def init_retrievers(index: InvertedIndex, index_dir: str) -> dict:
    """初始化三种检索器，语义检索失败则返回 None。"""
    retrievers = {
        "tfidf": TFIDFRetriever(index),
        "bm25": BM25Retriever(index),
    }
    try:
        sem = SemanticRetriever(
            index,
            model_path=os.path.join(index_dir, "w2v.model"),
            doc_vectors_path=os.path.join(index_dir, "doc_vectors.npy"),
        )
        sem.load()
        retrievers["semantic"] = sem
    except Exception as e:
        print(f"[警告] 语义检索器加载失败，跳过 Semantic 配置: {e}")
        retrievers["semantic"] = None
    return retrievers


def run_search(retriever, query: str, config: dict, index: InvertedIndex,
               top_k: int) -> tuple[list, float]:
    """执行单次检索，返回 (results, elapsed_ms)。"""
    mode = config["mode"]
    search_query = query

    # 查询扩展
    if mode == "qe":
        search_query = expand_query_wordnet(query)

    start = time.perf_counter()
    if mode == "prf":
        # PRF 模式：先用可能扩展后的查询检索，再做伪相关反馈
        results = pseudo_relevance_feedback(
            retriever, search_query, index, prf_top_n=5, top_k=top_k
        )
    else:
        results = retriever.search(search_query, top_k=top_k)
    elapsed = (time.perf_counter() - start) * 1000
    return results, elapsed


def print_summary_table(summary: dict):
    """在终端输出汇总表格。"""
    header = f"{'配置':<22} | {'Avg P@5':>8} | {'Avg P@10':>9} | {'Avg Time(ms)':>13}"
    sep = "-" * len(header)
    print("\n" + sep)
    print(header)
    print(sep)
    for label, stats in summary.items():
        print(
            f"{label:<22} | {format_metric(stats['avg_P@5']):>8} | "
            f"{format_metric(stats['avg_P@10']):>9} | "
            f"{stats['avg_time_ms']:>13.1f}"
        )
    print(sep)


def main():
    parser = argparse.ArgumentParser(
        description="IREngine 自动化性能评估：3 模型 × 3 模式 = 9 配置"
    )
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL"),
                        help="OpenAI 兼容 API 的 base URL")
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY"),
                        help="API 密钥")
    parser.add_argument("--ai-model", default="glm-5",
                        help="评价模型名称（默认 glm-5）")
    parser.add_argument("--index-dir", default="index",
                        help="索引目录（默认 index）")
    parser.add_argument("--top-k", type=int, default=10,
                        help="每个查询返回结果数（默认 10）")
    parser.add_argument("--output", default="benchmark_results.json",
                        help="输出文件路径（默认 benchmark_results.json）")
    parser.add_argument("--queries", default=None,
                        help="自定义查询文件路径（JSON 数组），覆盖内置查询")
    parser.add_argument("--skip-ai", action="store_true",
                        help="跳过 AI 相关性评价，仅测试加载耗时和检索响应时间")
    args = parser.parse_args()

    if not args.skip_ai and (not args.base_url or not args.api_key):
        parser.error(
            "未启用 --skip-ai 时必须提供 --base-url 和 --api-key，"
            "或设置 OPENAI_BASE_URL 与 OPENAI_API_KEY"
        )

    # 加载查询
    if args.queries:
        with open(args.queries, "r", encoding="utf-8") as f:
            queries = json.load(f)
        print(f"已加载自定义查询: {len(queries)} 条")
    else:
        queries = DEFAULT_QUERIES
        print(f"使用内置查询: {len(queries)} 条")

    # 初始化 OpenAI client
    client = None
    if args.skip_ai:
        print("已启用 --skip-ai：本次仅评估加载耗时与检索响应时间")
    else:
        client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    # 加载索引和文档数据
    print("正在加载索引...")
    load_metrics = []
    index, metric = timed_load("索引加载", lambda: InvertedIndex.load(args.index_dir))
    load_metrics.append(metric)
    doc_store, metric = timed_load("元数据加载", lambda: load_doc_store(args.index_dir))
    load_metrics.append(metric)
    doc_texts, metric = timed_load("正文库打开", lambda: load_doc_texts(args.index_dir))
    load_metrics.append(metric)

    # 初始化检索器
    retrievers, metric = timed_load(
        "检索器初始化", lambda: init_retrievers(index, args.index_dir)
    )
    load_metrics.append(metric)
    configs = build_configs()

    # 运行评估
    all_results = []
    total = len(configs) * len(queries)
    done = 0

    for cfg in configs:
        retriever = retrievers.get(cfg["model"])
        if retriever is None:
            print(f"[跳过] {cfg['label']}（检索器不可用）")
            done += len(queries)
            continue

        print(f"\n{'='*60}")
        print(f"评估配置: {cfg['label']}")
        print(f"{'='*60}")

        for query in queries:
            done += 1
            print(f"  [{done}/{total}] 查询: {query!r}")

            # 执行检索
            results, elapsed = run_search(
                retriever, query, cfg, index, args.top_k
            )

            # 收集结果信息
            results_info = []
            for rank, (doc_id, score) in enumerate(results, 1):
                info = get_result_info(doc_id, doc_store, doc_texts, query)
                results_info.append({
                    "rank": rank,
                    "doc_id": doc_id,
                    "title": info["title"],
                    "snippet": info["snippet"],
                    "score": round(score, 6),
                })

            # AI 评价
            judgments = []
            if not args.skip_ai:
                judgments = ai_judge_relevance(
                    client, args.ai_model, query, results_info
                )

            # 合并评价结果
            relevance_list = []
            for item in results_info:
                rank = item["rank"]
                if args.skip_ai:
                    item["relevant"] = None
                    item["reason"] = "未执行 AI 评价"
                    continue
                # 从 AI 返回中查找对应 rank 的判断
                judgment = next(
                    (j for j in judgments if j.get("rank") == rank), None
                )
                if judgment:
                    item["relevant"] = judgment.get("relevant", False)
                    item["reason"] = judgment.get("reason", "")
                else:
                    item["relevant"] = False
                    item["reason"] = "AI 未返回该条判断"
                relevance_list.append(item["relevant"])

            # 计算 P@5、P@10
            p5 = None if args.skip_ai else precision_at_k(relevance_list, 5)
            p10 = None if args.skip_ai else precision_at_k(relevance_list, 10)

            if args.skip_ai:
                print(f"    时间: {elapsed:.1f}ms | P@5: N/A | P@10: N/A")
            else:
                print(f"    时间: {elapsed:.1f}ms | P@5: {p5:.2f} | P@10: {p10:.2f}")

            all_results.append({
                "config": cfg["label"],
                "query": query,
                "time_ms": round(elapsed, 2),
                "results": results_info,
                "P@5": round_optional(p5, 4),
                "P@10": round_optional(p10, 4),
            })

    # 汇总统计
    summary = {}
    for cfg in configs:
        label = cfg["label"]
        entries = [r for r in all_results if r["config"] == label]
        if not entries:
            continue
        summary[label] = {
            "avg_P@5": average_optional(entries, "P@5"),
            "avg_P@10": average_optional(entries, "P@10"),
            "avg_time_ms": round(sum(e["time_ms"] for e in entries) / len(entries), 2),
        }

    # 输出 JSON
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ai_model": args.ai_model,
        "skip_ai": args.skip_ai,
        "load_metrics": load_metrics,
        "queries": queries,
        "results": all_results,
        "summary": summary,
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存到: {args.output}")

    # 终端汇总表格
    print_summary_table(summary)


if __name__ == "__main__":
    main()
