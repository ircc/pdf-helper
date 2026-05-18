# -*- coding: utf-8 -*-
"""将书签 txt 写入 PDF。"""
from pathlib import Path

from add_bookmarks import save_history
from utils import PDFHandler

from .config import pdf_out_path


class BookmarkApplier:
    def __init__(
        self,
        pdf_path: Path,
        bookmark_path: Path,
        output_path: Path | None = None,
        page_offset: int = 0,
        collapse: bool = True,
        save_hist: bool = True,
    ):
        self.pdf_path = Path(pdf_path)
        self.bookmark_path = Path(bookmark_path)
        self.output_path = Path(output_path) if output_path else pdf_out_path(self.pdf_path)
        self.page_offset = page_offset
        self.collapse = collapse
        self.save_hist = save_hist

    def apply(self) -> Path:
        handler = PDFHandler(self.pdf_path, "newly")
        bookmarks, max_parent = handler.read_bookmarks_from_txt(
            self.bookmark_path, page_offset=self.page_offset
        )
        handler.add_bookmarks(bookmarks, max_parent, collapse=self.collapse)
        handler.save(self.output_path)
        if self.save_hist:
            save_history(self.pdf_path, self.bookmark_path, self.output_path)
        return self.output_path
