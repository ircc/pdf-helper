# -*- coding: utf-8 -*-
"""TOC 配置查找与路径约定。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DIR = ROOT / "sample"


def bookmark_txt_path(pdf: Path) -> Path:
    return pdf.parent / f"{pdf.stem}_bookmark.txt"


def pdf_out_path(pdf: Path) -> Path:
    return pdf.parent / f"{pdf.stem}-TOC.pdf"


def find_toc_config(pdf: Path) -> Path | None:
    """根据 PDF 文件名或书名自动匹配 sample/toc_*.json。"""
    candidates = sorted(SAMPLE_DIR.glob("toc_*.json"))
    if not candidates:
        return None

    stem = pdf.stem
    for path in candidates:
        try:
            cfg = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        title = cfg.get("book_title", "")
        if title and (title in stem or stem in title):
            return path
        key = path.stem.removeprefix("toc_")
        if key and key in stem:
            return path

    if "十五五" in stem or "第十五个五年" in stem:
        for path in candidates:
            if "十五五" in path.stem:
                return path

    if len(candidates) == 1:
        return candidates[0]
    return None
