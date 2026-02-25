# Research: Kreuzberg (Extraction Backend)

## Date: 2026-02-25

## Overview

Kreuzberg is a document extraction library with a Rust core and Python bindings. It handles
76+ file formats including all 6 target formats for to-markdown. Adopted as the extraction
backend, replacing the per-format parser approach.

- **Latest version**: 4.3.8 (released Feb 21, 2026)
- **License**: MIT
- **Python support**: 3.10-3.14 (confirmed 3.14 compatible)
- **Install size**: 71MB, 20 dependencies
- **Performance**: 35+ files/second, Rust core via Maturin/pyo3

## Format Coverage

| Format | Support | Quality Notes |
|--------|---------|--------------|
| PDF | Full | 91% F1 Markdown quality. Font-size heading classification. 10-stage table filtering. |
| DOCX | Full | Bold/italic/underline/strikethrough/hyperlinks rendered as Markdown. Tables supported. |
| PPTX | Full | Slides, speaker notes, images, metadata. Also .pptm, .ppsx. |
| XLSX | Full | Sheet data, formulas, charts. Also .xlsm, .xlsb, .xls, .ods. |
| HTML | Full | DOM parsing, Open Graph/Twitter Card metadata, link extraction. |
| Images/OCR | Full | 3 OCR backends: Tesseract, PaddleOCR, EasyOCR. Preprocessing (contrast, deskew). |
| + 70 more | Full | Email, archives, academic, eBooks, web/data, markup formats. |

## Architecture

### Rust Core Components

| Crate | Purpose |
|-------|---------|
| `kreuzberg` | PDF (pdfium-render), Excel (calamine), XML, archives, Markdown (pulldown-cmark), HTML-to-MD (html-to-markdown-rs), language detection, text chunking, image processing |
| `kreuzberg-tesseract` | Tesseract OCR bindings |
| `kreuzberg-paddle-ocr` | PaddleOCR via ONNX Runtime |
| `kreuzberg-py` | Python FFI bindings |
| `kreuzberg-cli` | CLI binary (axum server, MCP support) |

### Python API

```python
from kreuzberg import extract_file_sync, ExtractionConfig

result = extract_file_sync("document.pdf", config=ExtractionConfig(
    output_format="markdown",
    enable_quality_processing=True,
))
print(result.content)    # Markdown text
print(result.metadata)   # Metadata object (title, authors, dates, page count, etc.)
print(result.tables)     # List[ExtractedTable]
```

### Key API Features

- Sync and async extraction (`extract_file` / `extract_file_sync`)
- Batch processing (`batch_extract_files_sync`)
- Bytes extraction (`extract_bytes_sync`)
- Multiple output formats: plain, markdown, djot, html
- OCR configuration with backend selection and language
- Image extraction (`ImageExtractionConfig`)
- Plugin system: register OCR backends, post-processors, validators, extractors

## Gaps vs to-markdown Requirements

| Requirement | Kreuzberg | Our Wrapper Adds |
|-------------|-----------|------------------|
| YAML frontmatter | Metadata as structured object | Compose from result.metadata |
| Default Markdown output | Default is plain text | Set output_format="markdown" |
| --summary flag | Not available | Gemini 2.5 Flash integration |
| --images flag | Not available | Gemini vision integration |
| --force overwrite | Not in CLI | Typer CLI with --force |
| Magic defaults (zero flags) | Requires --output-format | Default to markdown |
| Golden file testing | Has F1 benchmarks | syrupy snapshot tests |
| Single .md output file | Content + metadata separate | Assemble frontmatter + content |

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Beta status (v4.x, rapid evolution) | Medium | Pin version, isolate behind adapter interface |
| API breaking changes | Medium | Thin adapter layer in core/extraction.py |
| Kreuzberg abandoned | Low | Fork possible (MIT), or fall back to per-format libs |
| Quality insufficient for specific format | Low | Can add format-specific post-processing |

## Human Decision

- **Confirmed**: 2026-02-25
- **Decision**: Adopt Kreuzberg as extraction backend
- **Rationale**: Handles all formats at production quality, eliminates 6 per-format phases,
  allows focus on LLM-optimized wrapper (frontmatter, smart features, quality testing)
- **Architecture**: Thin CLI wrapper around Kreuzberg, not per-format parsers

## Sources

- [Kreuzberg on PyPI](https://pypi.org/project/kreuzberg/)
- [Kreuzberg GitHub](https://github.com/Goldziher/kreuzberg)
- [Kreuzberg docs](https://docs.kreuzberg.dev/)
- [Kreuzberg v4.3.0 benchmarks](https://dev.to/t_ivanova/kreuzberg-v430-and-benchmarks-500b)
- [Python text extraction benchmark](https://dev.to/nhirschfeld/i-benchmarked-4-python-text-extraction-libraries-2025-4e7j)
