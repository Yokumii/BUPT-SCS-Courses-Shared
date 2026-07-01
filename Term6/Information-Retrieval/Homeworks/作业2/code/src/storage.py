"""
文档正文存储：提供 SQLite 按需查询接口，替代全量 pkl 加载。
"""

import os
import pickle
import sqlite3


class DocTextsDB:
    """SQLite 后端的文档正文存储，提供与 dict 兼容的 .get() 接口。"""

    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

    def get(self, doc_id, default=None):
        """按 doc_id 查询单条文档正文。"""
        row = self.conn.execute(
            "SELECT abstract, body FROM doc_texts WHERE doc_id = ?", (doc_id,)
        ).fetchone()
        if row is None:
            return default
        return {"doc_id": doc_id, "abstract": row[0], "body": row[1]}

    def close(self):
        self.conn.close()


def load_doc_texts(index_dir: str = "index"):
    """加载文档正文存储，按优先级降级：.db → .pkl → {}。"""
    db_path = os.path.join(index_dir, "doc_texts.db")
    if os.path.exists(db_path):
        return DocTextsDB(db_path)

    pkl_path = os.path.join(index_dir, "doc_texts.pkl")
    if os.path.exists(pkl_path):
        with open(pkl_path, "rb") as f:
            text_list = pickle.load(f)
        return {d["doc_id"]: d for d in text_list}

    return {}
