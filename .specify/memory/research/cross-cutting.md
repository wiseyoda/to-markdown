# Research: Cross-Cutting Comparison

## Date: 2026-02-25

## Comparison: MarkItDown vs Kreuzberg vs Per-Format Libraries

### Overview

| Aspect | MarkItDown | Kreuzberg | Per-Format Libraries |
|--------|-----------|-----------|---------------------|
| **Maintainer** | Microsoft | Community (Goldziher) | Various |
| **Version** | 0.1.5 (pre-1.0) | 4.3.8 (Beta) | Varies |
| **License** | MIT | MIT | Mixed (MIT, AGPL, Apache) |
| **Formats** | ~15 | 76+ | 6 (our targets) |
| **Architecture** | Python converters | Rust core + Python FFI | Individual Python libs |
| **Speed** | Slow on complex docs | 35+ files/sec | Varies |
| **Install size** | 251MB, 25 deps | 71MB, 20 deps | Varies per format |

### Feature Comparison

| Feature | MarkItDown | Kreuzberg | Per-Format |
|---------|-----------|-----------|------------|
| PDF quality | Poor tables, no OCR | 91% F1, 3 OCR backends | pymupdf4llm: excellent |
| DOCX quality | Decent (mammoth->HTML->MD) | Good (Rust parser) | python-docx: excellent |
| PPTX quality | Good (speaker notes) | Good | python-pptx: good |
| XLSX quality | Good (pandas) | Good (calamine) | openpyxl: excellent |
| HTML quality | Good (markdownify) | Good (Rust html-to-md) | markdownify/html-to-md |
| OCR | Azure only (paid cloud) | 3 offline backends | pytesseract |
| YAML frontmatter | No | No (metadata as object) | N/A (we'd build this) |
| CLI | Basic (stdout) | Full CLI + MCP server | N/A (we'd build this) |
| LLM features | Python API only, OpenAI | None | N/A (we'd build this) |
| Plugin system | Yes (entry points) | Yes (backends, processors) | Our own registry |

### Decision Matrix

| Criterion | Weight | MarkItDown | Kreuzberg | Per-Format |
|-----------|--------|-----------|-----------|------------|
| Format coverage | High | 7/10 | 10/10 | 6/10 |
| Output quality | High | 5/10 | 8/10 | 9/10 |
| Development effort | High | Medium (still need wrapper) | Low (thin wrapper) | Very High |
| Maintenance burden | Medium | Low (Microsoft) | Low (active community) | High (6 libs) |
| API stability | Medium | Pre-1.0 risk | Beta risk | Stable (mature libs) |
| Performance | Low | Poor | Excellent | Varies |
| Independence | Low | Dependent on Microsoft | Dependent on maintainer | Full control |

### Scores

- **MarkItDown**: 5.8/10 - Good format coverage but poor output quality, especially PDF tables.
  No offline OCR. Pre-1.0 stability concerns.
- **Kreuzberg**: 8.2/10 - Best balance of quality, coverage, and effort. Rust core provides
  excellent performance. 91% F1 on PDFs. 76+ formats. Risk is Beta status.
- **Per-Format**: 7.5/10 - Best output quality potential but highest development effort.
  6+ phases of parser development. Most maintenance burden.

## Recommendation

**Kreuzberg** as extraction backend with thin CLI wrapper.

### Rationale

1. **Effort**: Eliminates 6 per-format converter phases. ~500-800 lines of wrapper vs thousands
   of parser code.
2. **Quality**: 91% F1 on PDFs is near-parity with per-format approach. Good quality across
   all formats.
3. **Coverage**: 76+ formats vs our planned 6. Users get bonus format support for free.
4. **Performance**: Rust core means 35+ files/sec. Faster than any pure Python approach.
5. **Our value-add**: Focus on what makes to-markdown unique - YAML frontmatter, LLM features,
   golden file testing, magic defaults CLI.

### Mitigation for Kreuzberg Beta Risk

1. Pin to specific version (4.3.8+)
2. Isolate behind adapter interface (`core/extraction.py`)
3. If Kreuzberg breaks, adapter can be reimplemented with per-format libs
4. MIT license allows forking if project is abandoned

## Human Decision

- **Confirmed**: 2026-02-25
- **Decision**: Wrap Kreuzberg (over MarkItDown, over building from scratch)
- **User notes**: "both of these look like they do exactly what I wanted... Investigate both
  FIRST, because it might mean we just pivot from this project all together"
- **Outcome**: Kreuzberg adopted as backend. Project pivots to thin wrapper architecture.

## Sources

- [MarkItDown on PyPI](https://pypi.org/project/markitdown/)
- [MarkItDown GitHub](https://github.com/microsoft/markitdown) (87.5k stars)
- [Kreuzberg on PyPI](https://pypi.org/project/kreuzberg/)
- [Kreuzberg GitHub](https://github.com/Goldziher/kreuzberg)
- [Kreuzberg docs](https://docs.kreuzberg.dev/)
- [Benchmark comparison](https://dev.to/nhirschfeld/i-benchmarked-4-python-text-extraction-libraries-2025-4e7j)
