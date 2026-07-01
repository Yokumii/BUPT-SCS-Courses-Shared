"""
IE 评价模块：计算信息抽取的 Precision / Recall / F1，
支持精确匹配和部分匹配，管理 gold standard 标注。
"""

import json
import os
from collections import defaultdict
from datetime import datetime

from src.schema import AcademicPaperEvent, MetricResult


class IEEvaluator:
    """信息抽取评价器。"""

    def __init__(self, gold_path: str = "index/ie_gold_standard.json"):
        self.gold_path = gold_path
        self.gold_data: dict[int, dict] = self._load_gold()

    def _load_gold(self) -> dict[int, dict]:
        """加载 gold standard 标注。"""
        if os.path.exists(self.gold_path):
            with open(self.gold_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {item["doc_id"]: item for item in data}
        return {}

    def save_gold(self):
        """保存 gold standard。"""
        os.makedirs(os.path.dirname(self.gold_path) or ".", exist_ok=True)
        data = list(self.gold_data.values())
        with open(self.gold_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_annotation(self, doc_id: int, annotations: dict):
        """
        添加或更新一篇文档的人工标注。

        Args:
            doc_id: 文档 ID
            annotations: {
                "methods": [...], "datasets": [...], "metrics": [...],
                "domain_keywords": [...], "affiliations": [...],
                "findings": [...], "study_characteristics": {...}
            }
        """
        self.gold_data[doc_id] = {
            "doc_id": doc_id,
            "annotator": "human",
            "timestamp": datetime.now().isoformat(),
            "annotations": annotations,
        }
        self.save_gold()

    def evaluate_event(
        self, event: AcademicPaperEvent, match_mode: str = "partial"
    ) -> dict:
        """
        评价单个事件的抽取质量。

        Args:
            event: 待评价的抽取事件
            match_mode: "exact" 精确匹配 / "partial" 部分匹配

        Returns:
            {field_name: {"precision": float, "recall": float, "f1": float}, ...}
        """
        gold = self.gold_data.get(event.doc_id)
        if gold is None:
            return {}

        ann = gold["annotations"]
        results = {}

        # 列表类字段
        for field in ["methods", "datasets", "domain_keywords", "affiliations", "findings"]:
            extracted = getattr(event, field, [])
            gold_items = ann.get(field, [])
            results[field] = self._compute_list_metrics(
                extracted, gold_items, match_mode
            )

        # metrics 字段
        extracted_metrics = [(m.name, m.value) for m in event.metrics]
        gold_metrics = ann.get("metrics", [])
        gold_metric_tuples = [
            (m["name"], m["value"]) if isinstance(m, dict) else (m, "")
            for m in gold_metrics
        ]
        results["metrics"] = self._compute_metric_metrics(
            extracted_metrics, gold_metric_tuples, match_mode
        )

        # study_characteristics（按 key 匹配）
        ext_chars = event.study_characteristics
        gold_chars = ann.get("study_characteristics", {})
        results["study_characteristics"] = self._compute_dict_metrics(
            ext_chars, gold_chars
        )

        return results

    def evaluate_batch(
        self,
        events,
        match_mode: str = "partial",
    ) -> dict:
        """
        批量评价，返回各字段的平均 P/R/F1 和 Macro/Micro 指标。

        Returns:
            {
                "per_field": {field: {"precision": ..., "recall": ..., "f1": ...}},
                "macro_f1": float,
                "micro_f1": float,
                "evaluated_count": int,
            }
        """
        field_tp = defaultdict(int)
        field_fp = defaultdict(int)
        field_fn = defaultdict(int)
        field_scores = defaultdict(lambda: {"p_sum": 0, "r_sum": 0, "f1_sum": 0, "count": 0})
        evaluated = 0

        for event in events:
            scores = self.evaluate_event(event, match_mode)
            if not scores:
                continue
            evaluated += 1
            for field_name, metrics in scores.items():
                p, r, f1 = metrics["precision"], metrics["recall"], metrics["f1"]
                field_scores[field_name]["p_sum"] += p
                field_scores[field_name]["r_sum"] += r
                field_scores[field_name]["f1_sum"] += f1
                field_scores[field_name]["count"] += 1
                field_tp[field_name] += metrics.get("tp", 0)
                field_fp[field_name] += metrics.get("fp", 0)
                field_fn[field_name] += metrics.get("fn", 0)

        if evaluated == 0:
            return {"per_field": {}, "macro_f1": 0, "micro_f1": 0, "evaluated_count": 0}

        # 各字段平均
        per_field = {}
        for field_name, data in field_scores.items():
            n = data["count"]
            per_field[field_name] = {
                "precision": data["p_sum"] / n if n else 0,
                "recall": data["r_sum"] / n if n else 0,
                "f1": data["f1_sum"] / n if n else 0,
            }

        # Macro F1
        f1_values = [v["f1"] for v in per_field.values()]
        macro_f1 = sum(f1_values) / len(f1_values) if f1_values else 0

        # Micro F1
        total_tp = sum(field_tp.values())
        total_fp = sum(field_fp.values())
        total_fn = sum(field_fn.values())
        micro_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0
        micro_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0
        micro_f1 = 2 * micro_p * micro_r / (micro_p + micro_r) if (micro_p + micro_r) else 0

        return {
            "per_field": per_field,
            "macro_f1": macro_f1,
            "micro_f1": micro_f1,
            "evaluated_count": evaluated,
        }

    # ── 内部计算方法 ────────────────────────────

    def _compute_list_metrics(
        self, extracted: list[str], gold: list[str], mode: str
    ) -> dict:
        """计算列表类字段的 P/R/F1。"""
        if not extracted and not gold:
            return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "tp": 0, "fp": 0, "fn": 0}

        if mode == "exact":
            ext_set = {s.lower().strip() for s in extracted}
            gold_set = {s.lower().strip() for s in gold}
            tp = len(ext_set & gold_set)
        else:
            # 部分匹配：token overlap
            tp = 0
            matched_gold = set()
            for ext in extracted:
                ext_tokens = set(ext.lower().split())
                best_overlap = 0
                best_idx = -1
                for i, g in enumerate(gold):
                    if i in matched_gold:
                        continue
                    gold_tokens = set(g.lower().split())
                    if not gold_tokens:
                        continue
                    overlap = len(ext_tokens & gold_tokens) / len(gold_tokens)
                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_idx = i
                if best_overlap >= 0.5 and best_idx >= 0:
                    tp += 1
                    matched_gold.add(best_idx)

        fp = len(extracted) - tp
        fn = len(gold) - tp

        precision = tp / (tp + fp) if (tp + fp) else 0
        recall = tp / (tp + fn) if (tp + fn) else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

        return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}

    def _compute_metric_metrics(
        self, extracted: list[tuple], gold: list[tuple], mode: str
    ) -> dict:
        """计算 metrics 字段的 P/R/F1。"""
        if not extracted and not gold:
            return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "tp": 0, "fp": 0, "fn": 0}

        tp = 0
        matched = set()
        for (en, ev) in extracted:
            for i, (gn, gv) in enumerate(gold):
                if i in matched:
                    continue
                if mode == "exact":
                    if en.lower() == gn.lower() and ev == gv:
                        tp += 1
                        matched.add(i)
                        break
                else:
                    # 部分匹配：指标名相似 or 值相同
                    name_match = en.lower().strip() in gn.lower().strip() or gn.lower().strip() in en.lower().strip()
                    value_match = ev.strip().rstrip("%") == gv.strip().rstrip("%")
                    if name_match or value_match:
                        tp += 1
                        matched.add(i)
                        break

        fp = len(extracted) - tp
        fn = len(gold) - tp
        precision = tp / (tp + fp) if (tp + fp) else 0
        recall = tp / (tp + fn) if (tp + fn) else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

        return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}

    def _compute_dict_metrics(self, extracted: dict, gold: dict) -> dict:
        """计算字典类字段的 P/R/F1（按 key 匹配）。"""
        if not extracted and not gold:
            return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "tp": 0, "fp": 0, "fn": 0}

        ext_keys = set(extracted.keys())
        gold_keys = set(gold.keys())
        tp = len(ext_keys & gold_keys)
        fp = len(ext_keys - gold_keys)
        fn = len(gold_keys - ext_keys)

        precision = tp / (tp + fp) if (tp + fp) else 0
        recall = tp / (tp + fn) if (tp + fn) else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

        return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}
