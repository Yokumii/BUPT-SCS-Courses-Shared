"""
人工评价系统：对检索结果进行二元相关性标注，
计算 Precision@K 指标，保存评价记录。
"""

import json
import os
from collections import defaultdict
from datetime import datetime


class Evaluator:
    """检索结果评价器。"""

    def __init__(self, save_path: str = "index/evaluations.json"):
        self.save_path = save_path
        self.evaluations = self._load()

    def _load(self) -> list:
        """从文件加载评价记录。"""
        if os.path.exists(self.save_path):
            with open(self.save_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save(self):
        """保存评价记录到文件。"""
        os.makedirs(os.path.dirname(self.save_path) or ".", exist_ok=True)
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(self.evaluations, f, ensure_ascii=False, indent=2)

    def add_evaluation(self, query: str, model: str,
                       results: list, judgments: list):
        """
        添加一条评价记录。

        参数:
            query: 查询字符串
            model: 使用的检索模型（如 "TF-IDF", "BM25"）
            results: [(doc_id, score, title), ...] 检索结果
            judgments: [True/False, ...] 相关性判断（与 results 一一对应）
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "model": model,
            "results": [
                {
                    "rank": i + 1,
                    "doc_id": r[0],
                    "score": r[1],
                    "title": r[2],
                    "relevant": j,
                }
                for i, (r, j) in enumerate(zip(results, judgments))
            ],
        }
        self.evaluations.append(record)
        self.save()

    def precision_at_k(self, judgments: list, k: int) -> float:
        """
        计算 Precision@K。

        参数:
            judgments: [True/False, ...] 相关性判断列表
            k: 截断位置

        返回:
            Precision@K 值
        """
        top_k = judgments[:k]
        if not top_k:
            return 0.0
        return sum(1 for j in top_k if j) / len(top_k)

    def compute_metrics(self, judgments: list) -> dict:
        """
        计算多个评价指标。

        参数:
            judgments: [True/False, ...] 相关性判断列表

        返回:
            {"P@5": float, "P@10": float, "relevant_count": int, "total": int}
        """
        return {
            "P@5": self.precision_at_k(judgments, 5),
            "P@10": self.precision_at_k(judgments, 10),
            "relevant_count": sum(1 for j in judgments if j),
            "total": len(judgments),
        }

    def add_feedback_record(self, query: str, model: str, iteration: int,
                            relevant_ids: list, non_relevant_ids: list,
                            results_before: list, results_after: list,
                            config: dict = None):
        """
        添加一条 Rocchio 反馈记录。

        参数:
            query: 查询字符串
            model: 检索模型名称
            iteration: 反馈迭代轮次
            relevant_ids: 标注为相关的文档 ID 列表
            non_relevant_ids: 标注为不相关的文档 ID 列表
            results_before: 反馈前的检索结果 [(doc_id, score), ...]
            results_after: 反馈后的检索结果 [(doc_id, score), ...]
            config: Rocchio 参数配置字典
        """
        record = {
            "type": "rocchio_feedback",
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "model": model,
            "iteration": iteration,
            "relevant_ids": list(relevant_ids),
            "non_relevant_ids": list(non_relevant_ids),
            "results_before": [
                {"doc_id": did, "score": s} for did, s in results_before
            ],
            "results_after": [
                {"doc_id": did, "score": s} for did, s in results_after
            ],
            "config": config or {},
        }
        self.evaluations.append(record)
        self.save()

    def get_summary(self) -> dict:
        """
        获取所有评价的汇总统计。

        返回:
            按模型分组的平均 Precision@K
        """
        model_metrics = defaultdict(lambda: {"p5_sum": 0, "p10_sum": 0, "count": 0})

        for record in self.evaluations:
            # 跳过反馈记录，只统计常规评价
            if record.get("type") == "rocchio_feedback":
                continue
            model = record["model"]
            judgments = [r["relevant"] for r in record["results"]]
            metrics = self.compute_metrics(judgments)
            model_metrics[model]["p5_sum"] += metrics["P@5"]
            model_metrics[model]["p10_sum"] += metrics["P@10"]
            model_metrics[model]["count"] += 1

        summary = {}
        for model, data in model_metrics.items():
            n = data["count"]
            summary[model] = {
                "avg_P@5": data["p5_sum"] / n if n > 0 else 0,
                "avg_P@10": data["p10_sum"] / n if n > 0 else 0,
                "num_queries": n,
            }
        return summary
