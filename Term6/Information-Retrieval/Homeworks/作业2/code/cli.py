"""
命令行检索界面：输入查询 → 显示 Top-K 结果。

用法:
    python cli.py [--index-dir INDEX_DIR] [--model {tfidf,bm25,semantic}] [--top-k K]
                  [--query-expansion] [--eval]
"""

import argparse
import json
import os
import pickle
import time

from src.indexer import InvertedIndex
from src.retriever import TFIDFRetriever, BM25Retriever, expand_query_wordnet
from src.snippet import generate_snippet
from src.storage import load_doc_texts
from src.evaluator import Evaluator
from src.feedback import (
    RocchioConfig, RocchioTFIDF, RocchioSemantic, RocchioBM25,
    pseudo_relevance_feedback,
)


def load_doc_store(index_dir: str) -> dict:
    """加载文档元数据（轻量，不含正文）。"""
    meta_path = os.path.join(index_dir, "doc_meta.pkl")
    with open(meta_path, "rb") as f:
        doc_list = pickle.load(f)
    return {d["doc_id"]: d for d in doc_list}


def format_result(rank: int, doc: dict, score: float, query: str,
                   doc_texts: dict = None) -> str:
    """格式化单条检索结果。"""
    text_entry = (doc_texts or {}).get(doc.get("doc_id"), doc)
    snippet_text = generate_snippet(
        text_entry.get("abstract") or text_entry.get("body", ""),
        query,
        max_sentences=2,
        max_length=250,
    )
    doi = doc.get("doi", "")
    doi_url = f"https://doi.org/{doi}" if doi else ""

    lines = [
        f"  [{rank}] (score: {score:.4f}) {doc.get('title', 'Untitled')}",
        f"      Journal: {doc.get('journal', 'N/A')}",
        f"      Date: {doc.get('date', 'N/A')}  |  Authors: {doc.get('authors', 'N/A')[:80]}",
        f"      DOI: {doi_url}",
        f"      Snippet: {snippet_text[:200]}",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="IREngine CLI")
    parser.add_argument("--index-dir", default="index", help="索引目录")
    parser.add_argument("--model", choices=["tfidf", "bm25", "semantic"], default="bm25",
                        help="检索模型")
    parser.add_argument("--top-k", type=int, default=10, help="返回结果数")
    parser.add_argument("--query-expansion", "-qe", action="store_true",
                        help="启用 WordNet 查询扩展")
    parser.add_argument("--eval", action="store_true",
                        help="启用人工评价模式（交互式标注相关性）")
    parser.add_argument("--feedback", choices=["off", "interactive", "prf"],
                        default="off", help="相关性反馈模式")
    parser.add_argument("--prf-top-n", type=int, default=5,
                        help="PRF 假设相关的文档数")
    args = parser.parse_args()

    # 加载索引和文档数据
    print("正在加载索引...")
    index = InvertedIndex.load(args.index_dir)
    doc_store = load_doc_store(args.index_dir)
    doc_texts = load_doc_texts(args.index_dir)

    # 初始化检索器
    if args.model == "tfidf":
        retriever = TFIDFRetriever(index)
        model_name = "TF-IDF"
    elif args.model == "semantic":
        # 尝试加载语义检索器
        try:
            from src.semantic import SemanticRetriever
            sem = SemanticRetriever(
                index,
                model_path=os.path.join(args.index_dir, "w2v.model"),
                doc_vectors_path=os.path.join(args.index_dir, "doc_vectors.npy"),
            )
            sem.load()
            retriever = sem
            model_name = "Semantic (Word2Vec)"
        except Exception as e:
            print(f"[警告] 语义检索器加载失败，回退到 BM25: {e}")
            retriever = BM25Retriever(index)
            model_name = "BM25 (fallback)"
    else:
        retriever = BM25Retriever(index)
        model_name = "BM25"

    # 初始化评价器（如果启用评价模式）
    evaluator = Evaluator() if args.eval else None

    print(f"检索模型: {model_name}")
    print(f"文档数量: {index.doc_count}")
    if args.query_expansion:
        print("查询扩展: 已启用 (WordNet)")
    if args.eval:
        print("评价模式: 已启用")
    if args.feedback != "off":
        print(f"相关性反馈: {args.feedback}" +
              (f" (PRF Top-{args.prf_top_n})" if args.feedback == "prf" else ""))
    print("输入查询（输入 'quit' 退出，'switch' 切换模型）:\n")

    while True:
        try:
            query = input("Query> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见!")
            break

        if not query:
            continue
        if query.lower() == "quit":
            print("再见!")
            break
        if query.lower() == "switch":
            # 切换模型
            if isinstance(retriever, TFIDFRetriever):
                retriever = BM25Retriever(index)
                model_name = "BM25"
            elif isinstance(retriever, BM25Retriever):
                # 尝试切换到语义检索
                try:
                    from src.semantic import SemanticRetriever
                    sem = SemanticRetriever(
                        index,
                        model_path=os.path.join(args.index_dir, "w2v.model"),
                        doc_vectors_path=os.path.join(args.index_dir, "doc_vectors.npy"),
                    )
                    sem.load()
                    retriever = sem
                    model_name = "Semantic (Word2Vec)"
                except Exception:
                    retriever = TFIDFRetriever(index)
                    model_name = "TF-IDF"
            else:
                retriever = TFIDFRetriever(index)
                model_name = "TF-IDF"
            print(f"已切换到 {model_name}\n")
            continue

        # 查询扩展
        search_query = query
        if args.query_expansion:
            search_query = expand_query_wordnet(query)
            if search_query != query:
                print(f"[扩展查询] {search_query}\n")

        start = time.time()
        results = retriever.search(search_query, top_k=args.top_k)
        elapsed = (time.time() - start) * 1000

        # PRF 模式：自动执行伪相关反馈
        if args.feedback == "prf" and results:
            print(f"\n[{model_name}] 初始检索 {len(results)} 条 ({elapsed:.1f} ms)")
            print(f"[PRF] 取 Top-{args.prf_top_n} 作为相关文档，执行 Rocchio 反馈...")
            start2 = time.time()
            results = pseudo_relevance_feedback(
                retriever, search_query, index,
                prf_top_n=args.prf_top_n, top_k=args.top_k)
            elapsed2 = (time.time() - start2) * 1000
            print(f"[PRF] 反馈检索完成: {len(results)} 条 ({elapsed2:.1f} ms)\n")
        else:
            print(f"\n[{model_name}] 找到 {len(results)} 条结果 ({elapsed:.1f} ms)\n")

        # 显示结果
        for rank, (doc_id, score) in enumerate(results, 1):
            doc = doc_store.get(doc_id, {})
            print(format_result(rank, doc, score, query, doc_texts))
            print()

        # 人工评价（和交互式反馈共用标注流程）
        if (args.eval or args.feedback == "interactive") and results:
            print("\n" + "=" * 60)
            print("请标注每条结果的相关性")
            print("=" * 60)
            judgments = []
            for rank, (doc_id, score) in enumerate(results, 1):
                doc = doc_store.get(doc_id, {})
                title = doc.get("title", "Untitled")[:60]
                while True:
                    try:
                        ans = input(f"[{rank}] {title}... 相关? [y/n]: ").strip().lower()
                        if ans in ["y", "n"]:
                            judgments.append(ans == "y")
                            break
                        print("请输入 y 或 n")
                    except (EOFError, KeyboardInterrupt):
                        print("\n标注已取消")
                        judgments = []
                        break
                if not judgments or len(judgments) < rank:
                    break

            if judgments:
                # 保存评价记录
                if args.eval:
                    result_tuples = [
                        (doc_id, score, doc_store.get(doc_id, {}).get("title", ""))
                        for doc_id, score in results
                    ]
                    evaluator.add_evaluation(query, model_name, result_tuples, judgments)
                    metrics = evaluator.compute_metrics(judgments)
                    print(f"\n评价已保存!")
                    print(f"  P@5:  {metrics['P@5']:.2f}")
                    print(f"  P@10: {metrics['P@10']:.2f}")
                    print(f"  相关文档: {metrics['relevant_count']}/{metrics['total']}")

                # 交互式 Rocchio 反馈
                if args.feedback == "interactive":
                    relevant_ids = {results[i][0] for i, j in enumerate(judgments) if j}
                    non_relevant_ids = {results[i][0] for i, j in enumerate(judgments) if not j}

                    if relevant_ids:
                        iteration = 1
                        while True:
                            print(f"\n[Rocchio 反馈 - 第 {iteration} 轮]")
                            print(f"  相关: {len(relevant_ids)} 篇, 不相关: {len(non_relevant_ids)} 篇")
                            start_fb = time.time()

                            # 根据模型类型执行反馈
                            from src.semantic import SemanticRetriever
                            if isinstance(retriever, TFIDFRetriever):
                                rocchio = RocchioTFIDF(index)
                                fb_results = rocchio.search_with_feedback(
                                    retriever, search_query,
                                    relevant_ids, non_relevant_ids, args.top_k)
                            elif isinstance(retriever, BM25Retriever):
                                rocchio = RocchioBM25(index)
                                fb_results = rocchio.search_with_feedback(
                                    retriever, search_query,
                                    relevant_ids, non_relevant_ids, args.top_k)
                            elif isinstance(retriever, SemanticRetriever):
                                rocchio = RocchioSemantic(retriever)
                                fb_results = rocchio.search_with_feedback(
                                    search_query,
                                    relevant_ids, non_relevant_ids, args.top_k)
                            else:
                                print("当前模型不支持 Rocchio 反馈")
                                break

                            elapsed_fb = (time.time() - start_fb) * 1000
                            print(f"  反馈检索: {len(fb_results)} 条 ({elapsed_fb:.1f} ms)\n")

                            for rank, (doc_id, score) in enumerate(fb_results, 1):
                                doc = doc_store.get(doc_id, {})
                                print(format_result(rank, doc, score, query, doc_texts))
                                print()

                            # 询问是否继续迭代
                            try:
                                cont = input("继续迭代反馈? [y/n]: ").strip().lower()
                            except (EOFError, KeyboardInterrupt):
                                break
                            if cont != "y":
                                break

                            # 重新标注
                            results = fb_results
                            judgments = []
                            for rank, (doc_id, score) in enumerate(fb_results, 1):
                                doc = doc_store.get(doc_id, {})
                                title = doc.get("title", "Untitled")[:60]
                                while True:
                                    try:
                                        ans = input(f"[{rank}] {title}... 相关? [y/n]: ").strip().lower()
                                        if ans in ["y", "n"]:
                                            judgments.append(ans == "y")
                                            break
                                        print("请输入 y 或 n")
                                    except (EOFError, KeyboardInterrupt):
                                        judgments = []
                                        break
                                if not judgments or len(judgments) < rank:
                                    break

                            if not judgments:
                                break

                            relevant_ids = {fb_results[i][0] for i, j in enumerate(judgments) if j}
                            non_relevant_ids = {fb_results[i][0] for i, j in enumerate(judgments) if not j}
                            iteration += 1
                    else:
                        print("\n未标注任何相关文档，跳过反馈。")

        print("-" * 60)


if __name__ == "__main__":
    main()
