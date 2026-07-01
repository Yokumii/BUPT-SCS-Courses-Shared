"""
索引构建脚本：解析 → 预处理 → 建索引 → 持久化 → (可选) 训练语义模型。

用法:
    python build_index.py [--data-dir DATA_DIR] [--index-dir INDEX_DIR] [--semantic]
"""

import argparse
import os
import pickle
import sqlite3
import time

from src.parser import parse_all_documents
from src.preprocessor import preprocess_document
from src.indexer import InvertedIndex



# 索引产物分为两组，各组内文件要么全有要么全无
_INDEX_FILES = [
    "lexicon.pkl", "postings_doc_ids.npy", "postings_tfs.npy",
    "doc_metadata.pkl", "idf.pkl",
    "doc_meta.pkl", "doc_texts.db",
]
_SEMANTIC_FILES = ["w2v.model", "doc_vectors.npy", "doc_vector_ids.npy"]


def _check_group(index_dir: str, files: list[str]) -> bool:
    """检查一组文件是否全部存在。"""
    return all(os.path.exists(os.path.join(index_dir, f)) for f in files)


def _print_skipped(index_dir: str, files: list[str], label: str):
    """打印跳过信息及已有文件大小。"""
    print(f"[跳过] {label}（文件已存在）:")
    for name in files:
        fpath = os.path.join(index_dir, name)
        if os.path.isfile(fpath):
            size_kb = os.path.getsize(fpath) / 1024
            print(f"  {name} ({size_kb:.1f} KB)")


def build(data_dir: str = "data", index_dir: str = "index",
          train_semantic: bool = False, force: bool = False):
    """执行完整的索引构建流程，自动跳过已存在的部分。"""

    # 判断各组是否需要构建
    need_index = force or not _check_group(index_dir, _INDEX_FILES)
    need_semantic = train_semantic and (force or not _check_group(index_dir, _SEMANTIC_FILES))

    if not need_index and not need_semantic:
        print("所有索引文件已存在，无需构建（使用 --force 强制重建）:")
        for name in sorted(os.listdir(index_dir)):
            fpath = os.path.join(index_dir, name)
            if os.path.isfile(fpath):
                size_kb = os.path.getsize(fpath) / 1024
                print(f"  {name} ({size_kb:.1f} KB)")
        return

    start_time = time.time()

    # 计算实际要执行的步骤数（解析和预处理始终需要）
    steps = ["解析文档", "文本预处理"]
    if need_index:
        steps.append("构建倒排索引")
    if need_semantic:
        steps.append("训练 Word2Vec 语义模型")
    total_steps = len(steps)
    current_step = 0

    # 打印跳过信息
    if not need_index:
        _print_skipped(index_dir, _INDEX_FILES, "倒排索引")
    if train_semantic and not need_semantic:
        _print_skipped(index_dir, _SEMANTIC_FILES, "语义模型")

    # Step: 解析文档
    current_step += 1
    print("=" * 60)
    print(f"Step {current_step}/{total_steps}: 解析文档")
    print("=" * 60)
    documents = parse_all_documents(data_dir, verbose=True)

    # Step: 预处理
    current_step += 1
    print()
    print("=" * 60)
    print(f"Step {current_step}/{total_steps}: 文本预处理")
    print("=" * 60)
    for i, doc in enumerate(documents):
        preprocess_document(doc)
        if (i + 1) % 2000 == 0:
            print(f"  已预处理 {i + 1}/{len(documents)} 篇文档")
    print(f"预处理完成: {len(documents)} 篇文档")

    # Step: 构建倒排索引（仅在缺失时执行）
    if need_index:
        current_step += 1
        print()
        print("=" * 60)
        print(f"Step {current_step}/{total_steps}: 构建倒排索引")
        print("=" * 60)
        index = InvertedIndex()
        index.build(documents, verbose=True)

        # 持久化索引
        index.save(index_dir)

        # 保存文档数据：拆分为轻量元数据 + 正文内容
        doc_meta = []
        for doc in documents:
            doc_meta.append({
                "doc_id": doc.doc_id,
                "title": doc.title,
                "journal": doc.journal,
                "doi": doc.doi,
                "date": doc.date,
                "authors": doc.authors,
                "filename": doc.filename,
            })

        # 轻量元数据（启动时加载）
        meta_path = os.path.join(index_dir, "doc_meta.pkl")
        with open(meta_path, "wb") as f:
            pickle.dump(doc_meta, f, protocol=pickle.HIGHEST_PROTOCOL)

        # 正文内容（SQLite 按需查询，不全量加载）
        db_path = os.path.join(index_dir, "doc_texts.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE doc_texts (doc_id INTEGER PRIMARY KEY, abstract TEXT, body TEXT)"
        )
        conn.executemany(
            "INSERT INTO doc_texts (doc_id, abstract, body) VALUES (?, ?, ?)",
            [(doc.doc_id, doc.abstract, doc.body) for doc in documents],
        )
        conn.commit()
        conn.close()

        print(f"文档数据已保存: {len(doc_meta)} 条记录 (doc_meta.pkl + doc_texts.db)")
    else:
        # 倒排索引已存在，从磁盘加载（语义训练需要 index 对象）
        index = InvertedIndex.load(index_dir)

    # Step: 训练语义模型（仅在缺失时执行）
    if need_semantic:
        current_step += 1
        print()
        print("=" * 60)
        print(f"Step {current_step}/{total_steps}: 训练 Word2Vec 语义模型")
        print("=" * 60)
        from src.semantic import SemanticRetriever
        sem = SemanticRetriever(
            index,
            model_path=os.path.join(index_dir, "w2v.model"),
            doc_vectors_path=os.path.join(index_dir, "doc_vectors.npy"),
        )
        sem.train(documents, vector_size=100, window=5, min_count=5, epochs=10)
        sem.save()

    elapsed = time.time() - start_time
    print()
    print("=" * 60)
    print(f"全部完成! 耗时: {elapsed:.1f} 秒")
    print(f"  有效文档: {len(documents)}")
    print(f"  词项数量: {len(index.index)}")
    print(f"  索引目录: {os.path.abspath(index_dir)}")
    built_parts = []
    if need_index:
        built_parts.append("倒排索引")
    if need_semantic:
        built_parts.append("语义模型")
    print(f"  本次构建: {', '.join(built_parts)}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="构建倒排索引")
    parser.add_argument("--data-dir", default="data", help="数据文件目录")
    parser.add_argument("--index-dir", default="index", help="索引输出目录")
    parser.add_argument("--semantic", action="store_true",
                        help="同时训练 Word2Vec 语义模型")
    parser.add_argument("--force", action="store_true",
                        help="强制重建索引（忽略已存在的索引文件）")
    args = parser.parse_args()

    build(data_dir=args.data_dir, index_dir=args.index_dir,
          train_semantic=args.semantic, force=args.force)
