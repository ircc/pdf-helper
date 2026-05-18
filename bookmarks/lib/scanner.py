# -*- coding: utf-8 -*-
"""扫描 PDF 正文，定位篇/章标题页码。"""
import json
import re
from pathlib import Path
from typing import Any

from PyPDF2 import PdfReader


def norm(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


class TocScanner:
    """根据 TOC 配置在 PDF 中扫描各标题对应页码。"""

    def __init__(self, pdf_path: Path):
        self.pdf_path = Path(pdf_path)
        self.reader = PdfReader(self.pdf_path)

    @staticmethod
    def load_config(toc_path: Path) -> dict[str, Any]:
        with open(toc_path, encoding="utf-8") as f:
            return json.load(f)

    def find_toc_page(self) -> int:
        for i, page in enumerate(self.reader.pages):
            if i == 0:
                continue
            raw = page.extract_text() or ""
            if "目录" in raw and "第一篇" in raw and "...." in raw:
                return i + 1
        return 2

    def find_preamble_page(self) -> int:
        for i, page in enumerate(self.reader.pages):
            text = norm(page.extract_text())
            if text.startswith("1中华人民共和国") or re.search(
                r"^1[\u4e00-\u9fff]", text
            ):
                return i + 1
        return 6

    def find_title_page(self, title: str, start_idx: int) -> int:
        key = norm(title)
        if "篇" in title and "章" not in title[:4]:
            m = re.match(r"(第[一二三四五六七八九十百]+篇)", key)
            probe = m.group(1) if m else key[:12]
        else:
            m = re.match(r"(第[一二三四五六七八九十百]+章)", key)
            probe = m.group(1) if m else key[:10]

        for i in range(start_idx, len(self.reader.pages)):
            text = norm(self.reader.pages[i].extract_text() or "")
            if probe not in text:
                continue
            raw = self.reader.pages[i].extract_text() or ""
            if i < 5 and "...." in raw:
                continue
            return i
        raise ValueError(f"未在 PDF 中找到章节：{title}")

    def scan(self, config: dict[str, Any]) -> dict[str, int]:
        """返回 {标题: PDF 页码(1-based)}。"""
        pages: dict[str, int] = {}
        last_idx = 5

        if config.get("book_title"):
            pages[config["book_title"]] = 1

        for item in config.get("front_matter", []):
            title = item if isinstance(item, str) else item["title"]
            detect = (
                item.get("detect", "manual")
                if isinstance(item, dict)
                else "manual"
            )
            if detect == "toc":
                pages[title] = self.find_toc_page()
            elif detect == "preamble":
                pages[title] = self.find_preamble_page()
            elif isinstance(item, dict) and "page" in item:
                pages[title] = int(item["page"])
            else:
                pages[title] = (
                    self.find_toc_page()
                    if "目录" in title
                    else self.find_preamble_page()
                )

        for part in config.get("parts", []):
            part_title = part["title"]
            p_idx = self.find_title_page(part_title, last_idx)
            pages[part_title] = p_idx + 1
            c_start = p_idx
            for ch in part.get("chapters", []):
                c_idx = self.find_title_page(ch, c_start)
                pages[ch] = c_idx + 1
                c_start = c_idx + 1
            last_idx = p_idx + 1

        return pages

    def build_entries(
        self, config: dict[str, Any], pages: dict[str, int]
    ) -> list[tuple[str, int, int]]:
        """(标题, 页码, 层级)：0=书名，1=目录/篇，2=章。"""
        entries: list[tuple[str, int, int]] = []
        if config.get("book_title"):
            t = config["book_title"]
            entries.append((t, pages[t], 0))
        for item in config.get("front_matter", []):
            title = item if isinstance(item, str) else item["title"]
            entries.append((title, pages[title], 1))
        for part in config.get("parts", []):
            pt = part["title"]
            entries.append((pt, pages[pt], 1))
            for ch in part.get("chapters", []):
                entries.append((ch, pages[ch], 2))
        return entries
