"""
知识图谱构建与可视化：
将抽取的实体和关系构建为跨论文知识图谱，
使用 networkx 构建图结构，pyvis 生成交互式可视化。
"""

import os
from collections import defaultdict

import networkx as nx

from src.schema import AcademicPaperEvent


# 节点颜色配置
NODE_COLORS = {
    "paper": "#4A90D9",
    "method": "#E74C3C",
    "dataset": "#2ECC71",
    "institution": "#F39C12",
    "domain": "#9B59B6",
}


class KnowledgeGraph:
    """学术论文知识图谱。"""

    def __init__(self):
        self.graph = nx.Graph()
        self._entity_freq: dict[str, int] = defaultdict(int)

    def build_from_events(
        self,
        events: list[AcademicPaperEvent],
        min_entity_freq: int = 2,
    ):
        self.build_from_event_source(lambda: events, min_entity_freq=min_entity_freq)

    def build_from_event_source(
        self,
        event_source,
        min_entity_freq: int = 2,
    ):
        """
        从事件源构建知识图谱。

        Args:
            event_source: 无参可调用对象，每次调用返回事件迭代器
            min_entity_freq: 实体最小出现频率（过滤低频噪声）
        """
        # 第一遍：统计实体频率
        self._entity_freq.clear()
        for event in event_source():
            for method in event.methods:
                self._entity_freq[("method", method.lower())] += 1
            for ds in event.datasets:
                self._entity_freq[("dataset", ds.lower())] += 1
            for aff in event.affiliations:
                self._entity_freq[("institution", aff.lower())] += 1
            for kw in event.domain_keywords:
                self._entity_freq[("domain", kw.lower())] += 1

        # 第二遍：构建图谱（仅保留高频实体）
        self.graph.clear()
        for event in event_source():
            paper_id = f"paper_{event.doc_id}"
            short_title = event.title[:60] + "..." if len(event.title) > 60 else event.title
            self.graph.add_node(
                paper_id,
                label=short_title,
                node_type="paper",
                color=NODE_COLORS["paper"],
                title=event.title,
            )

            self._add_entities(paper_id, "method", event.methods, "USES_METHOD", min_entity_freq)
            self._add_entities(paper_id, "dataset", event.datasets, "EVALUATED_ON", min_entity_freq)
            self._add_entities(paper_id, "institution", event.affiliations, "AUTHORED_BY", min_entity_freq)
            self._add_entities(paper_id, "domain", event.domain_keywords, "BELONGS_TO", min_entity_freq)

    def _add_entities(
        self,
        paper_id: str,
        entity_type: str,
        items: list[str],
        relation: str,
        min_freq: int,
    ):
        for item in items:
            key = (entity_type, item.lower())
            if self._entity_freq[key] < min_freq:
                continue
            node_id = f"{entity_type}:{item.lower()}"
            if not self.graph.has_node(node_id):
                self.graph.add_node(
                    node_id,
                    label=item,
                    node_type=entity_type,
                    color=NODE_COLORS.get(entity_type, "#95A5A6"),
                    title=f"{entity_type}: {item}",
                )
            self.graph.add_edge(paper_id, node_id, relation=relation)

    def get_stats(self) -> dict:
        """返回图谱统计信息。"""
        node_types = defaultdict(int)
        for _, data in self.graph.nodes(data=True):
            node_types[data.get("node_type", "unknown")] += 1

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": dict(node_types),
            "components": nx.number_connected_components(self.graph),
        }

    def get_top_entities(self, entity_type: str, top_k: int = 20) -> list[tuple[str, int]]:
        """获取某类型的高频实体。"""
        items = [
            (name, freq)
            for (etype, name), freq in self._entity_freq.items()
            if etype == entity_type
        ]
        items.sort(key=lambda x: x[1], reverse=True)
        return items[:top_k]

    def to_pyvis_html(
        self,
        output_path: str = "index/knowledge_graph.html",
        height: str = "700px",
        width: str = "100%",
        max_nodes: int = 500,
    ) -> str:
        """
        导出为 pyvis 交互式 HTML。

        Args:
            output_path: 输出文件路径
            height: 可视化高度
            width: 可视化宽度
            max_nodes: 最大节点数（过多节点会导致渲染卡顿）

        Returns:
            HTML 文件路径
        """
        from pyvis.network import Network

        net = Network(
            height=height,
            width=width,
            bgcolor="#ffffff",
            font_color="#333333",
            notebook=False,
            directed=False,
        )

        # 如果节点过多，取度数最大的子图
        if self.graph.number_of_nodes() > max_nodes:
            top_nodes = sorted(
                self.graph.degree(), key=lambda x: x[1], reverse=True
            )[:max_nodes]
            subgraph = self.graph.subgraph([n for n, _ in top_nodes])
        else:
            subgraph = self.graph

        # 添加节点
        for node, data in subgraph.nodes(data=True):
            degree = subgraph.degree(node)
            # 节点大小按度数缩放
            size = min(5 + degree * 2, 40)
            net.add_node(
                node,
                label=data.get("label", node)[:30],
                color=data.get("color", "#95A5A6"),
                size=size,
                title=data.get("title", node),
            )

        # 添加边
        for u, v, data in subgraph.edges(data=True):
            net.add_edge(u, v, title=data.get("relation", ""))

        # 物理引擎配置
        net.set_options("""
        {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 100,
                    "springConstant": 0.08
                },
                "solver": "forceAtlas2Based",
                "stabilization": {"iterations": 150}
            },
            "nodes": {
                "font": {"size": 12}
            }
        }
        """)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        net.save_graph(output_path)
        return output_path

    def save_gexf(self, path: str = "index/knowledge_graph.gexf"):
        """导出为 GEXF 格式（供 Gephi 等工具使用）。"""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        nx.write_gexf(self.graph, path)
