# -*- coding: utf-8 -*-
"""一键流程：扫描 → 生成书签 txt → 校验 → 写入 PDF。"""
from pathlib import Path

from .applier import BookmarkApplier
from .config import SAMPLE_DIR, bookmark_txt_path, find_toc_config, pdf_out_path
from .generator import BookmarkGenerator
from .verifier import BookmarkVerifier


class BookmarkPipeline:
    """为 PDF 添加完整书签目录（主入口类）。"""

    def __init__(
        self,
        pdf_path: Path,
        toc_path: Path | None = None,
        *,
        page_offset: int = 0,
        collapse: bool = True,
        verify: bool = True,
        save_history: bool = True,
    ):
        self.pdf_path = Path(pdf_path).resolve()
        self.toc_path = Path(toc_path).resolve() if toc_path else None
        self.page_offset = page_offset
        self.collapse = collapse
        self.verify = verify
        self.save_history = save_history

    def _resolve_toc(self) -> Path:
        toc = self.toc_path or find_toc_config(self.pdf_path)
        if toc is None:
            raise FileNotFoundError(
                f"未找到与「{self.pdf_path.name}」匹配的 TOC 配置。\n"
                f"请将 toc_*.json 放入 {SAMPLE_DIR}，或使用 --toc 指定。"
            )
        return toc

    def generate_txt(self, output: Path | None = None) -> Path:
        toc = self._resolve_toc()
        print(f"TOC 配置：{toc.name}")
        bm = BookmarkGenerator(self.pdf_path, toc).generate(output)
        print(f"书签 txt：{bm}")
        return bm

    def apply_txt(self, bookmark: Path, output: Path | None = None) -> Path:
        out = BookmarkApplier(
            self.pdf_path,
            bookmark,
            output_path=output or pdf_out_path(self.pdf_path),
            page_offset=self.page_offset,
            collapse=self.collapse,
            save_hist=self.save_history,
        ).apply()
        print(f"带目录 PDF：{out}")
        return out

    def run(self) -> Path:
        """完整流程，返回带目录的 PDF 路径。"""
        print(f"处理：{self.pdf_path.name}")
        bm = self.generate_txt()
        if self.verify:
            _, fail = BookmarkVerifier(self.pdf_path).verify_txt(bm)
            if fail:
                print("警告：部分书签未通过校验，仍将继续写入")
        return self.apply_txt(bm)
