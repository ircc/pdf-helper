# -*- coding: utf-8 -*-
"""校验书签 txt 与 PDF 大纲。"""
import re
from pathlib import Path

from PyPDF2 import PdfReader

from .scanner import norm


class BookmarkVerifier:
    def __init__(self, pdf_path: Path):
        self.pdf_path = Path(pdf_path)
        self.reader = PdfReader(self.pdf_path)

    @staticmethod
    def _parse_txt(txt_path: Path) -> list[tuple[str, int, int]]:
        entries = []
        for line in txt_path.read_text(encoding="utf-8").splitlines():
            line = line.rstrip()
            if not line or "@" not in line:
                continue
            title, page_s = line.split("@", 1)
            level = len(re.match(r"^[ ]*", title).group()) // 4
            entries.append((title.strip(), int(page_s.strip()), level))
        return entries

    def verify_txt(self, txt_path: Path) -> tuple[int, int]:
        entries = self._parse_txt(txt_path)
        ok, fail = 0, 0
        print(f"校验书签：{txt_path.name}")
        for title, page, _ in entries:
            idx = page - 1
            if idx < 0 or idx >= len(self.reader.pages):
                print(f"  [失败] 第 {page} 页越界：{title}")
                fail += 1
                continue
            text = norm(self.reader.pages[idx].extract_text())
            if "篇" in title and "章" not in title[:6]:
                m = re.match(r"(第[一二三四五六七八九十百]+篇)", norm(title))
                probe = m.group(1) if m else norm(title)[:12]
            elif "章" in title:
                m = re.match(r"(第[一二三四五六七八九十百]+章)", norm(title))
                probe = m.group(1) if m else norm(title)[:10]
            elif "说明" in title or "前言" in title:
                probe = "1中华人民共和国"
            else:
                probe = norm(title)[:8]
            if probe in text or norm(title)[:6] in text:
                ok += 1
            else:
                print(f"  [失败] 第 {page} 页未匹配「{probe}」：{title}")
                fail += 1
        print(f"  通过 {ok}/{len(entries)}")
        return ok, fail

    def preview_pages(self, max_pages: int = 15) -> None:
        n = min(max_pages, len(self.reader.pages))
        print(f"预览前 {n} 页：{self.pdf_path.name}")
        for i in range(n):
            t = (self.reader.pages[i].extract_text() or "")[:200].replace("\n", " ")
            print(f"  [{i + 1}] {t[:160]}")

    def show_outline(self) -> None:
        outline = self.reader.outline
        if not outline:
            print("未找到书签大纲")
            return
        print(f"大纲：{self.pdf_path.name}")

        def walk(items, depth=0):
            if not isinstance(items, list):
                items = [items]
            for item in items:
                if isinstance(item, list):
                    walk(item, depth)
                else:
                    page = self.reader.get_destination_page_number(item) + 1
                    print(f"{'  ' * depth}{item.title} (p{page})")
                    if item.children:
                        walk(item.children, depth + 1)

        walk(outline)
