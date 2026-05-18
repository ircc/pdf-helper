# -*- coding: utf-8 -*-
"""根据扫描结果生成书签 txt。"""
from pathlib import Path

from .config import bookmark_txt_path
from .scanner import TocScanner

INDENT = "    "


class BookmarkGenerator:
    def __init__(self, pdf_path: Path, toc_path: Path):
        self.pdf_path = Path(pdf_path)
        self.toc_path = Path(toc_path)
        self.scanner = TocScanner(self.pdf_path)

    def generate(self, output_path: Path | None = None) -> Path:
        config = TocScanner.load_config(self.toc_path)
        pages = self.scanner.scan(config)
        entries = self.scanner.build_entries(config, pages)
        content = self._entries_to_txt(entries)

        out = Path(output_path) if output_path else bookmark_txt_path(self.pdf_path)
        out.write_text(content, encoding="utf-8")
        return out

    @staticmethod
    def _entries_to_txt(entries: list[tuple[str, int, int]]) -> str:
        lines = [f"{INDENT * level}{title}@{page}" for title, page, level in entries]
        return "\n".join(lines) + "\n"
