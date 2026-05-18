# PDF 书签工具

为 PDF 添加可跳转、嵌套、默认折叠的书签目录。

## 用法

```bash
cd pdf-helper/bookmarks
pip install -r requirements.txt

py -3 bm.py 你的文档.pdf
```

输出（与源 PDF 同目录）：

- `你的文档_bookmark.txt` — 书签数据
- `你的文档-TOC.pdf` — 带目录的 PDF

TOC 配置会自动从 `sample/toc_*.json` 匹配（如十五五规划）；新文档请复制 `sample/toc_十五五规划.json` 并修改篇、章标题。

## 可选参数

| 参数 | 说明 |
|------|------|
| `-t, --toc` | 指定 TOC 配置文件 |
| `--gen-only` | 仅生成书签 txt |
| `--apply-only` | 仅从已有 txt 写入 PDF |
| `--preview` | 预览前几页文本（排查页码） |
| `--outline` | 查看 PDF 大纲 |
| `--export` | 导出书签到 `history/` |
| `--offset N` | 页码偏移 |
| `--no-collapse` | 打开时书签默认展开 |
| `--no-verify` | 跳过校验 |

## 目录结构

```
bookmarks/
  bm.py              ← 唯一入口
  lib/
    pipeline.py      一键流程
    scanner.py       PDF 扫描
    generator.py     生成书签 txt
    verifier.py      校验 / 预览
    applier.py       写入 PDF
    config.py        路径与 TOC 匹配
  sample/toc_*.json  目录结构配置
  utils.py           PDF 读写
  add_bookmarks.py   传统方式（info.conf）
  get_bookmarks.py   导出书签
```

## 书签 txt 格式

```
书名@1
    目录@2
    第一篇 …@7
        第一章 …@7
```

每多一层子级，标题前增加 4 个空格。

## 传统方式

复制 `sample/info_sample.conf` 为 `info.conf` 后运行 `py -3 add_bookmarks.py`。
