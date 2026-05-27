# Data Formats / 数据格式

ACE-Omega supports many input formats by best-effort parsing:

- CSV / TSV
- JSON / JSONL
- XLSX / XLS
- TXT
- Markdown
- PDF
- DOCX / DOC
- BibTeX
- RIS / XML / HTML as structured text fallback

Standard fields:

```text
title
authors
year
cited_by_count
abstract
keywords
doi
module
journal
```

The parser is intentionally tolerant. If it cannot find exact column names, it tries fuzzy matching and text fallback extraction.

中文：ACE-Omega 的解析器偏向“尽量能读”，而不是遇到不标准格式就直接失败。即使字段不完整，它也会尽量生成可以可视化的论文记录。
