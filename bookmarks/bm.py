# -*- coding: utf-8 -*-
"""
PDF 书签工具 — 入口

  py -3 bm.py 文档.pdf

自动完成：扫描正文 → 生成书签 → 写入带目录的 PDF（输出 <原名>-TOC.pdf）
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bm",
        description="为 PDF 添加可跳转的书签目录（传入 PDF 即可）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  py -3 bm.py 十五五规划.pdf
  py -3 bm.py 十五五规划.pdf --toc sample/toc_十五五规划.json
  py -3 bm.py 十五五规划.pdf --gen-only          仅生成书签 txt
  py -3 bm.py 十五五规划-TOC.pdf --export        导出已有书签
        """,
    )
    parser.add_argument("pdf", type=Path, help="PDF 文件路径")
    parser.add_argument("-t", "--toc", type=Path, help="TOC 配置（默认自动匹配 sample/toc_*.json）")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--gen-only", action="store_true", help="仅生成书签 txt")
    mode.add_argument("--apply-only", action="store_true", help="仅从已有书签 txt 写入 PDF")
    mode.add_argument("--export", action="store_true", help="导出 PDF 中的书签")
    mode.add_argument("--preview", action="store_true", help="预览 PDF 前几页文本")
    mode.add_argument("--outline", action="store_true", help="查看 PDF 大纲结构")

    parser.add_argument("--offset", type=int, default=0, help="页码偏移")
    parser.add_argument("--no-collapse", action="store_true", help="书签默认展开")
    parser.add_argument("--no-verify", action="store_true", help="跳过校验")
    parser.add_argument("--no-history", action="store_true", help="不备份到 history/")

    args = parser.parse_args(argv)
    pdf = args.pdf.resolve()

    if not pdf.exists():
        print(f"错误：文件不存在 {pdf}", file=sys.stderr)
        return 1

    from lib.config import bookmark_txt_path
    from lib.pipeline import BookmarkPipeline
    from lib.verifier import BookmarkVerifier

    pipe = BookmarkPipeline(
        pdf,
        args.toc,
        page_offset=args.offset,
        collapse=not args.no_collapse,
        verify=not args.no_verify,
        save_history=not args.no_history,
    )

    try:
        if args.export:
            cmd = [sys.executable, str(ROOT / "get_bookmarks.py"), str(pdf), "-q"]
            return subprocess.call(cmd, cwd=ROOT)
        if args.preview:
            BookmarkVerifier(pdf).preview_pages()
            return 0
        if args.outline:
            BookmarkVerifier(pdf).show_outline()
            return 0
        if args.gen_only:
            pipe.generate_txt()
            return 0
        if args.apply_only:
            bm = bookmark_txt_path(pdf)
            if not bm.exists():
                print(f"错误：未找到书签文件 {bm}", file=sys.stderr)
                return 1
            pipe.apply_txt(bm)
            return 0
        pipe.run()
        return 0
    except FileNotFoundError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
